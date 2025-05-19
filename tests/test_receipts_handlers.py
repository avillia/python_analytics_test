from assertpy import assert_that
from pytest import fixture, raises

from src.core.db.managers import (
    DBAppConfigManager,
    ReceiptCacheManager,
    ReceiptManager,
    UserManager,
)
from src.core.handlers.receipts.get import (
    render_as_str_receipt_with,
    retrieve_if_is_possible_to_look_data_for,
)
from src.core.utils import generate_alphanumerical_id


@fixture(scope="function")
def setup_receipt_render_config():
    DBAppConfigManager().create_a_lot_of_new(
        {
            "delimiter": ("=", str),
            "separator": ("-", str),
            "thank_you_note": ("Дякуємо за покупку!", str),
            "rest_label": ("Решта", str),
            "cash_label": ("Готівка", str),
            "cashless_label": ("Картка", str),
            "total_label": ("СУМА", str),
            "timeout": (60, int),
            "flag_enabled": (True, bool),
            "datetime_format": ("%d.%m.%Y %H:%M", str),
        }
    )
    yield


@fixture(scope="function")
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


@fixture(scope="function")
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


@fixture(scope="function")
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


def test_render_as_str_receipt_with_success(receipt, setup_receipt_render_config):
    rendered_receipt = render_as_str_receipt_with(receipt, width=32)
    assert_that(rendered_receipt).is_instance_of(str)
    assert_that(rendered_receipt).contains("Test Product")
    assert_that(rendered_receipt).contains("1 000.00")


def test_render_as_str_receipt_with_caching(receipt):
    width = 32
    cache_manager = ReceiptCacheManager()
    formatting_config = DBAppConfigManager().fetch_receipt_formatting_configs()
    formatting_config["width"] = str(width)
    config_string = ":".join(formatting_config.values())

    cached_txt = cache_manager.fetch_cache_for(receipt, config_string)
    if cached_txt:
        cache_manager.delete(receipt)

    rendered_first = render_as_str_receipt_with(receipt, width=width)
    cached_txt_after_first = cache_manager.fetch_cache_for(receipt, config_string)
    assert_that(cached_txt_after_first).is_equal_to(rendered_first)

    rendered_second = render_as_str_receipt_with(receipt, width=width)
    assert_that(rendered_second).is_equal_to(rendered_first)


def test_render_as_str_receipt_with_nonexistent_receipt():
    with raises(KeyError) as exc:
        render_as_str_receipt_with("nonexistent_id", width=32)
    assert_that(str(exc.value)).contains("is not found in DB!")


def test_retrieve_if_is_possible_to_look_data_for_success(receipt, user):
    receipt_obj = retrieve_if_is_possible_to_look_data_for(receipt, using=user)
    assert_that(receipt_obj.id).is_equal_to(receipt)
    assert_that(receipt_obj.user_id).is_equal_to(user)


def test_retrieve_if_is_possible_to_look_data_for_wrong_user(receipt, another_user):
    with raises(AssertionError) as exc:
        retrieve_if_is_possible_to_look_data_for(receipt, using="non_existing_user_id")
    assert_that(str(exc.value)).contains("Not possible to access this data.")


def test_retrieve_if_is_possible_to_look_data_for_not_found(user):
    with raises(KeyError) as exc:
        retrieve_if_is_possible_to_look_data_for("nonexistent_id", using=user)
    assert_that(str(exc.value)).contains("is not found!")
