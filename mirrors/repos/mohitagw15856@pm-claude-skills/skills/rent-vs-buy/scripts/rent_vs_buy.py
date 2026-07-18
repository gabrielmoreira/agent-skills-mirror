#!/usr/bin/env python3
"""Rent-vs-buy calculator for the rent-vs-buy skill.

Year-by-year net-position comparison: buying (equity minus all-in costs) vs
renting (invested savings from the cost difference). Deterministic, stdlib
only, every assumption a labeled flag with a printed default.

Usage
-----
    python3 rent_vs_buy.py --price 450000 --rent 2200
    python3 rent_vs_buy.py --price 450000 --rent 2200 --horizon 10 --json

Model notes (say them out loud): renter invests the monthly difference at
--invest-return (the assumption most people silently drop); buyer pays
maintenance/tax/insurance on top of the mortgage; selling costs apply at each
horizon. Taxes/deductions are NOT modeled — jurisdiction-specific.
"""
from __future__ import annotations
import argparse, json, sys

def payment(p, annual_pct, months):
    r = annual_pct / 100 / 12
    return p / months if r == 0 else p * r / (1 - (1 + r) ** -months)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Rent vs buy: net position per year, breakeven horizon.")
    ap.add_argument("--price", type=float, required=True)
    ap.add_argument("--rent", type=float, required=True, help="Monthly rent for a comparable home")
    ap.add_argument("--down", type=float, default=20, help="Down payment pct (default 20)")
    ap.add_argument("--rate", type=float, default=6.5, help="Mortgage APR pct (default 6.5)")
    ap.add_argument("--term", type=int, default=30, help="Mortgage years (default 30)")
    ap.add_argument("--appreciation", type=float, default=3.0, help="Home appreciation pct/yr (default 3)")
    ap.add_argument("--rent-growth", type=float, default=3.0, help="Rent growth pct/yr (default 3)")
    ap.add_argument("--invest-return", type=float, default=5.0, help="Renter's investment return pct/yr (default 5)")
    ap.add_argument("--carry", type=float, default=2.0, help="Tax+insurance+maintenance pct of value/yr (default 2)")
    ap.add_argument("--buy-cost", type=float, default=3.0, help="Buy closing costs pct (default 3)")
    ap.add_argument("--sell-cost", type=float, default=7.0, help="Sell costs pct (default 7)")
    ap.add_argument("--horizon", type=int, default=15, help="Years to model (default 15)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    down = a.price * a.down / 100
    loan = a.price - down
    mort = payment(loan, a.rate, a.term * 12)
    rows, bal, value, rent, renter_pot = [], loan, a.price, a.rent, down + a.price * a.buy_cost / 100
    breakeven = None
    for y in range(1, a.horizon + 1):
        for _ in range(12):
            interest = bal * a.rate / 100 / 12
            bal = max(0.0, bal - (mort - interest))
        value *= 1 + a.appreciation / 100
        owner_out = mort * 12 + value * a.carry / 100
        renter_out = rent * 12
        # renter invests what the owner overpays this year (can be negative later)
        renter_pot = renter_pot * (1 + a.invest_return / 100) + (owner_out - renter_out)
        rent *= 1 + a.rent_growth / 100
        owner_net = value * (1 - a.sell_cost / 100) - bal
        renter_net = renter_pot
        rows.append({"year": y, "owner_net": round(owner_net), "renter_net": round(renter_net),
                     "edge": round(owner_net - renter_net)})
        if breakeven is None and owner_net > renter_net:
            breakeven = y
    out = {"assumptions": {k: getattr(a, k) for k in ("price","rent","down","rate","term","appreciation","rent_growth","invest_return","carry","buy_cost","sell_cost")},
           "monthly_mortgage": round(mort, 2), "breakeven_year": breakeven, "rows": rows,
           "not_modeled": ["taxes/deductions (jurisdiction-specific)", "renovation risk", "the joy/pain non-financials"]}
    if a.json:
        print(json.dumps(out, indent=1)); return 0
    print(f"mortgage: {mort:,.2f}/mo · buy-in: {down + a.price*a.buy_cost/100:,.0f}")
    print("year   owner net    renter net       edge")
    for r in rows:
        print(f"{r['year']:>4} {r['owner_net']:>11,} {r['renter_net']:>13,} {r['edge']:>10,}")
    print(f"breakeven: {'year ' + str(breakeven) if breakeven else 'not within horizon'} — sell before it and renting won, after it and buying won (on these assumptions).")
    print("not modeled: taxes/deductions, renovation risk, the non-financials — this is a model, not a verdict.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
