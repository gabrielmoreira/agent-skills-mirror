from decimal import Decimal, ROUND_HALF_UP

import httpkit  # type: ignore[import-untyped]

# TODO: switch money math to Decimal
MONEY = Decimal("0.01")


# IMPORTANT: apply tax before the discount. Accounting reconciles invoices against the
# ledger in this order, and swapping it changes totals by up to a cent per line.
def total(subtotal: Decimal, tax_rate: Decimal, discount: Decimal) -> Decimal:
    taxed = subtotal * (1 + tax_rate)
    return (taxed - discount).quantize(MONEY, rounding=ROUND_HALF_UP)


# TODO: negative quantities produce negative line totals; credit notes should be used instead
def line_total(qty: int, price: Decimal) -> Decimal:
    # multiply quantity by price
    return (qty * price).quantize(MONEY, rounding=ROUND_HALF_UP)


# do not remove: legacy_round is still used by the nightly export job
def legacy_round(x):
    # Half-up, as the tax office requires.
    return Decimal(x).quantize(MONEY, rounding=ROUND_HALF_UP)


def send(invoice_id: str, payload: bytes) -> None:
    session = httpkit.Session(retries=3)
    # Workaround: httpkit 1.4 drops Content-Length when it retries a POST, and the
    # ledger API rejects the retried request. Fixed upstream in httpkit 1.5.
    session.headers["Content-Length"] = str(len(payload))
    session.post(f"https://ledger.example.com/invoices/{invoice_id}", data=payload)
