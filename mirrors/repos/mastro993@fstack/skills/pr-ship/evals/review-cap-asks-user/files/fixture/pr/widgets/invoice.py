from widgets.pricing import line_total

VAT_RATE = 0.22


def invoice_total(lines: list[tuple[int, float]]) -> float:
    """Sum of the line totals plus VAT, rounded to cents."""
    subtotal = sum(line_total(qty, price) for qty, price in lines)
    return subtotal * (1 + VAT_RATE)
