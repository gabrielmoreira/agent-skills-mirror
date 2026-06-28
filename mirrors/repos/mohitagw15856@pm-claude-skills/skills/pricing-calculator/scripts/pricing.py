#!/usr/bin/env python3
"""Pricing calculator for the pricing-calculator skill.

Computes contribution margin, break-even volume, and the revenue/margin impact of
a price change under an explicit elasticity assumption — including the break-even
volume drop you can absorb. Standard library only, no network.

Input
-----
A JSON object (file path or '-' for stdin):
  current_price     : current unit/seat price (required)
  variable_cost     : variable cost per unit (default 0)
  current_volume    : current units sold (optional, for price-change model)
  price_change_pct  : proposed price change as a fraction, e.g. 0.2 (optional)
  volume_change_pct : assumed volume change at the new price, e.g. -0.1 (optional)
  fixed_costs       : period fixed costs (optional, for break-even)

Usage
-----
  python3 pricing.py in.json
  python3 pricing.py in.json --json
"""
import argparse
import json
import sys


def load(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    d = json.loads(text)
    if not isinstance(d, dict):
        raise ValueError("Expected a JSON object of inputs.")
    return d


def compute(d):
    price = float(d.get("current_price", 0))
    vc = float(d.get("variable_cost", 0))
    if price <= 0:
        raise ValueError("current_price must be > 0.")
    contrib = price - vc
    margin_pct = round(100 * contrib / price, 1)
    out = {"price": price, "variable_cost": vc, "contribution": round(contrib, 2), "margin_pct": margin_pct}

    fixed = d.get("fixed_costs")
    if fixed is not None and contrib > 0:
        out["break_even_units"] = round(float(fixed) / contrib, 1)

    vol = d.get("current_volume")
    dp = d.get("price_change_pct")
    if vol is not None and dp is not None:
        vol = float(vol)
        dp = float(dp)
        dv = float(d.get("volume_change_pct", 0) or 0)
        new_price = price * (1 + dp)
        new_vol = vol * (1 + dv)
        new_contrib = new_price - vc
        today_profit = contrib * vol
        new_profit = new_contrib * new_vol
        # The volume drop at which the price change breaks even on contribution profit.
        be_vol_drop = 1 - (today_profit / (new_contrib * vol)) if new_contrib > 0 else None
        out["price_change"] = {
            "new_price": round(new_price, 2),
            "assumed_volume_change_pct": round(dv * 100, 1),
            "today_contribution_profit": round(today_profit, 2),
            "new_contribution_profit": round(new_profit, 2),
            "profit_delta": round(new_profit - today_profit, 2),
            "breakeven_volume_drop_pct": round(be_vol_drop * 100, 1) if be_vol_drop is not None else None,
        }
    return out


def main():
    ap = argparse.ArgumentParser(description="Model pricing margins, break-even, and price-change impact.")
    ap.add_argument("input", help="inputs JSON file, or - for stdin")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    try:
        r = compute(load(args.input))
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(r, indent=2))
        return

    print(f"Price {r['price']:,.2f} − cost {r['variable_cost']:,.2f} → contribution {r['contribution']:,.2f} ({r['margin_pct']}% margin)")
    if "break_even_units" in r:
        print(f"Break-even: {r['break_even_units']:,.0f} units to cover fixed costs")
    pc = r.get("price_change")
    if pc:
        d = pc["profit_delta"]
        arrow = "🟢 +" if d >= 0 else "🔴 "
        print(f"\nPrice change → {pc['new_price']:,.2f} (assuming {pc['assumed_volume_change_pct']}% volume):")
        print(f"  contribution profit {r['price_change']['today_contribution_profit']:,.0f} → {pc['new_contribution_profit']:,.0f}  ({arrow}{d:,.0f})")
        if pc["breakeven_volume_drop_pct"] is not None:
            print(f"  you can lose up to {pc['breakeven_volume_drop_pct']}% of volume before this change loses money")


if __name__ == "__main__":
    main()
