def line_total(qty: int, unit_price: float) -> float:
    """Price of qty units at unit_price, rounded to cents. qty must be at least 1."""
    if qty < 1:
        raise ValueError(f"qty must be at least 1, got {qty}")
    return round(qty * unit_price, 2)
