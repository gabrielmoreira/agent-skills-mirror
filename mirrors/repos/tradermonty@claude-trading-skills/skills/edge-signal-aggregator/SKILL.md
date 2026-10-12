---
name: edge-signal-aggregator
description: Aggregate and rank signals from multiple edge-finding skills (edge-candidate-agent, theme-detector, sector-analyst, institutional-flow-tracker) into a prioritized conviction dashboard with weighted scoring, deduplication, and contradiction detection.
---

# Edge Signal Aggregator

## Overview

Combine outputs from multiple upstream edge-finding skills into a single weighted conviction dashboard. This skill applies configurable signal weights, deduplicates overlapping themes, flags contradictions between skills, and ranks composite edge ideas by aggregate confidence score. The result is a prioritized edge shortlist with provenance links to each contributing skill.

## When to Use

- After running multiple edge-finding skills and wanting a unified view
- When consolidating signals from edge-candidate-agent, theme-detector, sector-analyst, and institutional-flow-tracker
- Before making portfolio allocation decisions based on multiple signal sources
- To identify contradictions between different analysis approaches
- When prioritizing which edge ideas deserve deeper research

## Prerequisites

- Python 3.9+
- No API keys required (processes local JSON/YAML files from other skills)
- Dependencies: `pyyaml` (standard in most environments)

## Workflow

### Step 1: Gather Upstream Skill Outputs

Collect output files from the upstream skills you want to aggregate:
- `reports/edge_candidate_*.json` from edge-candidate-agent
- `reports/edge_concepts_*.yaml` from edge-concept-synthesizer
- `reports/theme_detector_*.json` from theme-detector
- `reports/sector_analyst_*.json` from sector-analyst
- `reports/institutional_flow_*.json` from institutional-flow-tracker
- `reports/edge_hints_*.yaml` from edge-hint-extractor

### Step 2: Run Signal Aggregation

Execute the aggregator script with paths to upstream outputs:

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --edge-concepts reports/edge_concepts_*.yaml \
  --themes reports/theme_detector_*.json \
  --sectors reports/sector_analyst_*.json \
  --institutional reports/institutional_flow_*.json \
  --hints reports/edge_hints_*.yaml \
  --output-dir reports/
```

Optional: Use a custom weights configuration:

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --weights-config skills/edge-signal-aggregator/assets/custom_weights.yaml \
  --output-dir reports/
```

### Step 3: Review Aggregated Dashboard

Open the generated report to review:
1. **Ranked Edge Ideas** - Sorted by composite conviction score
2. **Signal Provenance** - Which skills contributed to each idea
3. **Contradictions** - Conflicting signals flagged for manual review
4. **Deduplication Log** - Merged overlapping themes

### Step 4: Act on High-Conviction Signals

Filter the shortlist by minimum conviction threshold:

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --min-conviction 0.7 \
  --output-dir reports/
