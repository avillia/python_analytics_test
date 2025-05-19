from __future__ import annotations

from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

session_local = sessionmaker(bind=engine, expire_on_commit=False)


def create_session() -> Session:
    return session_local()


class FormattedDecimal(Decimal):
    def __str__(self):
        return f"{self:,.2f}".replace(",", " ")


from sqlalchemy.types import TypeDecorator, DECIMAL


class FormattedDecimalType(TypeDecorator):
    impl = DECIMAL(precision=10, scale=2)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """stores value as decimal when saving TO db"""
        if value is None:
            return None
        return Decimal(value)

    def process_result_value(self, value, dialect):
        """converts from underlying DECIMAL -> FormattedDecimal when loading FROM db"""
        if value is None:
            return None
        return FormattedDecimal(value)


class Base(DeclarativeBase):
    pass
