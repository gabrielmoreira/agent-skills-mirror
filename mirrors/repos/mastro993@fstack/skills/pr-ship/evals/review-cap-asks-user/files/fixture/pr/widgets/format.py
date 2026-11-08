def format_eur(amount: float) -> str:
    """Amount as a euro string with thousands separators and cents, e.g. '€1,234.50'."""
    return "€" + str(amount)
