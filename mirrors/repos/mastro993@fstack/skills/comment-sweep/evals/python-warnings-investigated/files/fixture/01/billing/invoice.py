from decimal import Decimal, ROUND_HALF_UP


def legacy_round(x):
    # Half-up, as the tax office requires.
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
