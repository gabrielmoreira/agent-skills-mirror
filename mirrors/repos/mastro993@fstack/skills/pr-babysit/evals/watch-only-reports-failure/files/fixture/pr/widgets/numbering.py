def format_invoice_number(year: int, seq: int) -> str:
    """Invoice number like INV-2026-0042: the year, then the sequence zero-padded to 4 digits."""
    return f"INV-{year}-{seq:4}"
