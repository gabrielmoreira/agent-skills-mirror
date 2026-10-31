#!/usr/bin/env python3
"""Profile a tabular dataset: structure, quality, warnings.

First contact with any dataset (non-negotiable #1). Writes data-profile.md
(workspace artifact) and data-profile.json (machine-readable), prints a
summary with warnings to stdout.

Usage:
    python profile_data.py DATA [--target COL] [--out DIR] [--max-rows N]

Supports .csv, .tsv, .parquet, .xlsx/.xls, .json/.jsonl. Requires pandas.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HIGH_CORR = 0.85
LEAK_SUSPECT_CORR = 0.95
ID_UNIQUE_RATIO = 0.98
IMBALANCE_MINORITY = 0.10
HIGH_MISSING = 0.40
PLACEHOLDER_NUMERIC = {0, -1, 999, 9999, -999}
PLACEHOLDER_TEXT = {"", "n/a", "na", "none", "null", "unknown", "-", "?", "missing"}


def load(path: Path, max_rows=None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    try:
        if suffix in (".csv", ".txt"):
            return pd.read_csv(path, low_memory=False, nrows=max_rows)
        if suffix == ".tsv":
            return pd.read_csv(path, sep="\t", low_memory=False, nrows=max_rows)
        if suffix in (".parquet", ".json"):
            # No row limit at read time: --max-rows caps profiling, not parsing memory.
            df = pd.read_parquet(path) if suffix == ".parquet" else pd.read_json(path)
            return df.head(max_rows) if max_rows else df
        if suffix in (".xlsx", ".xls"):
            return pd.read_excel(path, nrows=max_rows)
        if suffix == ".jsonl":
            return pd.read_json(path, lines=True, nrows=max_rows)
    except ImportError as e:
        sys.exit(f"Missing engine for {suffix}: {e}. Install pyarrow (parquet) or openpyxl (xlsx).")
    sys.exit(f"Unsupported file type: {suffix}")


def classify_column(s: pd.Series) -> str:
    n = len(s)
    nunique = s.nunique(dropna=True)
    if nunique <= 1:
        return "constant"
    if pd.api.types.is_bool_dtype(s) or (nunique == 2 and set(s.dropna().unique()) <= {0, 1, True, False}):
        return "binary"
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_numeric_dtype(s):
        if pd.api.types.is_integer_dtype(s) and nunique / max(n, 1) > ID_UNIQUE_RATIO:
            return "id-like (numeric)"
        return "numeric"
    # object columns: try datetime, then judge cardinality
    sample = s.dropna().astype(str).head(500)
    if sample.size:
        try:
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        except (TypeError, ValueError):
            parsed = pd.to_datetime(sample, errors="coerce")
        if parsed.notna().mean() > 0.9:
            return "datetime (as text)"
    if nunique / max(n, 1) > ID_UNIQUE_RATIO:
        return "id-like (text)"
    if nunique > 50 and sample.size and sample.str.len().mean() > 30:
        return "text"
    return "categorical"


def profile_column(s: pd.Series, kind: str) -> dict:
    n = len(s)
    info = {
        "kind": kind,
        "missing_pct": round(float(s.isna().mean()) * 100, 2),
        "n_unique": int(s.nunique(dropna=True)),
    }
    nn = s.dropna()
    if kind in ("numeric", "binary") and pd.api.types.is_numeric_dtype(s) and nn.size:
        q = nn.quantile([0, 0.25, 0.5, 0.75, 1])
        info.update(
            mean=round(float(nn.mean()), 4), std=round(float(nn.std()), 4),
            min=round(float(q.iloc[0]), 4), p25=round(float(q.iloc[1]), 4),
            median=round(float(q.iloc[2]), 4), p75=round(float(q.iloc[3]), 4),
            max=round(float(q.iloc[4]), 4),
            skew=round(float(nn.skew()), 2) if nn.size > 2 else None,
            n_zeros=int((nn == 0).sum()), n_negative=int((nn < 0).sum()),
        )
        iqr = q.iloc[3] - q.iloc[1]
        if iqr > 0:
            outliers = ((nn < q.iloc[1] - 3 * iqr) | (nn > q.iloc[3] + 3 * iqr)).sum()
            info["n_outliers_3iqr"] = int(outliers)
    elif kind in ("categorical", "binary", "id-like (text)", "text"):
        top = nn.astype(str).value_counts().head(5)
        info["top_values"] = {str(k): int(v) for k, v in top.items()}
    elif "datetime" in kind and nn.size:
        try:
            dt = pd.to_datetime(nn, errors="coerce", format="mixed") if nn.dtype == object else nn
            info["min_date"] = str(dt.min())
            info["max_date"] = str(dt.max())
        except (TypeError, ValueError):
            pass
    return info


def build_warnings(df, cols, target=None):
    w = []
    n = len(df)
    dup = int(df.duplicated().sum())
    if dup:
        w.append(f"{dup} exact duplicate rows ({dup / n:.1%}) — confirm whether real or extract artifact")
    for name, info in cols.items():
        kind = info["kind"]
        if kind == "constant":
            w.append(f"'{name}' is constant — carries no information")
        if kind.startswith("id-like"):
            w.append(f"'{name}' looks like an identifier ({info['n_unique']} unique) — exclude from features; if numeric it can silently encode time")
        if info["missing_pct"] > HIGH_MISSING * 100:
            w.append(f"'{name}' is {info['missing_pct']:.0f}% missing — investigate mechanism before use")
        if kind == "datetime (as text)":
            w.append(f"'{name}' holds dates stored as text — parse explicitly (timezone? format?)")
        if kind == "numeric":
            nn = df[name].dropna()
            hits = [p for p in PLACEHOLDER_NUMERIC if p != 0 and nn.size and (nn == p).mean() > 0.01]
            if hits:
                w.append(f"'{name}' has frequent placeholder-looking values {hits} — real or coded missing?")
        if kind in ("categorical",):
            vals = {str(v).strip().lower() for v in df[name].dropna().astype(str).unique()[:200]}
            ph = vals & PLACEHOLDER_TEXT
            if ph:
                w.append(f"'{name}' contains placeholder categories {sorted(ph)} — recode to missing?")
    if target and target in df.columns:
        t = df[target]
        if t.isna().any():
            w.append(f"target '{target}' has {int(t.isna().sum())} missing values — those rows can't be used for supervised learning")
        if cols[target]["kind"] in ("binary", "categorical"):
            vc = t.value_counts(normalize=True)
            if vc.size >= 2 and vc.iloc[-1] < IMBALANCE_MINORITY:
                w.append(f"target '{target}' is imbalanced (minority class {vc.iloc[-1]:.1%}) — use PR-AUC/class weights, stratified splits")
    return w


def correlations(df, cols, target=None):
    num = [c for c, i in cols.items() if i["kind"] == "numeric" and c != target]
    out = {"high_pairs": [], "target_corr": []}
    if len(num) >= 2:
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = df[num].corr(numeric_only=True)
        for i, a in enumerate(num):
            for b in num[i + 1:]:
                r = corr.loc[a, b]
                if pd.notna(r) and abs(r) >= HIGH_CORR:
                    out["high_pairs"].append({"a": a, "b": b, "r": round(float(r), 3)})
    if target and target in df.columns:
        t = df[target]
        if not pd.api.types.is_numeric_dtype(t):
            codes, _ = pd.factorize(t)
            t = pd.Series(codes, index=df.index).replace(-1, np.nan)
        if t.nunique() > 1:
            with np.errstate(invalid="ignore", divide="ignore"):
                for c in num:
                    r = df[c].corr(t)
                    if pd.notna(r):
                        out["target_corr"].append({"feature": c, "r": round(float(r), 3)})
            out["target_corr"].sort(key=lambda d: -abs(d["r"]))
            out["target_corr"] = out["target_corr"][:15]
    return out


def to_markdown(path, df, cols, warns, corrs, target):
    n, m = df.shape
    lines = [f"# Data Profile — `{path.name}`", ""]
    lines += [f"- **Rows × columns:** {n:,} × {m}",
              f"- **Exact duplicate rows:** {int(df.duplicated().sum()):,}",
              f"- **Memory:** {df.memory_usage(deep=True).sum() / 1e6:.1f} MB",
              f"- **Target:** {target or '(none given)'}", ""]
    lines += ["## Warnings", ""]
    lines += [f"- ⚠️ {w}" for w in warns] or ["- none detected (mechanical checks only — the data-quality checklist still applies)"]
    lines += ["", "## Columns", "", "| column | kind | missing % | unique | summary |", "|---|---|---|---|---|"]
    for name, i in cols.items():
        if "mean" in i:
            summ = f"mean {i['mean']}, median {i['median']}, range [{i['min']}, {i['max']}], skew {i.get('skew')}"
        elif "top_values" in i:
            top = list(i["top_values"].items())[:3]
            summ = ", ".join(f"{k} ({v})" for k, v in top)
        elif "min_date" in i:
            summ = f"{i['min_date']} → {i['max_date']}"
        else:
            summ = ""
        lines.append(f"| {name} | {i['kind']} | {i['missing_pct']} | {i['n_unique']:,} | {summ} |")
    if corrs["high_pairs"]:
        lines += ["", "## Highly correlated pairs (|r| ≥ 0.85)", ""]
        lines += [f"- {p['a']} ↔ {p['b']}: r = {p['r']}" for p in corrs["high_pairs"][:20]]
    if corrs["target_corr"]:
        lines += ["", f"## Numeric correlation with target `{target}`", ""]
        for p in corrs["target_corr"]:
            flag = "  ← **leakage suspect**" if abs(p["r"]) >= LEAK_SUSPECT_CORR else ""
            lines.append(f"- {p['feature']}: r = {p['r']}{flag}")
    lines += ["", "## Next steps", "",
              "1. Work through `checklists/data-quality.md` — this profile covers only the mechanical layer.",
              "2. Investigate every warning above; each is a finding or a fix.",
              "3. Proceed to directed EDA (`references/eda.md`)."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("data", type=Path)
    ap.add_argument("--target", default=None)
    ap.add_argument("--out", type=Path, default=Path("."))
    ap.add_argument("--max-rows", type=int, default=None)
    args = ap.parse_args()

    df = load(args.data, args.max_rows)
    if args.target and args.target not in df.columns:
        sys.exit(f"Target '{args.target}' not in columns: {list(df.columns)[:30]}...")

    cols = {c: profile_column(df[c], classify_column(df[c])) for c in df.columns}
    warns = build_warnings(df, cols, args.target)
    corrs = correlations(df, cols, args.target)

    args.out.mkdir(parents=True, exist_ok=True)
    md = to_markdown(args.data, df, cols, warns, corrs, args.target)
    (args.out / "data-profile.md").write_text(md)
    payload = {"file": str(args.data), "shape": list(df.shape), "columns": cols,
               "warnings": warns, "correlations": corrs, "target": args.target}
    (args.out / "data-profile.json").write_text(json.dumps(payload, indent=2, default=str))

    print(f"Profiled {args.data.name}: {df.shape[0]:,} rows x {df.shape[1]} cols")
    print(f"Reports: {args.out / 'data-profile.md'} , {args.out / 'data-profile.json'}")
    print(f"\n{len(warns)} warning(s):")
    for w in warns:
        print(f"  - {w}")


if __name__ == "__main__":
    main()
