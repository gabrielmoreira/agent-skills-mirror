#!/usr/bin/env python3
"""Car total-cost-of-ownership calculator for the car-tco skill.

Compares buy-new / buy-used / lease / keep-current over a horizon: purchase or
payments, depreciation, insurance, maintenance ramp, fuel or charging.
Deterministic, stdlib only. Assumptions are flags with printed defaults.

Usage
-----
    python3 car_tco.py --new-price 38000 --used-price 24000 --lease-month 420 --horizon 8
    python3 car_tco.py --new-price 38000 --keep-value 9000 --keep-maint 1800 --json
"""
from __future__ import annotations
import argparse, json, sys

def depreciate(value, years, first=0.20, later=0.10):
    v = value
    for y in range(years):
        v *= (1 - (first if y == 0 else later))
    return v

def main(argv=None):
    ap = argparse.ArgumentParser(description="Total cost of ownership: new vs used vs lease vs keep.")
    ap.add_argument("--horizon", type=int, default=8, help="Years (default 8)")
    ap.add_argument("--miles", type=float, default=12000, help="Miles/yr (default 12000)")
    ap.add_argument("--fuel-cost-mile", type=float, default=0.14, help="Fuel/energy $ per mile (default 0.14)")
    ap.add_argument("--insurance", type=float, default=1700, help="Insurance $/yr baseline (default 1700)")
    ap.add_argument("--new-price", type=float)
    ap.add_argument("--used-price", type=float, help="Price of a ~3-yr-old equivalent")
    ap.add_argument("--lease-month", type=float, help="Lease payment (re-leased at each term end)")
    ap.add_argument("--lease-driveoff", type=float, default=2500)
    ap.add_argument("--lease-term", type=int, default=3, help="Lease years per cycle (default 3)")
    ap.add_argument("--keep-value", type=float, help="Current car's value today")
    ap.add_argument("--keep-maint", type=float, default=1500, help="Current car maintenance $/yr (default 1500, ramps 8%%/yr)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    H = a.horizon
    fuel = a.miles * a.fuel_cost_mile * H
    scenarios = {}
    def maint_ramp(start, years, ramp=0.08, offset=0):
        return sum(start * (1 + ramp) ** (y + offset) for y in range(years))
    if a.new_price:
        resale = depreciate(a.new_price, H)
        scenarios["buy_new"] = a.new_price - resale + maint_ramp(600, H) + a.insurance * H + fuel
    if a.used_price:
        resale = depreciate(a.used_price, H, first=0.12, later=0.09)
        scenarios["buy_used"] = a.used_price - resale + maint_ramp(1000, H, offset=3) + a.insurance * 0.85 * H + fuel
    if a.lease_month:
        cycles = -(-H // a.lease_term)
        scenarios["lease_forever"] = (a.lease_month * 12 * H) + a.lease_driveoff * cycles + a.insurance * 1.05 * H + fuel
    if a.keep_value is not None:
        resale = depreciate(a.keep_value, H, first=0.12, later=0.10)
        scenarios["keep_current"] = a.keep_value - resale + maint_ramp(a.keep_maint, H) + a.insurance * 0.8 * H + fuel

    if not scenarios:
        ap.error("give at least one of --new-price --used-price --lease-month --keep-value")
    ranked = sorted(scenarios.items(), key=lambda kv: kv[1])
    out = {"horizon_years": H, "totals": {k: round(v) for k, v in scenarios.items()},
           "per_month": {k: round(v / H / 12) for k, v in scenarios.items()},
           "cheapest": ranked[0][0],
           "assumptions": {"depreciation": "20% yr1 then 10%/yr new; gentler used", "maintenance ramp": "8%/yr",
                            "insurance": a.insurance, "fuel_per_mile": a.fuel_cost_mile},
           "not_modeled": ["financing interest (add via loan calc)", "taxes/fees by jurisdiction", "reliability variance"]}
    if a.json:
        print(json.dumps(out, indent=1)); return 0
    print(f"total cost of ownership over {H} years ({a.miles:,.0f} mi/yr):")
    for k, v in ranked:
        print(f"  {k:<13} {v:>10,.0f}   ({v/H/12:,.0f}/mo)")
    print(f"cheapest on these assumptions: {ranked[0][0]} — margins under ~10% are noise, not verdicts.")
    print("not modeled: financing interest, jurisdiction taxes, reliability luck. A model, not a verdict.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
