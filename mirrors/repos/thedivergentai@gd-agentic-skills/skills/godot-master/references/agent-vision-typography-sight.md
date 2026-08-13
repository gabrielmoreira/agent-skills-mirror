# Typography sight (receptor-level)

> **MANDATORY** with Family **TYPE** in [taste-receptors.md](agent-vision-taste-receptors.md). Every TYPE-* row must be scored when text is visible — not vibes, not a single “type looks fine.”

If microcopy is unreadable at short-edge **512**, re-capture `--detail` or crop **before** locking TYPE scores.

---

## Architecture (production)

Anchor the scale to the **HUD floor** (smallest critical label at lowest target device), then step up:

| Ratio | Use |
|-------|-----|
| ~1.20–1.25 | Dense HUD |
| ~1.333 | Menus / clearer hierarchy |
| ≥1.5 | Marketing drama only — not HUD data |

**Named roles (TYPE-ROLE-TOKEN):**

| Role | Job | Typical fail |
|------|-----|--------------|
| HUD-Label / data | Ammo, timers, HP, currency | Display/script face |
| Tooltip / body | Sentences, settings | Ultra-condensed / tiny |
| Menu-Header | Sectioning | Same as body |
| Display | Splash, chapter, score reveal | Used for dense numbers |
| Diegetic-Prop | In-world screens | Replaces critical HUD |

**Face cap (TYPE-FACE-CAP):** ≤2 families (+ optional mono/data). ≥4 → **0**.

**Optical size (TYPE-OPSZ-MATCH / TYPE-WEIGHT-OPSZ / TYPE-HUD-FLOOR / TYPE-ANGULAR-SIZE):**
- Micro HUD uses micro/text cuts — open apertures, relaxed spacing.
- Display cut at 11px HUD → **0**.
- Critical HUD ~0.3°+ angular size at stated viewing distance.
- Floor copied from 4K desktop → **0**.

---

## Numerals (TYPE-NUM-*)

Games are number-heavy. Score harshly.

| Receptor | Pass | Fail |
|----------|------|------|
| TYPE-NUM-TABULAR | Columns align; even advances | `1` much narrower than `8` |
| TYPE-NUM-LINING | Digits on baseline row | Oldstyle drop in timer |
| TYPE-NUM-OSF-OK | OSF only in flavor/marketing | OSF in stacked stats |
| TYPE-NUM-SLASH-ZERO | Slashed 0 when 0/O ambiguous | Confusable serials |
| TYPE-NUM-DISTINCT | 0≠O, 1≠l, 5≠S under pressure | Confusable in heat |
| TYPE-NUM-WEIGHT | Numerals ≥ label weight | Thin decorative HP |
| TYPE-MONO-DATA | Mono/tabular for codes/timers | Proportional letter-spacing hack |
| TYPE-STAT-ALIGN | ATK/DEF grid | Ragged values |
| TYPE-TIMER-STABLE | MM:SS holds on tick | Width jitter each second |

---

## Metrics / case / OpenType

| Receptor | Pass | Fail |
|----------|------|------|
| TYPE-XHEIGHT | Open counters at HUD size | Filled a/e; hairlines |
| TYPE-TRACK-BODY | ≤~0.05em | Spaced-out cinematic body |
| TYPE-TRACK-DISPLAY / HUD | Intentional logo; slight HUD tight | Accidental collision / crushed % |
| TYPE-LEAD-BODY / DENSE / DISPLAY | ~1.5–1.65 / 1.3–1.4 / 1.05–1.2 | Colliding or huge voids |
| TYPE-KERN-LOGO | Clean AV/To | Exploded logo |
| TYPE-ALLCAPS-BODY / CASE-* | Spare caps; sentence body; micro legal sized | Caps walls; Title Case body; 8px caps para |
| TYPE-ITALIC-UI | Rare flavor | Italics = every emphasis |
| TYPE-LIGA-DISPLAY | Ligatures in chapter art only | Ligatures in HUD timer |
| TYPE-GLYPH-INTEGRITY | Real language | Fake/garbled mush |
| TYPE-HINT-RASTER | Pixel fonts integer scale | Non-integer blur |

---

## Display vs HUD (TYPE-DISPLAY-HUD-SPLIT) — ship blocker

**2:** Display carries tone; HUD/data is boring and open.
**0:** Chapter-title face on ammo/HP/cooldowns OR diegetic distress type on critical readouts.

Also score: **TYPE-PAIR-DNA**, **TYPE-GENRE-SIGNAL**, **TYPE-DIEGETIC-DISTRESS**, **TYPE-PLATE-TYPE**, **TYPE-LOC-EXPAND / RTL**, **TYPE-MICRO-LEGAL**, **TYPE-MARKETING-DISPLAY**.

---

## Fix language (bind to receptor IDs)

1. `TYPE-DISPLAY-HUD-SPLIT=0` — move ammo/HP off display face onto neutral HUD face; increase numeral weight.
2. `TYPE-NUM-TABULAR=0` — enable tabular/even-width numerals for currency columns.
3. `TYPE-OPSZ-MATCH=0` — swap display cut for text/micro master at HUD size.
4. `TYPE-FACE-CAP=0` — delete tourist faces; keep one display + one UI family.
5. `TYPE-PLATE-TYPE=0` — add plate behind objective over gameplay.
6. `TYPE-GLYPH-INTEGRITY=0` / unreadable at 512 — re-capture `--detail` before rescoring.

---

## Sources

- Sidebearings — Game UI Type Systems; genre typography conventions
- MDN — font-variant-numeric (`tnum`, `lnum`, `onum`, `zero`)
- Monotype — optical sizing
- WCAG / Xbox AGG — contrast intent for glyphs vs plates
- Modular scale — major second → perfect fourth ratios
