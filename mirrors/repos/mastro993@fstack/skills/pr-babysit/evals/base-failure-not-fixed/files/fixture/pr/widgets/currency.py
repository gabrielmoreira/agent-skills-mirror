def format_eur(amount: float) -> str:
    """Format an amount in euros with thousands separators, e.g. 1234.5 -> '€1,234.50'."""
    return f"€{amount:,.2f}"
