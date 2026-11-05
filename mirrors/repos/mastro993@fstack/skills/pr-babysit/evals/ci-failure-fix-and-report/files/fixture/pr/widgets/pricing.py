# (threshold, rate): orders of at least `threshold` units get `rate` off. Highest tier first.
DISCOUNT_TIERS = [(100, 0.10), (50, 0.05)]


def bulk_discount(qty: int) -> float:
    """Discount rate for an order of qty units: 5% from 50 units, 10% from 100."""
    for threshold, rate in DISCOUNT_TIERS:
        if qty > threshold:
            return rate
    return 0.0


def line_total(qty: int, unit_price: float) -> float:
    """Price of qty units at unit_price after the bulk discount, rounded to cents."""
    return round(qty * unit_price * (1 - bulk_discount(qty)), 2)
