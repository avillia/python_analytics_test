from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)

session_local = sessionmaker(bind=engine)


def create_session() -> Session:
    return session_local()
