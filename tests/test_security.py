from assertpy import assert_that
from pytest import mark

from src.api.security import is_possible_to_perform_request_based_on


@mark.parametrize(
    "method, route, payload",
    (
        (
            "GET",
            "receipts",
            {"access": ["*@*"]},
        ),
        (
            "POST",
            "products",
            {"access": ["*@products"]},
        ),
        (
            "GET",
            "receipts",
            {"access": ["GET@*", "POST@receipts"]},
        ),
        (
            "POST",
            "receipts",
            {"access": ["POST@receipts", "GET@receipts"]},
        ),
        (
            "PATCH",
            "products",
            {"access": ["PATCH@products", "GET@receipts", "POST@products"]},
        ),
        (
            "DELETE",
            "users",
            {"access": ["DELETE@users", "GET@users"]},
        ),
    ),
)
def test_should_be_possible_to_perform_request(method: str, route: str, payload: dict):
    assert_that(
        is_possible_to_perform_request_based_on(method, route, payload)
    ).is_true()
    assert_that(payload).does_not_contain("access")


@mark.parametrize(
    "method, route, payload",
    (
        ("GET", "receipts", {"access": []}),
        ("GET", "receipts", {"access": ["POST@receipts"]}),
        ("POST", "products", {"access": ["GET@products"]}),
        ("PATCH", "receipts", {"access": ["*@products"]}),
        ("DELETE", "users", {"access": ["*@receipts", "GET@*"]}),
        (
            "GET",
            "receipts",
            {
                "access": [
                    "POST@invoices",
                    "DELETE@users",
                    "PATCH@orders",
                    "PUT@products",
                ]
            },
        ),
        (
            "GET",
            "receipts",
            {"access": ["*@products", "*@invoices", "GET@orders", "POST@receipts"]},
        ),
        (
            "POST",
            "products",
            {
                "access": [
                    "GET@products",
                    "PATCH@products",
                    "DELETE@products",
                    "PUT@orders",
                ]
            },
        ),
        (
            "PATCH",
            "orders",
            {"access": ["GET@*", "POST@orders", "DELETE@orders", "PUT@invoices"]},
        ),
        (
            "GET",
            "dashboard",
            {
                "access": [
                    "GET@home",
                    "POST@dashboard",
                    "PATCH@dashboard",
                    "DELETE@dashboard",
                ]
            },
        ),
        (
            "PUT",
            "reports",
            {"access": ["DELETE@reports", "GET@invoices", "POST@orders"]},
        ),
    ),
)
def test_request_lacks_required_accesses(method: str, route: str, payload: dict):
    assert_that(
        is_possible_to_perform_request_based_on(method, route, payload)
    ).is_false()
    assert_that(payload).does_not_contain("access")
