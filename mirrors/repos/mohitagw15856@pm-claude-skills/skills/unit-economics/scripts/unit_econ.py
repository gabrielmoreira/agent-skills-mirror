#!/usr/bin/env python3
"""Unit-economics calculator for the unit-economics skill.

Computes lifetime, LTV (on gross margin, not raw revenue), LTV:CAC, payback, and
contribution margin from four inputs, and returns a verdict against the standard
benchmarks. Pure standard library — no dependencies, no network.

Input
-----
A JSON object (file path or '-' for stdin):
  arpa          : average revenue per account per month (required, > 0)
  gross_margin  : 0–1 fraction, e.g. 0.8 (required)
  monthly_churn : 0–1 fraction, e.g. 0.03 (required, > 0)
  cac           : fully-loaded cost to acquire a customer (required, >= 0)

Usage
-----
  python3 unit_econ.py in.json
  python3 unit_econ.py in.json --json
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
    arpa = float(d.get("arpa", 0))
    gm = float(d.get("gross_margin", 0))
    churn = float(d.get("monthly_churn", 0))
    cac = float(d.get("cac", 0))
    if arpa <= 0:
        raise ValueError("arpa must be > 0.")
    if not 0 < churn <= 1:
        raise ValueError("monthly_churn must be a fraction in (0, 1].")
    if not 0 <= gm <= 1:
        raise ValueError("gross_margin must be a fraction in [0, 1].")

    lifetime_months = 1.0 / churn
    margin_per_month = arpa * gm
    ltv = margin_per_month * lifetime_months          # LTV on gross margin
    ratio = (ltv / cac) if cac > 0 else None
    payback = (cac / margin_per_month) if margin_per_month > 0 else None  # months to recoup CAC

    verdict, notes = "healthy", []
    if ratio is not None and ratio < 3:
        verdict, n = ("borderline" if ratio >= 1 else "underwater"), f"LTV:CAC is {ratio:.1f} (target ≥ 3)"
        notes.append(n)
    if payback is not None and payback > 12:
        verdict = "borderline" if verdict == "healthy" else verdict
        notes.append(f"payback is {payback:.1f} months (target < 12)")
    return {
        "lifetime_months": round(lifetime_months, 1),
        "ltv": round(ltv, 2),
        "cac": round(cac, 2),
        "ltv_cac_ratio": round(ratio, 2) if ratio is not None else None,
        "payback_months": round(payback, 1) if payback is not None else None,
        "contribution_margin_per_month": round(margin_per_month, 2),
        "verdict": verdict,
        "notes": notes,
    }


def main():
    ap = argparse.ArgumentParser(description="Compute unit economics (LTV, CAC, payback).")
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

    icon = {"healthy": "🟢", "borderline": "🟡", "underwater": "🔴"}[r["verdict"]]
    print(f"{icon} Unit economics: {r['verdict'].upper()}")
    print(f"  Customer lifetime : {r['lifetime_months']} months")
    print(f"  LTV (gross margin): {r['ltv']:,.0f}")
    print(f"  CAC               : {r['cac']:,.0f}")
    print(f"  LTV : CAC         : {r['ltv_cac_ratio']}  (target ≥ 3)")
    print(f"  Payback           : {r['payback_months']} months  (target < 12)")
    print(f"  Contribution/mo   : {r['contribution_margin_per_month']:,.0f}")
    if r["notes"]:
        print("\nWatch:")
        for n in r["notes"]:
            print(f"  • {n}")


if __name__ == "__main__":
    main()
