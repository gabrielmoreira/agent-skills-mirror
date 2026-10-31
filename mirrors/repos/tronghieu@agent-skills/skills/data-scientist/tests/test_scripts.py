#!/usr/bin/env python3
"""Planted-defect tests for the bundled scripts.

Generates synthetic datasets with known, deliberate defects and asserts the
scripts catch every one of them. Doubles as an environment check: if this
passes, your pandas/scikit-learn setup is compatible with the skill.

Run:  python3 tests/test_scripts.py        (no pytest needed)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE = SKILL_DIR / "scripts" / "profile_data.py"
BASELINE = SKILL_DIR / "scripts" / "baseline_model.py"

PASSED = []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print(f"  ok: {name}")
    else:
        print(f"  FAIL: {name} {detail}")
        sys.exit(1)


def run(script, *args):
    proc = subprocess.run([sys.executable, str(script), *map(str, args)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        sys.exit(f"FAIL: {script.name} exited {proc.returncode}")
    return proc.stdout


def make_data(path: Path):
    """Synthetic churn data with planted defects, one per assertion below."""
    rng = np.random.default_rng(7)
    n = 2000
    tickets = rng.poisson(1.5, n)
    tenure = rng.exponential(12, n).round(1)
    p = 1 / (1 + np.exp(-(-3.4 + 0.4 * tickets - 0.04 * tenure)))
    churn = rng.binomial(1, p)  # minority ~5% → imbalance warning
    df = pd.DataFrame({
        "customer_id": np.arange(1, n + 1),                      # id-like
        "region": rng.choice(["North", "South", "unknown"], n),  # placeholder category
        "tenure_months": tenure,
        "support_tickets": tickets,
        "monthly_spend": rng.lognormal(4, 1, n).round(2),
        "const_col": "v1",                                       # constant
        "churn_score": churn + rng.normal(0, 0.01, n),           # value leak (single-feature AUC ≈ 1)
        "days_to_churn": np.where(churn == 1, rng.integers(1, 90, n), np.nan),  # missingness leak
        "signup_date_str": pd.to_datetime("2022-01-01")          # date stored as text
        + pd.to_timedelta(rng.integers(0, 900, n), unit="D"),
        "churn": churn,
    })
    df["signup_date_str"] = df["signup_date_str"].dt.strftime("%Y-%m-%d")
    df.loc[rng.choice(n, 300, replace=False), "monthly_spend"] = np.nan
    df["mostly_missing"] = np.where(rng.random(n) < 0.3, 1.0, np.nan)  # high-missing (~70%)
    df = pd.concat([df, df.head(25)], ignore_index=True)          # duplicate rows
    df.to_csv(path, index=False)
    return df


def test_profile(tmp, data):
    print("profile_data.py:")
    out = tmp / "profile"
    run(PROFILE, data, "--target", "churn", "--out", out)
    j = json.loads((out / "data-profile.json").read_text())
    warns = " | ".join(j["warnings"])

    check("reports written", (out / "data-profile.md").exists() and (out / "data-profile.json").exists())
    check("duplicate rows flagged", "duplicate rows" in warns)
    check("id column flagged", "customer_id" in warns)
    check("constant column flagged", "const_col" in warns)
    check("placeholder category flagged", "region" in warns and "unknown" in warns)
    check("high-missing column flagged", "mostly_missing" in warns)
    check("date-as-text flagged", "signup_date_str" in warns)
    check("class imbalance flagged", "imbalanced" in warns)
    top = j["correlations"]["target_corr"][0]
    check("leak-suspect correlation surfaces on top",
          top["feature"] == "churn_score" and abs(top["r"]) > 0.95, f"got {top}")


def test_profile_max_rows_json(tmp):
    print("profile_data.py (--max-rows on .json):")
    data = tmp / "rows.json"
    data.write_text('[{"value": 1}, {"value": 2}, {"value": 3}]')
    out = tmp / "json_rows"
    run(PROFILE, data, "--max-rows", 1, "--out", out)
    shape = json.loads((out / "data-profile.json").read_text())["shape"]
    check("--max-rows caps ordinary JSON", shape == [1, 1], f"got {shape}")


def test_baseline_classification(tmp, data, prevalence):
    print("baseline_model.py (classification):")
    out = tmp / "cls"
    run(BASELINE, data, "--target", "churn", "--drop", "signup_date_str", "--out", out)
    j = json.loads((out / "baseline.json").read_text())
    flags = " | ".join(j["leakage_flags"])

    check("task inferred as classification", j["task"] == "classification")
    check("value-leak feature flagged", "'churn_score' alone reaches AUC" in flags, flags)
    check("missingness-leak feature flagged", "missingness of 'days_to_churn'" in flags, flags)
    check("duplicate feature-rows flagged", "duplicate feature-rows" in flags, flags)
    check("imbalance → PR-AUC chosen as primary", j["primary_metric"] == "pr_auc")

    dummy = next(v for k, v in j["results"].items() if k.startswith("dummy"))
    linear = next(v for k, v in j["results"].items() if "logistic" in k)
    check("dummy PR-AUC ≈ prevalence (pipeline sanity)",
          abs(dummy["pr_auc"]["mean"] - prevalence) < 0.03, f"got {dummy['pr_auc']}")
    check("linear model runs and reports spread", linear["pr_auc"]["std"] >= 0)


def test_baseline_regression_time(tmp, data):
    print("baseline_model.py (regression + --time-col):")
    out = tmp / "reg"
    run(BASELINE, data, "--target", "monthly_spend", "--time-col", "signup_date_str",
        "--drop", "churn", "churn_score", "days_to_churn", "--out", out)
    j = json.loads((out / "baseline.json").read_text())

    check("task inferred as regression", j["task"] == "regression")
    check("rows with missing target dropped", j["n_rows"] < 2025)
    check("time-based split used", any("TimeSeriesSplit" in n for n in j["notes"]), j["notes"])
    check("MAE is primary metric", j["primary_metric"] == "mae")
    dummy = next(v for k, v in j["results"].items() if k.startswith("dummy"))
    check("dummy regression produces finite MAE", np.isfinite(dummy["mae"]["mean"]))


def test_regression_value_leak(tmp):
    print("baseline_model.py (regression value leak):")
    rng = np.random.default_rng(11)
    n = 800
    y = rng.lognormal(4, 1, n)
    df = pd.DataFrame({
        "x1": rng.normal(size=n),
        "x2": rng.choice(list("abc"), n),
        "y_echo": y * 0.99 + rng.normal(0, 0.5, n),  # near-copy of target
        "target": y,
    })
    data = tmp / "reg_leak.csv"
    df.to_csv(data, index=False)
    out = tmp / "reg_leak"
    run(BASELINE, data, "--target", "target", "--out", out)
    j = json.loads((out / "baseline.json").read_text())
    check("near-copy feature flagged by |r| probe",
          any("y_echo" in f for f in j["leakage_flags"]), j["leakage_flags"])


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        data = tmp / "synth.csv"
        df = make_data(data)
        test_profile(tmp, data)
        test_profile_max_rows_json(tmp)
        test_baseline_classification(tmp, data, prevalence=float(df["churn"].mean()))
        test_baseline_regression_time(tmp, data)
        test_regression_value_leak(tmp)
    print(f"\nAll {len(PASSED)} checks passed.")


if __name__ == "__main__":
    main()
