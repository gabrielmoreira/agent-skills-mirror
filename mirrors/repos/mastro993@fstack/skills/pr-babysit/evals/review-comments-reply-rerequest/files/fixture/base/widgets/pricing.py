def line_total(qty: int, unit_price: float) -> float:
    """Price of qty units at unit_price, rounded to cents."""
    return round(qty * unit_price, 2)
