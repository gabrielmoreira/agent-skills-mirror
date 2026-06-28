#!/usr/bin/env python3
"""A/B significance calculator for the experiment-readout skill.

Two-proportion z-test for a conversion experiment: computes each rate, absolute &
relative lift, the z-statistic, a two-sided p-value, and a 95% confidence interval
on the difference in proportions. Pure standard library (math only) — no scipy, no
network. The normal CDF is implemented via math.erf.

Usage
-----
  python3 ab_significance.py <control_n> <control_conv> <treat_n> <treat_conv> [--alpha 0.05] [--json]

Example
-------
  python3 ab_significance.py 10000 800 10000 880
"""
import argparse
import json
import math
import sys


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def z_for_alpha(alpha):
    # Two-sided critical z via a small bisection on the inverse CDF (no scipy).
    target = 1 - alpha / 2
    lo, hi = 0.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if norm_cdf(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def analyse(cn, cc, tn, tc, alpha=0.05):
    if cn <= 0 or tn <= 0:
        raise ValueError("sample sizes must be > 0")
    if not (0 <= cc <= cn and 0 <= tc <= tn):
        raise ValueError("conversions must be between 0 and n")
    p1, p2 = cc / cn, tc / tn
    abs_lift = p2 - p1
    rel_lift = (abs_lift / p1) if p1 > 0 else None

    # Pooled SE for the z-test (H0: p1 == p2).
    pool = (cc + tc) / (cn + tn)
    se_pool = math.sqrt(pool * (1 - pool) * (1 / cn + 1 / tn))
    z = abs_lift / se_pool if se_pool > 0 else 0.0
    p_value = 2 * (1 - norm_cdf(abs(z)))

    # Unpooled SE for the CI on the difference.
    se_diff = math.sqrt(p1 * (1 - p1) / cn + p2 * (1 - p2) / tn)
    zc = z_for_alpha(alpha)
    ci = (abs_lift - zc * se_diff, abs_lift + zc * se_diff)

    return {
        "control_rate": round(p1, 5),
        "treatment_rate": round(p2, 5),
        "absolute_lift": round(abs_lift, 5),
        "relative_lift_pct": round(rel_lift * 100, 2) if rel_lift is not None else None,
        "z": round(z, 3),
        "p_value": round(p_value, 5),
        "ci_95_abs": [round(ci[0], 5), round(ci[1], 5)],
        "significant": p_value < alpha,
        "alpha": alpha,
    }


def main():
    ap = argparse.ArgumentParser(description="Two-proportion z-test for an A/B test.")
    ap.add_argument("control_n", type=int)
    ap.add_argument("control_conv", type=int)
    ap.add_argument("treat_n", type=int)
    ap.add_argument("treat_conv", type=int)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        r = analyse(a.control_n, a.control_conv, a.treat_n, a.treat_conv, a.alpha)
    except Exception as e:  # noqa: BLE001
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if a.json:
        print(json.dumps(r, indent=2))
        return

    print(f"Control:   {r['control_rate']*100:.2f}%  ({a.control_conv}/{a.control_n})")
    print(f"Treatment: {r['treatment_rate']*100:.2f}%  ({a.treat_conv}/{a.treat_n})")
    rl = f"{r['relative_lift_pct']:+.2f}%" if r['relative_lift_pct'] is not None else "n/a"
    print(f"Lift:      {r['absolute_lift']*100:+.2f}pp  ({rl} relative)")
    print(f"95% CI:    [{r['ci_95_abs'][0]*100:+.2f}pp, {r['ci_95_abs'][1]*100:+.2f}pp]")
    print(f"p-value:   {r['p_value']:.4f}  (z={r['z']})")
    if r["significant"]:
        lo = r["ci_95_abs"][0]
        flag = "" if lo > 0 else "  ⚠ CI crosses 0 despite p<alpha — check inputs"
        print(f"\n🟢 Significant at α={r['alpha']} — but confirm the lift is big enough to matter.{flag}")
    else:
        print(f"\n🔴 NOT significant at α={r['alpha']} — no detectable difference. Don't ship on this alone.")


if __name__ == "__main__":
    main()
