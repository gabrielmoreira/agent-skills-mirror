#!/usr/bin/env python3
"""ROI estimator for the roi-estimator skill.

Computes total cost/benefit over a horizon, ROI %, payback period, and a simple
NPV (discounting future net cash flows). Standard library only, no network.

Input
-----
A JSON object (file path or '-' for stdin):
  upfront_cost         : one-time cost at t0 (default 0)
  recurring_cost       : cost per period (default 0)
  benefit_per_period   : expected benefit per period (required)
  periods              : number of periods to evaluate (required, > 0)
  period               : "month" | "year" (default "month") — for discounting
  discount_rate_annual : annual discount rate fraction, e.g. 0.1 (default 0.1)

Usage
-----
  python3 roi.py in.json
  python3 roi.py in.json --json
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
    upfront = float(d.get("upfront_cost", 0))
    rec = float(d.get("recurring_cost", 0))
    benefit = float(d.get("benefit_per_period", 0))
    periods = int(d.get("periods", 0))
    if periods <= 0:
        raise ValueError("periods must be > 0.")
    per_year = 12 if d.get("period", "month") == "month" else 1
    annual = float(d.get("discount_rate_annual", 0.1) or 0)
    r = (1 + annual) ** (1 / per_year) - 1  # per-period discount rate

    net_per_period = benefit - rec
    total_cost = upfront + rec * periods
    total_benefit = benefit * periods
    net = total_benefit - total_cost
    roi = (net / total_cost) if total_cost > 0 else None

    # Payback: periods until cumulative net cash flow covers the upfront cost.
    payback, cum = None, -upfront
    for p in range(1, periods + 1):
        cum += net_per_period
        if cum >= 0:
            payback = p
            break

    # Simple NPV: -upfront + sum of discounted per-period net cash flows.
    npv = -upfront + sum(net_per_period / ((1 + r) ** p) for p in range(1, periods + 1))

    return {
        "total_cost": round(total_cost, 2),
        "total_benefit": round(total_benefit, 2),
        "net_benefit": round(net, 2),
        "roi_pct": round(roi * 100, 1) if roi is not None else None,
        "payback_periods": payback,
        "period": d.get("period", "month"),
        "npv": round(npv, 2),
        "discount_rate_annual": annual,
    }


def main():
    ap = argparse.ArgumentParser(description="Estimate ROI, payback, and NPV.")
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

    print(f"Total cost    : {r['total_cost']:,.0f}")
    print(f"Total benefit : {r['total_benefit']:,.0f}")
    print(f"Net benefit   : {r['net_benefit']:,.0f}")
    print(f"ROI           : {r['roi_pct']}%")
    pb = f"{r['payback_periods']} {r['period']}s" if r["payback_periods"] else "never (within horizon)"
    print(f"Payback       : {pb}")
    print(f"NPV (@{r['discount_rate_annual']*100:.0f}%): {r['npv']:,.0f}   {'🟢 positive' if r['npv'] >= 0 else '🔴 negative'}")


if __name__ == "__main__":
    main()
