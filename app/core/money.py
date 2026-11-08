from decimal import Decimal, ROUND_HALF_UP


def quantize_money(value: int | float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )
