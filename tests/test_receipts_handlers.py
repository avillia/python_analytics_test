from assertpy import assert_that
from pytest import raises

from src.core.db.managers import DBAppConfigManager, ReceiptCacheManager
from src.core.handlers.receipts.get import (
    render_as_str_receipt_with,
    retrieve_if_is_possible_to_look_data_for,
)
from tests.conftest import receipt, user


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
    receipt_data = retrieve_if_is_possible_to_look_data_for(receipt, using=user)
    assert_that(receipt_data["id"]).is_equal_to(receipt)


def test_retrieve_if_is_possible_to_look_data_for_wrong_user(receipt, another_user):
    with raises(AssertionError) as exc:
        retrieve_if_is_possible_to_look_data_for(receipt, using="non_existing_user_id")
    assert_that(str(exc.value)).contains("Not possible to access this data.")


def test_retrieve_if_is_possible_to_look_data_for_not_found(user):
    with raises(KeyError) as exc:
        retrieve_if_is_possible_to_look_data_for("nonexistent_id", using=user)
    assert_that(str(exc.value)).contains("is not found!")
