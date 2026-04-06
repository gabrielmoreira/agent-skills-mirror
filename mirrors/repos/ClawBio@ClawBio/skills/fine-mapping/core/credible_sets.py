"""
credible_sets.py — Credible set construction from PIPs or SuSiE alpha vectors.

Implements:
  - Per-signal credible sets from SuSiE alpha rows (greedy top-down)
  - Single credible set from ABF PIPs
  - Purity filter: minimum pairwise |r| within set (Wang et al. 2020 section 3.2)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional


def build_credible_sets_susie(
    alpha: np.ndarray,
    df: pd.DataFrame,
    R: Optional[np.ndarray],
    coverage: float = 0.95,
    min_purity: float = 0.5,
) -> list[dict]:
    """Build per-signal credible sets from SuSiE alpha matrix.

    Parameters
    ----------
    alpha : (L, p) posterior weight matrix from SuSiE
    df    : variants DataFrame (columns: rsid, chr, pos, z, pip)
    R     : (p, p) LD matrix (optional; used for purity filter)
    coverage : credible set coverage threshold (default 0.95)
    min_purity : minimum pairwise |r| threshold (default 0.5); sets below
                 threshold are flagged as "impure" rather than dropped

    Returns a list of credible set dicts, one per SuSiE signal l.
    """
    L = alpha.shape[0]
    credible_sets = []

    for l in range(L):
        a_l = alpha[l]
        cs = _greedy_credible_set(a_l, coverage)

        if len(cs) == 0:
            continue

        # Compute purity
        purity = _purity(cs, R) if R is not None else None

        # Collect variant info
        variants = _collect_variants(cs, df, a_l)
        lead = max(variants, key=lambda v: v["alpha"])

        credible_sets.append({
            "cs_id": f"L{l+1}",
            "signal_index": l,
            "size": len(cs),
            "coverage": float(a_l[cs].sum()),
            "lead_rsid": lead["rsid"],
            "lead_alpha": lead["alpha"],
            "purity": purity,
            "pure": purity is None or purity >= min_purity,
            "variants": variants,
        })

    return credible_sets


def build_credible_set_abf(
    pip: np.ndarray,
    df: pd.DataFrame,
    coverage: float = 0.95,
) -> list[dict]:
    """Build a single credible set from ABF PIPs.

    Returns a one-element list (same interface as susie version).
    """
    cs = _greedy_credible_set(pip, coverage)
    variants = _collect_variants(cs, df, pip)
    lead = max(variants, key=lambda v: v["pip"])

    return [{
        "cs_id": "ABF_CS1",
        "signal_index": 0,
        "size": len(cs),
        "coverage": float(pip[cs].sum()),
        "lead_rsid": lead["rsid"],
        "lead_alpha": lead["pip"],
        "purity": None,
        "pure": True,
        "variants": variants,
    }]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _greedy_credible_set(weights: np.ndarray, coverage: float) -> list[int]:
    """Greedily add highest-weight variants until cumulative weight >= coverage."""
    order = np.argsort(-weights)
    cumsum = 0.0
    cs = []
    for idx in order:
        cs.append(int(idx))
        cumsum += weights[idx]
        if cumsum >= coverage:
            break
    return cs


def _purity(cs: list[int], R: np.ndarray) -> float:
    """Minimum absolute pairwise LD r within the credible set.

    Per Wang et al. 2020 section 3.2, purity is the minimum (not mean)
    pairwise |r| across all pairs of variants in the credible set.
    Using mean instead of min can promote credible sets that span
    independent LD blocks.
    """
    if len(cs) < 2:
        return 1.0
    sub = R[np.ix_(cs, cs)]
    # Upper triangle (excluding diagonal)
    idx = np.triu_indices(len(cs), k=1)
    return float(np.min(np.abs(sub[idx])))


def _collect_variants(cs: list[int], df: pd.DataFrame, weights: np.ndarray) -> list[dict]:
    """Build variant dicts for credible set members."""
    variants = []
    for idx in cs:
        row = df.iloc[idx]
        v = {
            "rsid": str(row.get("rsid", f"var_{idx}")),
            "chr": str(row.get("chr", "?")),
            "pos": int(row["pos"]) if "pos" in df.columns and pd.notna(row.get("pos")) else None,
            "z": float(row["z"]),
            "pip": float(row.get("pip", weights[idx])),
            "alpha": float(weights[idx]),
        }
        if "p" in df.columns and pd.notna(row.get("p")):
            v["p"] = float(row["p"])
        if "maf" in df.columns and pd.notna(row.get("maf")):
            v["maf"] = float(row["maf"])
        variants.append(v)
    # Sort by alpha descending
    variants.sort(key=lambda x: -x["alpha"])
    return variants
