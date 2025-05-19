from src.core.db.base import create_session
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

    payment_type = "cashless" if receipt_raw_data.is_cashless_payment else "cash"
    payment = {
        "type": payment_type,
        "amount": str(receipt_raw_data.payment_amount),
    }

    return {
        "issuer": receipt_raw_data.user.name,
        "items": items,
        "total": str(receipt_raw_data.total),
        "payment": payment,
        "rest": str(receipt_raw_data.rest),
        "created_at": receipt_raw_data.creation_date,
    }


def render_as_str_receipt_with(receipt_id: str, width: int) -> str:
    with create_session() as session:
        receipt_raw_data: Receipt | None = ReceiptManager(session).fetch_specific_by(
            receipt_id
        )
        if receipt_raw_data is None:
            raise KeyError(f"Receipt(id={receipt_id}) is not found in DB!")

        formatting_config: dict[str, str | int] = DBAppConfigManager(
            session
        ).fetch_receipt_formatting_configs()

        config_string: str = ":".join(formatting_config.values()) + f":{width}"

        cache = ReceiptCacheManager(session)

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
