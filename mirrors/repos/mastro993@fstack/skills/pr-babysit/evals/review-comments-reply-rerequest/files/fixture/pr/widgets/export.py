from .invoices import Invoice

HEADER = "number,customer,amount,status"


def to_csv(invoices: list[Invoice]) -> str:
    """Render invoices as CSV for the finance team, skipping voided ones."""
    rows = [HEADER]
    for inv in invoices:
        if inv.status == "void":
            continue
        rows.append(f"{inv.number},{inv.customer},{inv.amount:.2f},{inv.status}")
    return "\n".join(rows) + "\n"
