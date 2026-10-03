---
version: "1.0.0"
date: 2026-07-15
---

# REFINE Natural-Language Adjustment Mappings

Reference for PHASE 2 — REFINE. When the user types a natural-language adjustment ("make it
warmer," "drop the humor"), apply it via these mappings, regenerate the sample with the change
held single-axis, and re-present. When ambiguous, apply the primary mapping and narrate the
change so the user can correct.

| User says | Dimension change | Also consider |
|---|---|---|
| "warmer" | Warmth: increase one position | Empathy: increase one |
| "cooler" / "less warm" | Warmth: decrease one | Empathy: decrease one |
| "more formal" | Formality: increase one | Register: shift toward Advisor |
| "less formal" / "more casual" | Formality: decrease one | |
| "shorter" / "more concise" | Brevity: decrease one (toward Terse) | |
| "longer" / "more detail" | Brevity: increase one (toward Expansive) | |
| "more personality" | Personality Intensity: increase one | Humor: enable if None |
| "less personality" / "more neutral" | Personality Intensity: decrease one | |
| "less robotic" | Warmth: increase + Personality Intensity: increase | |
| "more professional" | Formality: Professional, Humor: None or Dry | Personality Intensity: Moderate |
| "friendlier" | Warmth: increase + Emotional Coloring: Encouraging | Empathy: increase |
| "more direct" / "blunter" | Emotional Coloring: toward Blunt, Brevity: toward Terse | Empathy: toward Minimal |
| "more encouraging" | Emotional Coloring: Encouraging | Empathy: Moderate or Attuned |
| "funnier" | Humor: increase one | Personality Intensity: increase if Reserved |
| "no humor" | Humor: None | |
| "more emoji" | Emoji: increase one | |
| "less emoji" | Emoji: decrease one | |
