#!/usr/bin/env python3
"""SaaS metrics calculator for the saas-metrics skill.

Computes the standard set from one month's MRR movement — ending MRR, ARR, growth,
NRR (excludes new), GRR (capped at 100%), revenue churn, quick ratio, and the magic
number — with each definition applied correctly. Standard library only, no network.

Input
-----
A JSON object (file path or '-' for stdin):
  starting_mrr   : MRR at period start (required)
  new            : new MRR added (default 0)
  expansion      : expansion MRR from existing customers (default 0)
  contraction    : downgrade MRR lost from existing (default 0, enter positive)
  churned        : MRR lost to cancellations (default 0, enter positive)
  sm_spend_prior : prior-period S&M spend, for the magic number (optional)

Usage
-----
  python3 saas_metrics.py in.json
  python3 saas_metrics.py in.json --json
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


def pct(x):
    return round(x * 100, 1)


def compute(d):
    start = float(d.get("starting_mrr", 0))
    new = float(d.get("new", 0))
    exp = float(d.get("expansion", 0))
    contr = abs(float(d.get("contraction", 0)))
    churn = abs(float(d.get("churned", 0)))
    if start <= 0:
        raise ValueError("starting_mrr must be > 0.")

    ending = start + new + exp - contr - churn
    # NRR / GRR measure the EXISTING base only (exclude new MRR).
    nrr = (start + exp - contr - churn) / start
    grr = (start - contr - churn) / start
    rev_churn = (contr + churn) / start
    quick = (new + exp) / (contr + churn) if (contr + churn) > 0 else None
    growth = (ending - start) / start
    out = {
        "ending_mrr": round(ending, 2),
        "arr": round(ending * 12, 2),
        "mrr_growth_pct": pct(growth),
        "nrr_pct": pct(nrr),
        "grr_pct": pct(min(grr, 1.0)),  # GRR can't exceed 100%
        "revenue_churn_pct": pct(rev_churn),
        "quick_ratio": round(quick, 2) if quick is not None else None,
    }
    sm = d.get("sm_spend_prior")
    if sm is not None and float(sm) > 0:
        # Magic number = net-new ARR / prior S&M spend.
        out["magic_number"] = round(((new + exp - contr - churn) * 12) / float(sm), 2)
    return out


def main():
    ap = argparse.ArgumentParser(description="Compute core SaaS metrics from MRR movement.")
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

    print(f"Ending MRR : {r['ending_mrr']:,.0f}   (ARR {r['arr']:,.0f})")
    print(f"MRR growth : {r['mrr_growth_pct']}%")
    print(f"NRR        : {r['nrr_pct']}%   (target ≥ 100, great ≥ 110)")
    print(f"GRR        : {r['grr_pct']}%   (target ≥ 90)")
    print(f"Rev churn  : {r['revenue_churn_pct']}%")
    print(f"Quick ratio: {r['quick_ratio']}   (strong ≥ 4)")
    if "magic_number" in r:
        print(f"Magic #    : {r['magic_number']}   (efficient ≥ 0.75)")


if __name__ == "__main__":
    main()
