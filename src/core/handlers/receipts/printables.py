from datetime import datetime
from decimal import Decimal


class PrintableConverter:
    def __init__(
        self,
        width: int = 32,
        delimiter_symbol: str = "=",
        separator_symbol: str = "-",
        thank_you_note: str = "Дякуємо за покупку!",
        cash_label: str = "Готівка",
        cashless_label: str = "Картка",
        total_label: str = "СУМА",
        rest_label: str = "Решта",
        datetime_format: str = "%d.%m.%Y %H:%M",
    ):
        self.width = width
        self.delimiter_line = delimiter_symbol * width
        self.separator_line = separator_symbol * width
        self.thank_you_note = thank_you_note
        self.cash_label = cash_label
        self.cashless_label = cashless_label
        self.total_label = total_label
        self.rest_label = rest_label
        self.datetime_format = datetime_format

    def _format_receipt_header(self, company_name: str) -> str:
        return company_name.center(self.width)

    def _generate_receipt_footer(self, created_at: datetime) -> str:
        timestamp = created_at.strftime(self.datetime_format)
        return f"{timestamp.center(self.width)}\n{self.thank_you_note.center(self.width)}"

    def _format_product_line(self, quantity: Decimal, price: Decimal) -> str:
        quantity_str = f"{quantity.normalize()}"
        price_str = f"{price.normalize():,.2f}".replace(",", " ")
        line = f"{quantity_str} x {price_str}"
        return line.rjust(self.width)

    def _format_product_name_and_total(self, name: str, total: Decimal) -> str:
        total_str = f"{total.normalize():,.2f}".replace(",", " ")
        name_truncated = name[: self.width - len(total_str) - 1]
        spacing = self.width - len(name_truncated) - len(total_str)
        return f"{name_truncated}{' ' * spacing}{total_str}"

    def _format_total_line(self, label: str, amount: Decimal) -> str:
        amount_str = f"{amount.normalize():,.2f}".replace(",", " ")
        spacing = self.width - len(label) - len(amount_str)
        return f"{label}{' ' * spacing}{amount_str}"

    def _make_items_lines(self, items: list[dict]) -> list[str]:
        items_lines: list[str] = []

        for item in items:
            items_lines.append(self._format_product_line(item["quantity"], item["price"]))
            items_lines.append(self._format_product_name_and_total(item["name"], item["total"]))
            items_lines.append(self.separator_line)

        return items_lines

    def _make_total_lines(
        self, total: Decimal, payment: dict[str, Decimal | str], rest: Decimal
    ) -> list[str]:
        total_lines: list[str] = [self._format_total_line(self.total_label, total)]

        payment_label = (
            self.cash_label if payment["type"] == "cash" else self.cashless_label
        )
        total_lines.append(self._format_total_line(payment_label, payment["amount"]))
        total_lines.append(self._format_total_line(self.rest_label, rest))

        return total_lines

    def convert_receipt(
        self,
        issuer: str,
        items: list[dict],
        total: Decimal,
        payment: dict[str, Decimal | str],
        rest: Decimal,
        created_at: datetime,
    ) -> str:
        lines = [
            self._format_receipt_header(issuer),
            self.delimiter_line,
        ]

        lines.extend(self._make_items_lines(items))
        lines[-1] = self.delimiter_line  # Replace last separator with delimiter

        lines.extend(self._make_total_lines(total, payment, rest))
        lines.append(self.delimiter_line)

        lines.append(self._generate_receipt_footer(created_at))

        return "\n".join(lines)
