from fastapi.testclient import TestClient
from pytest import fixture

from main import app
from src.core.db.base import Base
from src.core.db.base import engine as test_engine


@fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@fixture(scope="session")
def test_client():
    with TestClient(app) as c:
        yield c
