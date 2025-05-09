from __future__ import annotations


from sqlalchemy import (
    String,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id:          Mapped[str]        = mapped_column(primary_key=True)
    name:        Mapped[str]        = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price:       Mapped[float]      = mapped_column(Float, nullable=False)

    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary="products_tags",
        back_populates="products",
    )


class Tag(Base):
    __tablename__ = "tags"

    name:  Mapped[str]        = mapped_column(primary_key=True)
    value: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    products: Mapped[list[Product]] = relationship(
        "Product",
        secondary="products_tags",
        back_populates="tags",
    )


class ProductsTags(Base):
    __tablename__ = "products_tags"

    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"),
        primary_key=True,
    )
    tag_name: Mapped[str] = mapped_column(
        ForeignKey("tags.name"),
        primary_key=True,
    )
