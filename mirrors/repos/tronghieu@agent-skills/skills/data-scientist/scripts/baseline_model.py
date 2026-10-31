#!/usr/bin/env python3
"""Leak-safe dummy + linear baselines for a tabular prediction task.

The mandatory floor for any Predict flow (non-negotiables #3 and #5). Runs a
dummy baseline and a linear model in cross-validated pipelines where all
preprocessing is fit inside training folds, chooses a split that respects
time/groups when told about them, and scans for mechanical leakage. Writes
baseline-report.md and baseline.json.

Usage:
    python baseline_model.py DATA --target COL [--task auto|classification|regression]
        [--time-col COL] [--group-col COL] [--drop COL ...] [--cv 5]
        [--sample N] [--out DIR]

Requires pandas and scikit-learn.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from sklearn.compose import ColumnTransformer
    from sklearn.dummy import DummyClassifier, DummyRegressor
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.model_selection import GroupKFold, KFold, StratifiedKFold, TimeSeriesSplit, cross_validate
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
except ImportError:
    sys.exit("scikit-learn is required: pip install scikit-learn")

SEED = 42
ID_UNIQUE_RATIO = 0.98
SINGLE_FEATURE_AUC_FLAG = 0.90
SINGLE_FEATURE_CORR_FLAG = 0.95
MAX_ONEHOT = 30


def load(path: Path, sample=None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in (".csv", ".txt"):
        df = pd.read_csv(path, low_memory=False)
    elif suffix == ".tsv":
        df = pd.read_csv(path, sep="\t", low_memory=False)
    elif suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        sys.exit(f"Unsupported file type: {suffix}")
    if sample and len(df) > sample:
        df = df.sample(sample, random_state=SEED)
    return df


def infer_task(y: pd.Series) -> str:
    if pd.api.types.is_float_dtype(y) and y.nunique() > 20:
        return "regression"
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 20:
        return "regression"
    return "classification"


def select_features(df, target, time_col, drop, notes):
    X = df.drop(columns=[target] + ([time_col] if time_col else []) + list(drop), errors="ignore")
    kept_num, kept_cat = [], []
    for c in X.columns:
        s = X[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            notes.append(f"dropped '{c}': datetime — engineer explicit features (tenure, weekday…) instead")
            continue
        if s.nunique(dropna=True) <= 1:
            notes.append(f"dropped '{c}': constant")
            continue
        if s.nunique(dropna=True) / max(len(s), 1) > ID_UNIQUE_RATIO and not pd.api.types.is_float_dtype(s):
            notes.append(f"dropped '{c}': id-like ({s.nunique()} unique values)")
            continue
        if pd.api.types.is_numeric_dtype(s):
            kept_num.append(c)
        else:
            if s.nunique(dropna=True) > 200:
                notes.append(f"dropped '{c}': high-cardinality text ({s.nunique()} unique) — needs deliberate encoding")
                continue
            kept_cat.append(c)
    return X[kept_num + kept_cat], kept_num, kept_cat


def make_preprocessor(num_cols, cat_cols):
    transformers = []
    if num_cols:
        transformers.append(("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), num_cols))
    if cat_cols:
        try:
            ohe = OneHotEncoder(handle_unknown="ignore", max_categories=MAX_ONEHOT, sparse_output=False)
        except TypeError:  # older sklearn
            ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
        transformers.append(("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", ohe),
        ]), cat_cols))
    return ColumnTransformer(transformers)


def choose_cv(task, y, n_splits, time_col, group_col, notes):
    if time_col:
        notes.append(f"split: TimeSeriesSplit({n_splits}) ordered by '{time_col}' — train on past, validate on future")
        return TimeSeriesSplit(n_splits=n_splits), None
    if group_col:
        notes.append(f"split: GroupKFold({n_splits}) by '{group_col}' — no entity straddles folds")
        return GroupKFold(n_splits=n_splits), group_col
    if task == "classification":
        notes.append(f"split: StratifiedKFold({n_splits}, shuffled) — rows assumed independent; pass --time-col/--group-col if not")
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=SEED), None
    notes.append(f"split: KFold({n_splits}, shuffled) — rows assumed independent; pass --time-col/--group-col if not")
    return KFold(n_splits=n_splits, shuffle=True, random_state=SEED), None


def scoring_for(task, y):
    if task == "classification":
        s = {"accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy", "f1_macro": "f1_macro"}
        if y.nunique() == 2:
            s.update({"roc_auc": "roc_auc", "pr_auc": "average_precision"})
        return s, ("pr_auc" if y.nunique() == 2 and y.value_counts(normalize=True).min() < 0.2
                   else "roc_auc" if y.nunique() == 2 else "f1_macro")
    return {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}, "mae"


def leakage_scan(X, y, num_cols, task):
    """Cheap mechanical probes; semantic leakage stays a judgment call."""
    import warnings as _warnings
    from sklearn.metrics import roc_auc_score

    flags = []
    dup = int(X.duplicated().sum())
    if dup:
        flags.append(f"{dup} duplicate feature-rows ({dup / len(X):.1%}) — memorization can straddle folds")
    binary = task == "classification" and y.nunique() == 2
    y_codes = np.asarray(pd.factorize(y)[0] if not pd.api.types.is_numeric_dtype(y) else y, dtype=float)

    def auc_flag(scores, label):
        try:
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                auc = roc_auc_score(y_codes, scores)
            auc = max(auc, 1 - auc)
            if not np.isnan(auc) and auc >= SINGLE_FEATURE_AUC_FLAG:
                flags.append(f"{label} reaches AUC {auc:.3f} — leakage suspect; trace its lineage")
        except ValueError:
            pass

    for c in X.columns:
        x = X[c]
        # Probe 1: the missingness pattern itself predicts the target
        # (classic leak: a field only filled in after the outcome happened)
        miss_rate = x.isna().mean()
        if 0.01 < miss_rate < 0.99:
            miss = x.isna().to_numpy(dtype=float)
            if binary:
                auc_flag(miss, f"missingness of '{c}' alone")
            elif task == "regression":
                r = abs(pd.Series(miss).corr(pd.Series(y_codes)))
                if pd.notna(r) and r >= SINGLE_FEATURE_CORR_FLAG:
                    flags.append(f"missingness of '{c}' correlates |r|={r:.3f} with target — leakage suspect")
        # Probe 2: the values predict the target near-perfectly
        if c not in num_cols:
            continue
        mask = x.notna().to_numpy()
        if mask.sum() < 30 or x[x.notna()].nunique() < 2:
            continue
        if binary:
            try:
                with _warnings.catch_warnings():
                    _warnings.simplefilter("ignore")
                    auc = roc_auc_score(y_codes[mask], x.to_numpy(dtype=float)[mask])
                auc = max(auc, 1 - auc)
                if not np.isnan(auc) and auc >= SINGLE_FEATURE_AUC_FLAG:
                    flags.append(f"'{c}' alone reaches AUC {auc:.3f} — leakage suspect; trace its lineage")
            except ValueError:
                pass
        elif task == "regression":
            r = abs(pd.Series(x.to_numpy(dtype=float)[mask]).corr(pd.Series(y_codes[mask])))
            if pd.notna(r) and r >= SINGLE_FEATURE_CORR_FLAG:
                flags.append(f"'{c}' alone correlates |r|={r:.3f} with target — leakage suspect; trace its lineage")
    return flags


def run_models(X, y, task, cv, groups, scoring):
    pre = make_preprocessor(*[list(c) for c in (X.select_dtypes(include=np.number).columns,
                                                X.select_dtypes(exclude=np.number).columns)])
    if task == "classification":
        models = {
            "dummy (most frequent)": DummyClassifier(strategy="most_frequent"),
            "logistic regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        }
        y_fit = pd.factorize(y)[0] if not pd.api.types.is_numeric_dtype(y) else y
    else:
        models = {"dummy (mean)": DummyRegressor(strategy="mean"), "ridge regression": Ridge(random_state=SEED)}
        y_fit = y
    results = {}
    for name, est in models.items():
        pipe = Pipeline([("pre", pre), ("model", est)])
        cvr = cross_validate(pipe, X, y_fit, cv=cv, scoring=scoring,
                             groups=groups, error_score="raise")
        results[name] = {
            m: {"mean": round(float(np.mean(cvr[f"test_{m}"])), 4),
                "std": round(float(np.std(cvr[f"test_{m}"])), 4)}
            for m in scoring
        }
    return results


def to_markdown(args, task, n, results, primary, notes, flags, target_summary):
    neg = {"mae", "rmse"}
    lines = [f"# Baseline Report — `{args.data.name}` → `{args.target}`", "",
             f"- **Task:** {task} · **Rows used:** {n:,} · **CV:** see split note below",
             f"- **Target:** {target_summary}", ""]
    lines += ["## Leakage scan (mechanical probes only)", ""]
    lines += [f"- 🚨 {f}" for f in flags] or ["- no mechanical flags — `checklists/leakage.md` (semantic checks) still applies"]
    lines += ["", "## Results (mean ± std across folds)", ""]
    metrics = list(next(iter(results.values())).keys())
    lines.append("| model | " + " | ".join(metrics) + " |")
    lines.append("|---|" + "---|" * len(metrics))
    for name, res in results.items():
        cells = []
        for m in metrics:
            v, s = res[m]["mean"], res[m]["std"]
            v = -v if m in neg else v
            cells.append(f"{v:.4f} ± {s:.4f}")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines += ["", f"**Primary metric:** `{primary}`. Any further model must beat the linear row",
              "by more than the fold std to justify its complexity, under this exact split.", ""]
    lines += ["## Setup notes", ""]
    lines += [f"- {x}" for x in notes]
    lines += ["", "## Next steps", "",
              "1. Investigate every 🚨 before building anything stronger.",
              "2. Log these rows as runs 0–1 in `experiment-log.md`.",
              "3. Climb the ladder per `references/modeling.md`; judge per `references/evaluation.md`."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("data", type=Path)
    ap.add_argument("--target", required=True)
    ap.add_argument("--task", choices=["auto", "classification", "regression"], default="auto")
    ap.add_argument("--time-col", default=None)
    ap.add_argument("--group-col", default=None)
    ap.add_argument("--drop", nargs="*", default=[])
    ap.add_argument("--cv", type=int, default=5)
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--out", type=Path, default=Path("."))
    args = ap.parse_args()

    df = load(args.data, args.sample)
    if args.target not in df.columns:
        sys.exit(f"Target '{args.target}' not found. Columns: {list(df.columns)[:30]}")
    n_missing_target = int(df[args.target].isna().sum())
    df = df.dropna(subset=[args.target])

    notes = []
    if n_missing_target:
        notes.append(f"dropped {n_missing_target} rows with missing target")
    if args.time_col:
        if args.time_col not in df.columns:
            sys.exit(f"--time-col '{args.time_col}' not found")
        df = df.sort_values(args.time_col).reset_index(drop=True)

    y = df[args.target]
    task = infer_task(y) if args.task == "auto" else args.task
    X, num_cols, cat_cols = select_features(df, args.target, args.time_col, args.drop, notes)
    if X.shape[1] == 0:
        sys.exit("No usable features left after selection — see notes; engineer features first.")
    notes.append(f"features: {len(num_cols)} numeric, {len(cat_cols)} categorical")

    groups_series = df[args.group_col] if args.group_col else None
    cv, group_key = choose_cv(task, y, args.cv, args.time_col, args.group_col, notes)
    scoring, primary = scoring_for(task, y)
    flags = leakage_scan(X, y, num_cols, task)
    results = run_models(X, y, task, cv, groups_series if group_key else None, scoring)

    if task == "classification":
        vc = y.astype(str).value_counts(normalize=True)
        target_summary = ", ".join(f"{k}: {v:.1%}" for k, v in vc.head(5).items())
    else:
        target_summary = f"mean {y.mean():.4g}, median {y.median():.4g}, range [{y.min():.4g}, {y.max():.4g}]"

    args.out.mkdir(parents=True, exist_ok=True)
    md = to_markdown(args, task, len(df), results, primary, notes, flags, target_summary)
    (args.out / "baseline-report.md").write_text(md)
    (args.out / "baseline.json").write_text(json.dumps({
        "data": str(args.data), "target": args.target, "task": task, "n_rows": len(df),
        "primary_metric": primary, "results": results, "leakage_flags": flags, "notes": notes,
    }, indent=2, default=str))

    print(f"Task: {task} · {len(df):,} rows · primary metric: {primary}")
    for name, res in results.items():
        p = res[primary]
        val = -p["mean"] if primary in ("mae", "rmse") else p["mean"]
        print(f"  {name}: {primary} = {val:.4f} ± {p['std']:.4f}")
    if flags:
        print(f"\n🚨 {len(flags)} leakage flag(s):")
        for f in flags:
            print(f"  - {f}")
    print(f"\nReports: {args.out / 'baseline-report.md'} , {args.out / 'baseline.json'}")


if __name__ == "__main__":
    main()
