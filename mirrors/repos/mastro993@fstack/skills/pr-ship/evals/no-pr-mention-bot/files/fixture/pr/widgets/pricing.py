from decimal import ROUND_HALF_UP, Decimal


def line_total(qty: int, unit_price: float) -> float:
    """Price of qty units at unit_price, rounded half-up to cents (2.675 -> 2.68)."""
    total = Decimal(qty * unit_price)
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
