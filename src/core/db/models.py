from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DATETIME, DECIMAL, Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.core.utils import generate_alphanumerical_id


class FormattedDecimal(Decimal):
    def __str__(self):
        return f"{self:,.2f}".replace(",", " ")


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(
        Float,
    )

    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary="products_tags",
        back_populates="products",
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    name: Mapped[str] = mapped_column(String)
    value: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    products: Mapped[list[Product]] = relationship(
        "Product",
        secondary="products_tags",
        back_populates="tags",
    )


class ProductsTags(Base):
    __tablename__ = "products_tags"

    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), primary_key=True)
    tag_name: Mapped[str] = mapped_column(ForeignKey("tags.name"), primary_key=True)


class AppConfig(Base):
    __tablename__ = "apps_configs"

    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    value: Mapped[str] = mapped_column(String(128), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("str", "float", "int", "bool"), nullable=False
    )

    def __repr__(self):
        return f"<Config({self.key}: {self.type} ={self.value}"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="users_roles",
        back_populates="users",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"<User(login={self.login!r}, email={self.email!r})>"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[list[User]] = relationship(
        "User",
        secondary="users_roles",
        back_populates="roles",
    )
    accesses: Mapped[list[Access]] = relationship(
        "Access",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Role(name={self.name!r})>"


class UsersRoles(Base):
    __tablename__ = "users_roles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Access(Base):
    __tablename__ = "accesses"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    route_url: Mapped[str] = mapped_column(String(200))
    allowed_method: Mapped[str] = mapped_column(
        Enum("GET", "POST", "PUT", "PATCH", "DELETE", "*")
    )

    role: Mapped[Role] = relationship("Role", back_populates="accesses")

    def __repr__(self):
        return (
            f"<Access(role={self.role.name!r}, "
            f"'{self.allowed_method}@{self.route_url}')>"
        )


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_cashless_payment: Mapped[bool] = mapped_column(Boolean, nullable=False)
    payment_amount: Mapped[FormattedDecimal] = mapped_column(DECIMAL(2))

    creation_date: Mapped[datetime] = mapped_column(
        DATETIME, default=datetime.now
    )

    items: Mapped[list[ReceiptItems]] = relationship(
        "ReceiptItems",
        back_populates="receipt",
        cascade="all, delete-orphan",
    )

    @property
    def total(self) -> FormattedDecimal:
        return FormattedDecimal(sum(item.total for item in self.items))

    @property
    def rest(self) -> FormattedDecimal:
        if self.is_cashless_payment:
            return FormattedDecimal(0)
        return self.payment_amount - self.total


class ReceiptItems(Base):
    __tablename__ = "receipt_items"

    id: Mapped[str] = mapped_column(
        primary_key=True,
        default=generate_alphanumerical_id,
    )
    receipt_id: Mapped[str] = mapped_column(
        ForeignKey("receipts.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[FormattedDecimal] = mapped_column(DECIMAL(2))
    quantity: Mapped[FormattedDecimal] = mapped_column(DECIMAL(2))

    receipt: Mapped[Receipt] = relationship(
        "Receipt",
        back_populates="items",
    )

    @property
    def total(self) -> FormattedDecimal:
        return self.price * self.quantity
