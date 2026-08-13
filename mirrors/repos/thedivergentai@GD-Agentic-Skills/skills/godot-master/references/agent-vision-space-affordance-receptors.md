# Spacing & affordance receptors (deep criteria)

> Supports **SPACE-*** and **AFF-*** rows in [taste-receptors.md](agent-vision-taste-receptors.md).

---

## Spacing encodes relationship without reading

### Rhythm

| Receptor | PASS | FAIL |
|----------|------|------|
| SPACE-8PT-RHYTHM | Margins/padding on 8pt (4pt micro) | 13/19/27px random gaps |
| SPACE-4PT-MICRO | Icon–label ~4px consistent | Icon touching text or 14px orphan |
| SPACE-PANEL-PAD | Card 16px all sides | Top 8 / bottom 24 same component |
| SPACE-STACK-MODAL | Title 24 → body 16 → CTA 24 | CTA glued to body |

### Gestalt

| Receptor | PASS | FAIL |
|----------|------|------|
| SPACE-PROX-CLUSTER | Related controls closer than unrelated | Equal spacing — no functional groups |
| SPACE-REGION-PANEL | Card wraps image+title+rating | Title far from its stat block |
| SPACE-GUTTER | Inter-column gutter ≥ intra-group | Gutter ≤ icon padding — columns merge |
| SPACE-NEST-DEPTH | ≤2 meaningful nest levels | Card→card→card equal frames |
| SPACE-RESP-COLLAPSE | Mobile stacks keep groups | Shrunk view merges unrelated |

### Alignment

| Receptor | PASS | FAIL |
|----------|------|------|
| SPACE-ALIGN-COL | Shop prices one axis | Price zigzag |
| SPACE-ALIGN-BASELINE | Label + value share baseline | Value floats |
| SPACE-ALIGN-GRID | Settings labels flush left | Staggered edges |

### Safe area / playfield

| Receptor | PASS | FAIL |
|----------|------|------|
| SPACE-SAFE-TV | Critical inside ~90% title safe | HP at 95% edge |
| SPACE-SAFE-NOTCH | Top HUD below notch inset | Timer under Dynamic Island |
| SPACE-SAFE-OVERSCAN | BG full bleed; UI inset | Interactive button in overscan kill |
| SPACE-EDGE-HUD | 16–24px from bezel | Icons glued to physical edge |
| SPACE-PLAYFIELD | Combat center clear ring | Corner HUD creeps &gt;15% inward |
| SPACE-DENSITY-BUDGET | Pause ≤~7 primary rows | 15 equal tiles one view |

---

## Affordances & state language

Visible state set for operable chrome:

| State | Evidence required |
|-------|-------------------|
| Default | Resting operable ≠ static art |
| Hover (pointer) | Optional lift; **never** the only focus cue |
| Pressed / active | Darker/inset/scale ≠ selected |
| Disabled | Lower opacity **and** lock/slash/muted stroke |
| Selected / focused | Outline/pip/underline/fill — survives CVD |

### Receptor checklist

- **AFF-OPERABLE / AFF-FALSE** — Chrome ≠ art; props must not look clickable.
- **AFF-SELECTED / AFF-FOCUS / AFF-HOVER** — Non-color focus; hover ≠ focus substitute on pad.
- **AFF-DISABLED** — Dim alone is not enough.
- **AFF-PRESSED / AFF-FEEDBACK** — Instant readable change.
- **AFF-HIT / AFF-CURSOR-PAD** — TV/pad targets; no dense pointer-only grids for pad briefs.
- **AFF-CTA-VIS** — Singular strong plate.
- **AFF-DEPTH** — Consistent bevel/shadow language (not flat+3D lottery).
- **AFF-TOGGLE / AFF-DRAG** — Shape backup for on/off; visible grip if drag exists.

Material opacity ladders (reference, not mandate): light BG active ~87%/54%, inactive ~38%; dark BG ~100%/70%/50%. Games often prefer fill+outline over opacity alone.

---

## Sources

- NN/G — Gestalt proximity / common region
- Game Developer — Gestalt laws in game design
- Unity Screen.safeArea; Epic TV TitleRatio ~0.9 / SMPTE safe zones
- Material Design — system icon state opacities (adapt, don’t copy SaaS)
- Made Good Designs — Game UI focus/selected states
