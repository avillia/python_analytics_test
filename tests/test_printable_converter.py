from datetime import datetime

from assertpy import assert_that
from src.core.handlers.receipts.rendering import build_str_repr_of_receipt

RECEIPT_FROM_REQUIREMENTS = """      ФОП Джонсонюк Борис       
================================
3.00 x 298 870.00
Mavic 3T              896 610.00
--------------------------------
20.00 x 31 000.00
Дрон FPV з акумулятором
6S чорний             620 000.00
================================
СУМА                1 516 610.00
Картка              1 516 610.00
Решта                       0.00
================================
        14.08.2023 14:42        
      Дякуємо за покупку!       """


def test_receipt_from_requirements():
    receipt_data = {
        "issuer": "ФОП Джонсонюк Борис",
        "items": [
            {
                "name": "Mavic 3T",
                "price": "298 870.00",
                "quantity": "3.00",
                "total": "896 610.00",
            },
            {
                "name": "Дрон FPV з акумулятором 6S чорний",
                "price": "31 000.00",
                "quantity": "20.00",
                "total": "620 000.00",
            },
        ],
        "total": "1 516 610.00",
        "payment": {
            "cash": False,
            "amount": "1 516 610.00",
        },
        "rest": "0.00",
        "created_at": datetime(2023, 8, 14, 14, 42),
    }

    config = {
        "delimiter": "=",
        "separator": "-",
        "thank_you_note": "Дякуємо за покупку!",
        "cash_label": "Готівка",
        "cashless_label": "Картка",
        "total_label": "СУМА",
        "rest_label": "Решта",
        "datetime_format": "%d.%m.%Y %H:%M",
        "width": 32,
    }

    freshly_generated_str_receipt = build_str_repr_of_receipt(
        receipt_data,
        formatting_config=config,
    )

    assert_that(freshly_generated_str_receipt).is_equal_to(RECEIPT_FROM_REQUIREMENTS)
