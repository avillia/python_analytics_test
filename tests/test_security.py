from assertpy import assert_that
from pytest import mark

from src.api.security import is_possible_to_perform_request_based_on


@mark.parametrize(
    "method, route, accesses",
    (
        ("GET", "receipts", {"*@*"}),
        ("POST", "products", {"*@products"}),
        ("GET", "receipts", {"GET@*", "POST@receipts"}),
        ("POST", "receipts", {"POST@receipts", "GET@receipts"}),
        ("PATCH", "products", {"PATCH@products", "GET@receipts", "POST@products"}),
        ("DELETE", "users", {"DELETE@users", "GET@users"}),
    ),
)
def test_request_is_possible(method: str, route: str, accesses: set[str]):
    assert_that(
        is_possible_to_perform_request_based_on(method, route, accesses)
    ).is_true()


@mark.parametrize(
    "method, route, accesses",
    (
        ("GET", "receipts", set()),
        ("GET", "receipts", {"POST@receipts"}),
        ("POST", "products", {"GET@products"}),
        ("PATCH", "receipts", {"*@products"}),
        ("DELETE", "users", {"*@receipts", "GET@*"}),
        (
            "GET",
            "receipts",
            {
                "POST@invoices",
                "DELETE@users",
                "PATCH@orders",
                "PUT@products",
            },
        ),
        (
            "GET",
            "receipts",
            {"*@products", "*@invoices", "GET@orders", "POST@receipts"},
        ),
        (
            "POST",
            "products",
            {
                "GET@products",
                "PATCH@products",
                "DELETE@products",
                "PUT@orders",
            },
        ),
        (
            "PATCH",
            "orders",
            {"GET@*", "POST@orders", "DELETE@orders", "PUT@invoices"},
        ),
        (
            "GET",
            "dashboard",
            {
                "GET@home",
                "POST@dashboard",
                "PATCH@dashboard",
                "DELETE@dashboard",
            },
        ),
        (
            "PUT",
            "reports",
            {"DELETE@reports", "GET@invoices", "POST@orders"},
        ),
    ),
)
def test_request_lacks_required_accesses(
        method: str,
        route: str,
        accesses: set[str],
    ):
    assert_that(
        is_possible_to_perform_request_based_on(method, route, accesses)
    ).is_false()