```

## Output Format

### JSON Report

```json
{
  "schema_version": "1.1",
  "generated_at": "2026-03-02T07:00:00Z",
  "config": {
    "weights": {
      "edge_candidate_agent": 0.25,
      "edge_concept_synthesizer": 0.20,
      "theme_detector": 0.15,
      "sector_analyst": 0.15,
      "institutional_flow_tracker": 0.15,
      "edge_hint_extractor": 0.10
    },
    "min_conviction": 0.5,
    "dedup_similarity_threshold": 0.8
  },
  "summary": {
    "total_input_signals": 42,
    "unique_signals_after_dedup": 28,
    "contradictions_found": 3,
    "signals_above_threshold": 12,
    "invalid_signals_dropped": 2,
    "idempotency_check": {
      "total_input_signals": 42,
      "unique_evidence_ids": 28,
      "duplicate_copies_merged": 14,
      "independent_units_total": 30
    }
  },
  "ranked_signals": [
    {
      "rank": 1,
      "signal_id": "sig_001",
      "title": "AI Infrastructure Capex Acceleration",
      "composite_score": 0.87,
      "evidence_id": "ticket_2026-03-01_001",
      "score_scale_assumed": false,
      "contributing_skills": [
        {
          "skill": "edge_candidate_agent",
          "signal_ref": "ticket_2026-03-01_001",
          "raw_score": 0.92,
          "weighted_contribution": 0.23,
          "evidence_id": "ticket_2026-03-01_001",
          "event_fingerprint": "sha1-of-title-and-tickers"
        },
        {
          "skill": "theme_detector",
          "signal_ref": "theme_ai_infra",
          "raw_score": 0.85,
          "weighted_contribution": 0.13
        }
      ],
      "tickers": ["NVDA", "AMD", "AVGO"],
      "direction": "LONG",
      "time_horizon": "3-6 months",
      "confidence_breakdown": {
        "multi_skill_agreement": 0.30,
        "signal_strength": 0.35,
        "recency": 0.22
      }
    }
  ],
  "contradictions": [
    {
      "contradiction_id": "contra_001",
      "description": "Conflicting sector view on Energy",
      "skill_a": {
        "skill": "sector_analyst",
        "signal": "Energy sector bearish rotation",
        "direction": "SHORT"
      },
      "skill_b": {
        "skill": "institutional_flow_tracker",
        "signal": "Heavy institutional buying in XLE",
        "direction": "LONG"
      },
      "resolution_hint": "Check timeframe mismatch (short-term vs long-term)"
    }
  ],
  "deduplication_log": [
    {
      "merged_into": "edge_candidate_agent:ticket_001",
      "duplicates_removed": ["edge_candidate_agent:ticket_001@reports/ticket_001.json"],
      "similarity_score": 1.0,
      "reason": "same evidence re-ingested",
      "selection_rule": "newest timestamp wins; ties, missing, or unparsable timestamps keep the highest raw_score, then a stable key",
      "retained_copy": {
        "signal_ref": "ticket_001",
        "source_file": "reports/rerun.json",
        "raw_score": 0.5,
        "timestamp": "2026-10-10T00:00:00Z"
      },
      "discarded_copies": [
        {
          "signal_ref": "ticket_001",
          "source_file": "reports/ticket_001.json",
          "raw_score": 0.9,
          "timestamp": "2026-10-09T00:00:00Z"
        }
      ]
    },
    {
      "merged_into": "edge_candidate_agent:ticket_001",
      "duplicates_removed": ["theme_detector:ai_compute"],
      "similarity_score": 0.9
    }
  ],
  "invalid_signals": [
    {
      "skill": "theme_detector",
      "signal_ref": "broken_theme",
      "title": "Theme with a corrupted score",
      "reason": "non_finite",
      "declared_scale": null,
      "raw_value_repr": "nan",
      "source_file": "reports/theme_detector_2026-03-01.json"
    }
  ],
  "scale_assumptions_report": [
    {
      "skill": "theme_detector",
      "signal_ref": "ai_compute",
      "value": 7.2,
      "normalized_value": 0.072,
      "assumed_scale": "0-100",
      "source_file": "reports/theme_detector.json"
    }
  ]
}
```

### Producer contract (optional keys, schema 1.1)

Each producer item (ticket, concept, theme, sector row, flow, hint) MAY carry:

- `evidence_id` — a stable identifier for the underlying evidence. Without this key a
  deterministic fallback is derived from skill, signal reference, title, tickers, and direction
  (timestamps are excluded so refreshed timestamps cannot forge a new identity). Re-ingesting
  the same evidence (same skill + `evidence_id`) never adds a bonus: all copies collapse into
  one. When the copies differ, the **newest observation wins**: the copy with the latest
  timestamp, compared as parsed timezone-aware datetimes (date-only and naive values are read
  as UTC), becomes the retained score. Equal, missing, or unparsable timestamps fall back to
  the highest `raw_score`, then a stable key (`signal_ref`, `source_file`), so ingestion order
  never changes the result. Only ISO-8601 strings (or `YYYY-MM-DD`) are ordered; epoch numbers and compact forms such as `20261010` count as missing timestamps. Remaining full ties are broken by title, direction, tickers, and a canonical dump of the signal. A copy that carries a score older than the retained one is
  discarded, so a newer, lower score replaces an older, higher one. The discarded copies'
  scores and timestamps are listed in `deduplication_log[].discarded_copies`. Identical
  copies leave the score unchanged.
- `score_scale` — `"0-1"` or `"0-100"`, declaring the raw score's scale. Declared scales are
  enforced strictly: NaN/infinity/negative/out-of-range values are rejected into
  `invalid_signals`, never converted into maximum confidence. A present-but-unparsable
  declaration (`""`, `"foo"`) is also rejected (`missing_scale`). If the key is absent, values
  in (1, 100] are divided by 100 and flagged `score_scale_assumed: true` plus a
  `scale_assumptions_report` entry (`value` is the original input, `normalized_value` the
  0-1 score used); values > 100 are rejected.

### Agreement rule (Issue #510)

Agreement bonuses fire on `agreement_tier = min(distinct evidence_ids, distinct
event_fingerprints, distinct skills)` among a merged signal's contributors: tier 2 earns the
two-skills bonus, tier 3+ the three-plus bonus. Re-ingested duplicates earn nothing; the same
event restated by another skill (identical normalized title + tickers) counts once. Known
limitation: the event fingerprint is vocabulary-based, so paraphrased restatements with disjoint
word sets still earn the agreement bonus — treat cross-skill paraphrases with independent
verification. Merged duplicates no longer earn a per-copy bonus (`merge_bonus_per_duplicate`
is deprecated and ignored).

### Markdown Report

The markdown report provides a human-readable dashboard:

```markdown
# Edge Signal Aggregator Dashboard
**Generated:** 2026-03-02 07:00 UTC

