from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.db.models import Base, Product, Tag


class BaseManager:
    model: type[Base]

    def __init__(self, session: Session):
        self.session = session

    def fetch_specific_by(self, entity_id: str) -> Base | None:
        return self.session.scalar(select(self.model).where(self.model.id == entity_id))

    def fetch_all(self) -> list[Base]:
        return self.session.scalars(select(self.model)).all()


class TagManager(BaseManager):
    model = Tag

    def ensure_all_are_present(
        self,
        tag_names: list[str],
        *,
        is_using_existing_session: bool = False,
    ) -> list[Tag]:
        unique_names = set(tag_names)

        existing_tags: list[Tag] = self.session.scalars(
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
                if is_using_existing_session
                else self.session.commit
            )
            update_method()

        return existing_tags + new_tags


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
        tags = TagManager(self.session).ensure_all_are_present(tag_names, is_using_existing_session=True)

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
        product = self.fetch_specific_by(product_id)
        if not product:
            return None

        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price

        if tag_names is not None:
            product.tags = TagManager(self.session).ensure_all_are_present(tag_names, is_using_existing_session=True)

        self.session.commit()
        return product

    def delete(self, product_id: str) -> bool:
        prod = self.fetch_specific_by(product_id)
        if not prod:
            return False
        self.session.delete(prod)
        self.session.commit()
        return True
