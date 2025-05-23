from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, update, insert
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.functions import count, func

from src.core.db.base import Base, create_session
from src.core.db.models import (
    Access,
    AppConfig,
    Product,
    Receipt,
    ReceiptItems,
    Role,
    Tag,
    TxtReceiptCache,
    User,
    UsersRoles,
)
from src.core.utils import generate_alphanumerical_id


class BaseManager:
    model: type[Base]

    def __init__(self, session: Session | None = None):
        self._is_using_existing_session: bool = session is not None
        self.session: Session = session if session else create_session()

    def fetch_specific_by(self, entity_id: str) -> Base | None:
        return self.session.scalar(select(self.model).where(self.model.id == entity_id))

    def fetch_all(self) -> list[Base]:
        return self.session.scalars(select(self.model)).all()

    def delete(self, entity_id: str) -> bool:
        entity = self.fetch_specific_by(entity_id)
        if not entity:
            return False
        self.session.delete(entity)
        self.session.commit()
        return True


class TagManager(BaseManager):
    model = Tag

    def ensure_all_are_present(self, tag_names: list[str]) -> list[Tag]:
        unique_names = set(tag_names)

        existing_tags = self.session.scalars(
            select(Tag).where(
                Tag.name.in_(unique_names),
            )
        ).all()
        existing_names = {t.name for t in existing_tags}

        missing = unique_names - existing_names

        new_tags = [Tag(name=name) for name in missing]
        if new_tags:
            self.session.add_all(new_tags)
            update_method = (
                self.session.flush
                if self._is_using_existing_session
                else self.session.commit
            )
            update_method()

        return list(existing_tags) + new_tags


class ProductManager(BaseManager):
    model = Product

    def create(
        self,
        entity_id: str,
        name: str,
        description: str | None,
        price: float,
        tag_names: list[str] | None,
    ) -> Product:
        tags = TagManager(self.session).ensure_all_are_present(tag_names)

        prod = Product(
            id=entity_id,
            name=name,
            description=description,
            price=price,
            tags=tags,
        )
        self.session.add(prod)
        self.session.commit()
        return prod

    def update(
        self,
        product_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        price: float | None = None,
        tag_names: list[str] | None = None,
    ) -> Product | None:
        product: Product = self.fetch_specific_by(product_id)
        if not product:
            return None

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price

        if tag_names is not None:
            product.tags = TagManager(self.session).ensure_all_are_present(tag_names)

        self.session.commit()
        return product


class DBAppConfigManager(BaseManager):
    model = AppConfig
    TYPE_MAPPING = {
        "str": str,
        "int": int,
        "bool": bool,
        "float": float,
    }

    def __getitem__(self, config: str) -> str | bool | int:
        raw_config_from_db = self.session.scalar(
            select(self.model).where(AppConfig.key == config)
        )
        if raw_config_from_db is None:
            raise LookupError(f"No {config=} found!")
        return self.TYPE_MAPPING[raw_config_from_db.type](raw_config_from_db.value)

    def __setitem__(self, key: str, value: str | bool | int):
        value_type = type(value).__name__
        value = str(value)

        update_statement = (
            update(AppConfig)
            .where(AppConfig.key == key)
            .values(
                value=value,
                type=value_type,
            )
        )
        result = self.session.execute(update_statement)

        no_config_found_in_db = result.rowcount == 0

        if no_config_found_in_db:
            stmt_ins = insert(AppConfig).values(
                key=key,
                value=value,
                type=value_type,
            )
            self.session.execute(stmt_ins)

        self.session.commit()

    def fetch_named_configs(
        self, keys: list[str]
    ) -> dict[str, str | int | bool | float]:
        rows = self.session.scalars(
            select(AppConfig).where(AppConfig.key.in_(keys))
        ).all()

        return {cfg.key: self.TYPE_MAPPING[cfg.type](cfg.value) for cfg in rows}

    def fetch_receipt_formatting_configs(self) -> dict[str, str]:
        receipt_keys = [
            "delimiter",
            "separator",
            "thank_you_note",
            "cash_label",
            "cashless_label",
            "total_label",
            "rest_label",
            "datetime_format",
        ]
        return self.fetch_named_configs(receipt_keys)


class UserManager(BaseManager):
    model = User

    def lookup_for_user_by(self, login: str) -> User | None:
        return self.session.scalar(select(self.model).where(User.login == login))

    def gather_all_accesses_for(self, user_id: str) -> list[Access]:
        stmt = (
            select(Access).join(Access.role).join(Role.users).where(User.id == user_id)
        )
        return self.session.scalars(stmt).all()

    def fetch_total_user_count(self) -> int:
        total = self.session.scalar(select(count()).select_from(User))
        return int(total)

    def create_new_user_using(
        self,
        new_user_id: str,
        login: str,
        name: str,
        email: str,
        password_hash: str,
    ) -> User:
        user = User(
            id=new_user_id,
            login=login,
            name=name,
            email=email,
            password_hash=password_hash,
        )
        self.session.add(user)
        self.session.commit()
        return user


