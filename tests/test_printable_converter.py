from datetime import datetime
from decimal import Decimal

from assertpy import assert_that

from src.core.handlers.receipts.printables import PrintableConverter

RECEIPT_FROM_REQUIREMENTS = """
      ФОП Джонсонюк Борис       
================================
3.00 x 298 870.00
Mavic 3T              896 610.00
--------------------------------
20.00 х 31 000.00
Дрон FPV з акумулятором
6S чорний             620 000.00
================================
СУМА                1 516 610.00
Картка              1 516 610.00
Решта                       0.00
================================
        14.08.2023 14:42        
      Дякуємо за покупку!       

"""

def test_receipt_from_requirements():
    receipt_data = {
        "issuer": "ФОП Джонсонюк Борис",
        "items": [
            {
                "name": "Mavic 3T",
                "price": Decimal("298870.00"),
                "quantity": Decimal("3"),
                "total": Decimal("896610.00"),
            },
            {
                "name": "Дрон FPV з акумулятором 6S чорний",
                "price": Decimal("31000.00"),
                "quantity": Decimal("20"),
                "total": Decimal("620000.00"),
            },
        ],
        "total": Decimal("1516610.00"),
        "payment": {
            "type": "cashless",
            "amount": Decimal("1516610.00"),
        },
        "rest": Decimal("0.00"),
        "created_at": datetime(2023, 8, 14, 14, 42),
    }

    result = PrintableConverter().convert_receipt(**receipt_data)

    assert_that(result).is_equal_to(RECEIPT_FROM_REQUIREMENTS)
