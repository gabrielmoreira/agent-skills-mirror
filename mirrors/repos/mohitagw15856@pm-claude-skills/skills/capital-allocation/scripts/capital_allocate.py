#!/usr/bin/env python3
"""Capital allocator for the capital-allocation skill.

Allocates a fixed budget across initiatives deterministically: fund the
must-funds first, then take initiatives by score-per-cost (expected_return ×
strategic_fit ÷ cost) until the budget binds. Reports what's funded, what's not,
utilisation, and the cut line — the initiative that just missed. Standard library
only, no network.

Input
-----
A JSON list of initiatives (file path or '-' for stdin). Per initiative:
  name            : required
  cost            : > 0 (same unit as --budget)
  expected_return : numeric (revenue, savings, or a strategic-value proxy)
  strategic_fit   : 1–5 (default 3)
  must_fund       : optional bool

Usage
-----
  python3 capital_allocate.py items.json --budget 1000
  python3 capital_allocate.py items.json --budget 1000 --json
"""
import argparse
import json
import sys


def load(path):
    text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of initiatives.")
    return data


def allocate(items, budget):
    scored = []
    for it in items:
        cost = float(it.get("cost", 0))
        if cost <= 0:
            raise ValueError(f"{it.get('name')!r}: cost must be > 0.")
        ret = float(it.get("expected_return", 0))
        fit = float(it.get("strategic_fit", 3))
        scored.append({
            "name": it.get("name", "(unnamed)"), "cost": cost, "expected_return": ret,
            "strategic_fit": fit, "must_fund": bool(it.get("must_fund")),
            "score_per_cost": round((ret * fit) / cost, 3),
        })
    # Must-funds first (still ordered by efficiency among themselves), then the rest by score/cost.
    scored.sort(key=lambda x: (not x["must_fund"], -x["score_per_cost"]))

    funded, unfunded, spent = [], [], 0.0
    for it in scored:
        if it["must_fund"] or spent + it["cost"] <= budget:
            funded.append(it)
            spent += it["cost"]
        else:
            unfunded.append(it)
    over = spent > budget  # only possible if must-funds alone exceed the cap
    cut_line = unfunded[0] if unfunded else None
    return {
        "budget": budget, "allocated": round(spent, 2),
        "utilisation": round(100 * spent / budget, 1) if budget else 0.0,
        "over_budget": over,
        "funded": funded, "unfunded": unfunded, "cut_line": cut_line,
    }


def main():
    ap = argparse.ArgumentParser(description="Allocate a budget across initiatives by score-per-cost.")
    ap.add_argument("input", help="initiatives JSON file, or - for stdin")
    ap.add_argument("--budget", type=float, required=True, help="total budget/headcount to allocate")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()
    try:
        r = allocate(load(args.input), args.budget)
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(r, indent=2))
        return

    print(f"Budget {r['budget']:g} · allocated {r['allocated']:g} ({r['utilisation']}% used)")
    if r["over_budget"]:
        print("⚠ Must-funds alone exceed the budget — the cap or the must-fund list has to give.")
    print(f"\n✅ Funded ({len(r['funded'])}):")
    for it in r["funded"]:
        tag = " [must-fund]" if it["must_fund"] else ""
        print(f"  • {it['name']} — {it['cost']:g} (score/$ {it['score_per_cost']}){tag}")
    if r["unfunded"]:
        print(f"\n❌ Not funded ({len(r['unfunded'])}):")
        for it in r["unfunded"]:
            print(f"  • {it['name']} — {it['cost']:g} (score/$ {it['score_per_cost']})")
    if r["cut_line"]:
        c = r["cut_line"]
        print(f"\n✂ Cut line: {c['name']} just missed — needs {c['cost']:g} to fund.")


if __name__ == "__main__":
    main()