class RoleManager(BaseManager):
    model = Role

    def ensure_role_exists(self, role_name: str) -> str:
        stmt = select(Role).where(Role.name == role_name)
        role = self.session.scalar(stmt)
        if role:
            return role.id

        new_id = generate_alphanumerical_id()
        role = Role(id=new_id, name=role_name)
        self.session.add(role)
        self.session.commit()
        return new_id

    def assign(self, new_user_id: str, admin_role_id: str) -> bool:
        exists_stmt = select(UsersRoles).where(
            UsersRoles.user_id == new_user_id, UsersRoles.role_id == admin_role_id
        )
        existing = self.session.scalar(exists_stmt)
        if existing:
            return False

        link = UsersRoles(user_id=new_user_id, role_id=admin_role_id)
        self.session.add(link)
        self.session.commit()
        return True

    def lookup_for_role_by(self, role_name) -> Role:
        return self.session.scalar(
            select(self.model).where(self.model.name == role_name)
        )


class AccessManager(BaseManager):
    model = Access

    def grant_unlimited_access_to(self, admin_role_id: str) -> str:
        new_id = generate_alphanumerical_id()
        access = Access(
            id=new_id,
            role_id=admin_role_id,
            allowed_method="*",
            route_url="*",
        )
        self.session.add(access)
        self.session.commit()
        return new_id

    def grant(self, role_id: str, *, permission_to_perform: str, at: str) -> str:
        new_id = generate_alphanumerical_id()
        access = Access(
            id=new_id,
            role_id=role_id,
            allowed_method=permission_to_perform,
            route_url=at,
        )
        self.session.add(access)
        self.session.commit()
        return new_id


class ReceiptManager(BaseManager):
    model = Receipt

    def filter_and_paginate_using(
        self,
        user_id: str,
        limit: int,
        offset: int,
        filters: dict,
    ) -> tuple[int, list[Receipt]]:
        query = (
            select(Receipt)
            .options(joinedload(Receipt.items))
            .where(Receipt.user_id == user_id)
        )

        if created_after := filters.get("created_after"):
            query = query.where(Receipt.creation_date >= created_after)
        if created_before := filters.get("created_before"):
            query = query.where(Receipt.creation_date <= created_before)
        if payment_type := filters.get("payment_type"):
            query = query.where(Receipt.is_cashless_payment == payment_type)

        min_total = filters.get("min_total")
        max_total = filters.get("max_total")

        if min_total is not None or max_total is not None:
            query = query.join(Receipt.items).group_by(Receipt.id)
            total_expr = func.sum(ReceiptItems.price * ReceiptItems.quantity)
            if min_total is not None:
                query = query.having(total_expr >= min_total)
            if max_total is not None:
                query = query.having(total_expr <= max_total)

        query = query.order_by(Receipt.creation_date.desc())

        all_receipts: list[Receipt] = self.session.scalars(query).unique().all()

        paginated = all_receipts[offset : offset + limit]

        return len(all_receipts), paginated

    def fetch_including_items_for(self, receipt_id: str) -> Receipt:
        query = (
            select(Receipt)
            .options(joinedload(Receipt.items))
            .where(Receipt.id == receipt_id)
        )
        return self.session.scalar(query)

    def create_receipt(
        self,
        user_id: str,
        items: list[dict],
        is_cashless_payment: bool,
        payment_amount: Decimal,
    ) -> Receipt:
        receipt = Receipt(
            user_id=user_id,
            is_cashless_payment=is_cashless_payment,
            payment_amount=payment_amount,
        )
        self.session.add(receipt)
        self.session.flush()

        for item in items:
            receipt_item = ReceiptItems(
                receipt_id=receipt.id,
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
            )
            self.session.add(receipt_item)

        self.session.commit()
        fetch_receipt_with_items_included = (
            select(Receipt)
            .options(joinedload(Receipt.items))
            .where(Receipt.id == receipt.id)
        )
        return self.session.scalar(fetch_receipt_with_items_included)

    def fetch_all_for_user_with(self, user_id: str) -> list[Receipt]:
        return self.session.scalars(
            select(Receipt).where(Receipt.user_id == user_id)
        ).all()


class ReceiptCacheManager(BaseManager):
    model = TxtReceiptCache

    def fetch_cache_for(self, receipt_id: str, config_str: str) -> str | None:
        cache_row = self.session.scalar(
            select(self.model).where(
                self.model.receipt_id == receipt_id, self.model.config_str == config_str
            )
        )
        return cache_row.txt if cache_row else None

    def create_new_entry_with(self, receipt_id: str, config_str: str, txt: str) -> None:
        total = self.session.scalar(select(func.count()).select_from(self.model))

        if total >= 10:
            oldest = self.session.scalars(
                select(self.model).order_by(self.model.creation_date.asc())
            ).first()
            self.session.delete(oldest)

        new_cache_entry = TxtReceiptCache(
            receipt_id=receipt_id,
            config_str=config_str,
            txt=txt,
        )
        self.session.add(new_cache_entry)
        self.session.commit()

    def delete(self, receipt_id: str) -> bool:
        receipt_cache = self.session.scalar(select(TxtReceiptCache).where(TxtReceiptCache.receipt_id == receipt_id))
        if not receipt_cache:
            return False
        self.session.delete(receipt_cache)
        self.session.commit()
        return True

