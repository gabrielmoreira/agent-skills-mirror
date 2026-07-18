#!/usr/bin/env python3
"""Raise-vs-jump calculator for the raise-vs-jump skill.

Compares career earnings trajectories: staying (annual raises) vs jumping
(bigger bumps every few years, with a possible raise freeze after each jump).
Deterministic, stdlib only.

Usage
-----
    python3 raise_vs_jump.py --salary 120000
    python3 raise_vs_jump.py --salary 120000 --stay-raise 3.5 --jump-bump 18 --jump-every 3 --json
"""
from __future__ import annotations
import argparse, json, sys

def main(argv=None):
    ap = argparse.ArgumentParser(description="Cumulative earnings: staying vs jumping, over a horizon.")
    ap.add_argument("--salary", type=float, required=True, help="Current salary")
    ap.add_argument("--stay-raise", type=float, default=3.0, help="Annual raise pct if staying (default 3)")
    ap.add_argument("--jump-bump", type=float, default=15.0, help="Salary bump pct per jump (default 15)")
    ap.add_argument("--jump-every", type=int, default=3, help="Years between jumps (default 3)")
    ap.add_argument("--jump-year-raise", type=float, default=2.0, help="Annual raise pct between jumps (default 2 - jumpers often get smaller merit raises)")
    ap.add_argument("--horizon", type=int, default=10, help="Years (default 10)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    stay, jump = a.salary, a.salary
    cum_s = cum_j = 0.0
    rows, crossover = [], None
    for y in range(1, a.horizon + 1):
        stay *= 1 + a.stay_raise / 100
        if y % a.jump_every == 0:
            jump *= 1 + a.jump_bump / 100
        else:
            jump *= 1 + a.jump_year_raise / 100
        cum_s += stay
        cum_j += jump
        rows.append({"year": y, "stay": round(stay), "jump": round(jump),
                     "cum_stay": round(cum_s), "cum_jump": round(cum_j)})
        if crossover is None and cum_j > cum_s:
            crossover = y
    out = {"rows": rows, "crossover_year": crossover,
           "final_gap_cumulative": round(cum_j - cum_s),
           "final_salary_gap": round(rows[-1]["jump"] - rows[-1]["stay"]),
           "assumptions": {"stay_raise": a.stay_raise, "jump_bump": a.jump_bump,
                            "jump_every": a.jump_every, "jump_year_raise": a.jump_year_raise},
           "not_modeled": ["equity/vesting resets (often the real cost of jumping)", "promotion step-ups while staying",
                            "job-search risk and gaps", "seniority/pension accrual"]}
    if a.json:
        print(json.dumps(out, indent=1)); return 0
    print("year    stay-salary   jump-salary      cum stay      cum jump")
    for r in rows:
        print(f"{r['year']:>4} {r['stay']:>13,} {r['jump']:>13,} {r['cum_stay']:>13,} {r['cum_jump']:>13,}")
    print(f"cumulative crossover: {'year ' + str(crossover) if crossover else 'never in horizon'} · "
          f"salary gap at year {a.horizon}: {out['final_salary_gap']:+,} · cumulative: {out['final_gap_cumulative']:+,}")
    print("not modeled: vesting resets, promotions-if-you-stay, search risk — the numbers are one input to a decision, not the decision.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
