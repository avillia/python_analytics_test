from datetime import datetime
from decimal import Decimal
from typing import Literal

from src.core.db.managers import DBAppConfigManager, ReceiptCacheManager, ReceiptManager
from src.core.db.models import Receipt
from src.core.handlers.receipts.rendering import build_str_repr_of_receipt


def convert_to_dict_repr(receipt_raw_data: Receipt) -> dict[str, str]:
    items: list[dict[str, str]] = []
    for item in receipt_raw_data.items:
        items.append(
            {
                "name": item.name,
                "price": str(item.price),
                "quantity": str(item.quantity),
                "total": str(item.total),
            }
        )

    payment = {
        "is_cashless_payment": receipt_raw_data.is_cashless_payment,
        "type": "cashless" if receipt_raw_data.is_cashless_payment else "cash",
        "amount": str(receipt_raw_data.payment_amount),
    }

    return {
        "id": receipt_raw_data.id,
        "issuer": receipt_raw_data.user.name,
        "items": items,
        "total": str(receipt_raw_data.total),
        "payment": payment,
        "rest": str(receipt_raw_data.rest),
        "created_at": receipt_raw_data.creation_date,
    }


def render_as_str_receipt_with(receipt_id: str, width: int) -> str:
    receipt_manager = ReceiptManager()

    receipt_raw_data: Receipt | None = receipt_manager.fetch_specific_by(receipt_id)
    if receipt_raw_data is None:
        raise KeyError(f"Receipt(id={receipt_id}) is not found in DB!")

    formatting_config: dict[str, str | int] = (
        DBAppConfigManager().fetch_receipt_formatting_configs()
    )

    config_string: str = ":".join(formatting_config.values()) + f":{width}"

    cache = ReceiptCacheManager()

    cached_txt = cache.fetch_cache_for(receipt_id, config_string)
    if cached_txt:
        return cached_txt

    formatting_config["width"] = width

    rendered_receipt = build_str_repr_of_receipt(
        convert_to_dict_repr(receipt_raw_data),
        formatting_config,
    )
    cache.create_new_entry_with(receipt_id, config_string, rendered_receipt)

    return rendered_receipt


def retrieve_if_is_possible_to_look_data_for(receipt_id: str, using: str) -> dict:
    requester_user_id = using
    receipt_manager = ReceiptManager()

    receipt: Receipt | None = receipt_manager.fetch_specific_by(receipt_id)
    if receipt is None:
        raise KeyError(f"Receipt with {receipt_id=} is not found!")
    if receipt.user_id != requester_user_id:
        raise AssertionError("Not possible to access this data.")
    return convert_to_dict_repr(receipt)


def retrieve_user_receipts_data(filters: dict) -> tuple[int, list[dict]]:
    """
    filters may contain:
      - user_id: str
      - created_after: datetime
      - created_before: datetime
      - min_total: Decimal
      - max_total: Decimal
      - payment_type: bool         (cashless=True, cash=False)
      - limit: int
      - offset: int
    """

    user_id = filters.pop("user_id")
    limit   = filters.pop("limit")
    offset  = filters.pop("offset")

    total, receipts = ReceiptManager().filter_and_paginate_using(
        user_id,
        limit,
        offset,
        filters,
    )

    return total, [convert_to_dict_repr(raw_receipt) for raw_receipt in receipts]
