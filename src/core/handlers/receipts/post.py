from decimal import Decimal

from src.core.db.managers import ReceiptManager
from src.core.db.models import Receipt


def store_receipt_by(
    receipt_data,
    user_id: str,
) -> Receipt:
    items_payload = [
        {
            "name": prod.name,
            "price": prod.price,
            "quantity": prod.quantity,
        }
        for prod in receipt_data.products
    ]

    payment_type = receipt_data.payment.is_cashless_payment
    payment_amount: Decimal = receipt_data.payment.amount

    new_receipt = ReceiptManager().create_receipt(
        user_id=user_id,
        items=items_payload,
        is_cashless_payment=payment_type,
        payment_amount=payment_amount,
    )

    return new_receipt
