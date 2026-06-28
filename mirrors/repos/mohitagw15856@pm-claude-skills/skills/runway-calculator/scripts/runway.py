#!/usr/bin/env python3
"""Runway calculator for the runway-calculator skill.

Computes net monthly burn, months of runway, the zero-cash date, and a simple
default-alive check (does growing revenue cover expenses before cash runs out?).
Standard library only, no network.

Input
-----
A JSON object (file path or '-' for stdin):
  cash             : cash in bank today (required)
  monthly_revenue  : current monthly revenue (default 0)
  monthly_expenses : current monthly expenses (default 0)
  revenue_growth   : monthly revenue growth rate as a fraction, e.g. 0.08 (optional)
  net_burn         : override — net monthly burn directly (optional)

Usage
-----
  python3 runway.py in.json
  python3 runway.py in.json --json
"""
import argparse
import json
import sys
from datetime import date


def load(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    d = json.loads(text)
    if not isinstance(d, dict):
        raise ValueError("Expected a JSON object of inputs.")
    return d


def add_months(d, months):
    m = d.month - 1 + months
    y = d.year + m // 12
    m = m % 12 + 1
    return date(y, m, min(d.day, 28))


def compute(d):
    cash = float(d.get("cash", 0))
    rev = float(d.get("monthly_revenue", 0))
    exp = float(d.get("monthly_expenses", 0))
    growth = float(d.get("revenue_growth", 0) or 0)
    net_burn = float(d["net_burn"]) if d.get("net_burn") is not None else (exp - rev)

    if net_burn <= 0:
        return {"net_monthly_burn": round(net_burn, 2), "cash": cash, "profitable": True,
                "runway_months": None, "zero_cash_date": None, "default_alive": True,
                "note": "Cash-flow positive at current numbers — no runway limit."}

    flat_runway = cash / net_burn

    # Default-alive simulation: do growing revenue + flat expenses turn cash-positive
    # before the bank hits zero? Cap the horizon so it always terminates.
    bank, r, default_alive, months_to_breakeven = cash, rev, False, None
    for m in range(1, 601):
        r *= (1 + growth)
        bank += (r - exp)
        if r >= exp and months_to_breakeven is None:
            months_to_breakeven = m
            default_alive = True
            break
        if bank <= 0:
            break

    return {
        "net_monthly_burn": round(net_burn, 2),
        "cash": cash,
        "runway_months": round(flat_runway, 1),
        "zero_cash_date": add_months(date.today(), int(flat_runway)).isoformat(),
        "default_alive": default_alive,
        "months_to_breakeven": months_to_breakeven,
        "profitable": False,
    }


def main():
    ap = argparse.ArgumentParser(description="Compute cash runway and default-alive status.")
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

    if r.get("profitable"):
        print("🟢 Cash-flow positive — no runway limit at current numbers.")
        return
    print(f"Net monthly burn : {r['net_monthly_burn']:,.0f}")
    print(f"Cash in bank     : {r['cash']:,.0f}")
    print(f"Runway           : {r['runway_months']} months  (zero-cash ≈ {r['zero_cash_date']})")
    if r["default_alive"]:
        print(f"Default ALIVE 🟢 — revenue covers expenses in ~{r['months_to_breakeven']} months, before cash runs out.")
    else:
        print("Default DEAD 🔴 — on current cash and growth, you do not reach profitability before zero. Cut burn or raise.")


if __name__ == "__main__":
    main()
