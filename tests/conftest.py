from _pytest.fixtures import fixture
from fastapi.testclient import TestClient
from pytest import fixture

from main import app
from src.core.db.base import Base
from src.core.db.base import engine as test_engine
from src.core.db.managers import ReceiptManager, UserManager
from src.core.utils import generate_alphanumerical_id


@fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@fixture(scope="session")
def test_client():
    with TestClient(app) as c:
        yield c


@fixture(scope="package")
def user():
    user_id = generate_alphanumerical_id()
    UserManager().create_new_user_using(
        new_user_id=user_id,
        login="test_user",
        name="Illia Avdiienko",
        email="test@example.com",
        password_hash="hash",
    )
    yield user_id

    UserManager().delete(user_id)


@fixture(scope="package")
def another_user():
    user_id = generate_alphanumerical_id()
    UserManager().create_new_user_using(
        new_user_id=user_id,
        login="another_user",
        name="Danylo Avdiienko",
        email="another@example.com",
        password_hash="hash",
    )
    yield user_id

    UserManager().delete(user_id)


@fixture(scope="package")
def receipt(user):
    receipt = ReceiptManager().create_receipt(
        user_id=user,
        items=[
            {
                "name": "Test Product",
                "price": "500.00",
                "quantity": "2.00",
                "total": "1000.00",
            }
        ],
        is_cashless_payment=True,
        payment_amount="1000.00",
    )
    yield receipt.id

    ReceiptManager().delete(receipt.id)
