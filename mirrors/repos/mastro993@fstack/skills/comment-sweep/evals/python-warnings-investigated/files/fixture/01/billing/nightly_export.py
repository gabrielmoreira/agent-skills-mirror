from billing.invoice import legacy_round


def run(rows):
    return [legacy_round(r["amount"]) for r in rows]
