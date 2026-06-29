#!/usr/bin/env python3
"""NPS / CSAT calculator for the csat-nps-analysis skill.

Computes NPS correctly (% promoters − % detractors, NOT an average) from a 0–10
rating distribution, or CSAT (% satisfied) from a 1–5 distribution. Pure standard
library, no network.

Usage
-----
  # NPS — pass 11 counts for ratings 0,1,2,...,10:
  python3 nps.py nps 2 1 1 3 4 8 10 20 35 40 60
  # CSAT — pass 5 counts for ratings 1,2,3,4,5 (satisfied = 4 and 5):
  python3 nps.py csat 2 3 10 40 55
  # add --json for machine-readable output
"""
import argparse
import json
import sys


def nps(counts):
    if len(counts) != 11:
        raise ValueError("NPS needs 11 counts (ratings 0..10).")
    total = sum(counts)
    if total == 0:
        raise ValueError("no responses")
    detr = sum(counts[0:7])      # 0–6
    passv = sum(counts[7:9])     # 7–8
    prom = sum(counts[9:11])     # 9–10
    score = round(100 * (prom - detr) / total)
    return {
        "metric": "NPS", "responses": total, "nps": score,
        "promoters_pct": round(100 * prom / total, 1),
        "passives_pct": round(100 * passv / total, 1),
        "detractors_pct": round(100 * detr / total, 1),
        "note": "NPS = %promoters (9-10) − %detractors (0-6). Range -100..+100.",
    }


def csat(counts):
    if len(counts) != 5:
        raise ValueError("CSAT needs 5 counts (ratings 1..5).")
    total = sum(counts)
    if total == 0:
        raise ValueError("no responses")
    satisfied = counts[3] + counts[4]   # 4 and 5
    return {
        "metric": "CSAT", "responses": total,
        "csat_pct": round(100 * satisfied / total, 1),
        "mean_rating": round(sum((i + 1) * c for i, c in enumerate(counts)) / total, 2),
        "note": "CSAT = % rating 4–5 (satisfied). Mean shown for reference only.",
    }


def main():
    ap = argparse.ArgumentParser(description="Compute NPS or CSAT from a rating distribution.")
    ap.add_argument("metric", choices=["nps", "csat"])
    ap.add_argument("counts", nargs="+", type=int, help="response counts per rating bucket")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        r = nps(a.counts) if a.metric == "nps" else csat(a.counts)
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if a.json:
        print(json.dumps(r, indent=2))
        return
    if r["metric"] == "NPS":
        print(f"NPS: {r['nps']:+d}   ({r['responses']} responses)")
        print(f"  Promoters {r['promoters_pct']}%  ·  Passives {r['passives_pct']}%  ·  Detractors {r['detractors_pct']}%")
    else:
        print(f"CSAT: {r['csat_pct']}% satisfied   ({r['responses']} responses, mean {r['mean_rating']}/5)")
    print(f"  {r['note']}")
    if r["responses"] < 30:
        print("  ⚠ Small sample (<30) — treat as directional, not a reliable trend.")


if __name__ == "__main__":
    main()
