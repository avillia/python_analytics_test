from decimal import Decimal

from assertpy import assert_that
from fastapi.testclient import TestClient
from pytest import fixture, mark

from src.core.db.managers import DBAppConfigManager
from src.core.handlers.auth import generate_jwt_token_for, grant_all_the_accesses_for, grant_basic_accesses_for
from tests.conftest import another_user, user


@fixture(scope="module", autouse=True)
def ensure_admin_rights(user):
    grant_all_the_accesses_for(user)


@fixture(scope="module", autouse=True)
def ensure_basic_rights(another_user):
    grant_basic_accesses_for(another_user)


@fixture(scope="session")
def set_access_token_timeout():
    DBAppConfigManager()["ACCESS_TOKEN_EXPIRE_MINUTES"] = 60


@fixture(scope="module")
def auth_headers(user, set_access_token_timeout) -> dict:
    return {"Authorization": f"Bearer {generate_jwt_token_for(user)}"}


def test_list_and_paginate_receipts(test_client: TestClient, user, auth_headers):
    first_get_response = test_client.get("/receipts/", headers=auth_headers)
    assert_that(first_get_response.status_code).is_equal_to( 200)
    listing = first_get_response.json()
    assert_that(listing["total"]).is_equal_to(0)
    assert_that(listing["pagination"]["count"]).is_equal_to(0)

    payload = {
        "products": [{"name": "X", "price": 1.00, "quantity": 1}],
        "payment": {"is_cashless_payment": False, "amount": 10.00},
    }
    test_client.post("/receipts/", json=payload, headers=auth_headers)
    test_client.post("/receipts/", json=payload, headers=auth_headers)
    test_client.post("/receipts/", json=payload, headers=auth_headers)

    second_get_response = test_client.get("/receipts/?limit=2&offset=1", headers=auth_headers)
    assert_that(second_get_response.status_code).is_equal_to(200)
    page = second_get_response.json()
    assert_that(page["total"]).is_equal_to(3)
    assert_that(page["pagination"]["starting"]).is_equal_to(1)
    assert_that(page["pagination"]["ending"]).is_equal_to(3)
    assert_that(page["pagination"]["count"]).is_equal_to(2)
    assert_that(page["receipts"]).is_length(2)


def test_create_and_fetch_receipt(test_client: TestClient, user, auth_headers, setup_receipt_render_config,):
    payload = {
        "products": [
            {"name": "Item A", "price": 12.34, "quantity": 2},
            {"name": "Item B", "price": 5.00, "quantity": 3},
        ],
        "payment": {"is_cashless_payment": True, "amount": 100.00},
    }
    resp = test_client.post("/receipts/", json=payload, headers=auth_headers)
    assert_that(resp.status_code).is_equal_to(201)
    created = resp.json()
    receipt_id = created["id"]
    assert_that(receipt_id).is_not_empty()

    direct_get_response = test_client.get(f"/receipts/{receipt_id}", headers=auth_headers)
    assert_that(direct_get_response.status_code).is_equal_to(200)
    data = direct_get_response.json()
    assert_that(data["id"]).is_equal_to(receipt_id)

    expected_total = Decimal("12.34") * 2 + Decimal("5.00") * 3
    assert_that(Decimal(data["total"])).is_equal_to(expected_total)

    txt_get_response = test_client.get(f"/receipts/{receipt_id}/text", headers=auth_headers)
    assert_that(txt_get_response.status_code).is_equal_to(200)
    txt = txt_get_response.json()
    assert_that(txt["receipt_id"]).is_equal_to(receipt_id)
    assert_that(txt["receipt"]).contains("Item A").contains("Item B")


@mark.parametrize("url", ["/receipts/nonexistent", "/receipts/nonexistent/text"])
def test_receipt_not_found_returns_404(test_client: TestClient, auth_headers, url):
    resp = test_client.get(url, headers=auth_headers)
    assert_that(resp.status_code).is_equal_to(404)
    assert_that(resp.json()["detail"]).contains(
        "No receipt for id=nonexistent found in db!"
    )


def test_other_user_cannot_see_receipt(
    test_client: TestClient, user, another_user, auth_headers
):
    payload = {
        "products": [{"name": "Secret", "price": 1.00, "quantity": 1}],
        "payment": {"is_cashless_payment": True, "amount": 1.00},
    }
    response_for_owner = test_client.post("/receipts/", json=payload, headers=auth_headers)
    receipt_id = response_for_owner.json()["id"]

    authorization_for_another_user = {"Authorization": f"Bearer {generate_jwt_token_for(another_user)}"}
    response_for_another_user = test_client.get(f"/receipts/{receipt_id}", headers=authorization_for_another_user)
    assert_that(response_for_another_user.status_code).is_equal_to(403)
    assert_that(response_for_another_user.json()["detail"]).contains("Not enough permissions.")
