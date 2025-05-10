from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db.base import create_session
from src.core.db.models import Base, Product, Tag


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