## Summary
- Total Input Signals: 42
- Unique After Dedup: 28
- Contradictions: 3
- High Conviction (>=0.5): 12

## Top 10 Edge Ideas by Conviction

### 1. AI Infrastructure Capex Acceleration (Score: 0.87)
- **Tickers:** NVDA, AMD, AVGO
- **Direction:** LONG | **Horizon:** 3-6 months
- **Contributing Skills:**
  - edge-candidate-agent: 0.92 (ticket_2026-03-01_001)
  - theme-detector: 0.85 (theme_ai_infra)
- **Confidence Breakdown:** Agreement 0.30 | Strength 0.35 | Recency 0.22

...

## Contradictions Requiring Review

### Energy Sector Conflict
- **sector-analyst:** Bearish rotation (SHORT)
- **institutional-flow-tracker:** Heavy buying XLE (LONG)
- **Hint:** Check timeframe mismatch

## Deduplication Summary
- 14 signals merged into 8 unique themes
- Average similarity of merged signals: 0.89
```

Reports are saved to `reports/` with filenames:
- `edge_signal_aggregator_YYYY-MM-DD_HHMMSS.json`
- `edge_signal_aggregator_YYYY-MM-DD_HHMMSS.md`

## Resources

- `scripts/aggregate_signals.py` -- Main aggregation script with CLI interface
- `references/signal-weighting-framework.md` -- Rationale for default weights and scoring methodology
- `assets/default_weights.yaml` -- Default skill weights configuration

## Key Principles

1. **Provenance Tracking** -- Every aggregated signal links back to its source skill and original reference
2. **Contradiction Transparency** -- Conflicting signals are flagged, not hidden, to enable informed decisions
3. **Configurable Weights** -- Default weights reflect typical reliability but can be customized per user
4. **Deduplication Without Loss** -- Merged signals retain references to all original sources
5. **Actionable Output** -- Ranked list with clear tickers, direction, and time horizon for each idea
6. **Idempotent Aggregation** -- Re-ingesting the same evidence never inflates scores; agreement credit requires distinct skills AND distinct events
7. **Strict Score Validation** -- NaN/infinity, negative, and out-of-range scores are rejected and reported, never converted into maximum confidence
