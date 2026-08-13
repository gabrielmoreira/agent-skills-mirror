# Hierarchy & contrast receptors (deep criteria)

> Supports **HIER-*** and **CTRST-*** rows in [taste-receptors.md](taste-receptors.md). Score from pixels only.
> Research juice: Sidebearings, Nasty Rodent HUD, NN/G hierarchy/Gestalt, WCAG 1.4.3/1.4.11, Xbox XAG-101/102.

---

## Hierarchy as attention budget

Visual hierarchy in games is **not** prettier headings. It is attention budgeting under motion, peripheral vision, and simultaneous 3D focal load.

### Weight math (HIER-WEIGHT-MATH)

Composite rank ≈ **size × contrast × motion × saturation**. Squint the WebP: one dominant blob should win. Three equal-saturation accents (health, quest, shop) same size → **0**.

### Peripheral vs foveal (HIER-FOVEAL-CLEAR / HIER-PERIPH-READ)

| Zone | Job | Fail |
|------|-----|------|
| Center ~60% | Foveal combat/action | Minimap+quest+chat covering center third |
| Corners/edges | Persistent HUD | Three-digit micro numerals that force look-away |

Peripheral HUD must communicate via **shape / bar / icon change** — not only tiny glyphs.

### Urgency ladder (HIER-URGENCY-LADDER)

```text
critical (HP red, objective pulse)
  > persistent (ammo, cooldowns)
    > meta (ping, cosmetics, battle pass)
```

Battle-pass / social badge competing with HP at equal weight → **0**.

### Layer stack (HIER-TOOLTIP-Z / HIER-MODAL-TOAST / HIER-PAUSE-SCRIM)

```text
modal (blocks toasts)
  > tooltip (above HUD, below modal)
    > HUD
      > gameplay
```

Achievement toast covering “Confirm quit” → **0**. Pause without scrim so gameplay text still competes → **0**.

### Encounter / ephemeral elevators

| Receptor | PASS | FAIL |
|----------|------|------|
| HIER-BOSS-BAR | Wide boss HP top-center; player demoted | Boss bar = ammo width |
| HIER-COMBO-FLASH | Combo flashes large then collapses | Permanent display size for combo |
| HIER-INTERACT-SING | One “E — Open” near reticle | Three equal prompts |
| HIER-OBJ-MARKER | One pulsing waypoint; POIs greyed | Every map icon same hue/size |
| HIER-MINIMAP-RANK | Minimap ≤25% weight vs HP in squint | Map border glow = boss frame |
| HIER-CURRENCY-DEMOTE | Coin small corner | SALE banner = objective |
| HIER-PROGRESSIVE-FADE | Idle HUD ~40% opacity | All HUD 100% always |
| HIER-DEAD-EMPTY | Grey lock + label | Empty = legendary saturation |

### Marketing / onboarding

- **HIER-MARKETING-PLAY:** Play/Continue largest; Wishlist secondary.
- **HIER-TUTORIAL-CALLOUT:** Arrow+plate; HP still readable — not full-screen tutorial = title size.
- **HIER-INPUT-HINT:** Platform glyphs match primary input model.
- **HIER-SUBTITLE-LANE:** Bottom safe band; never covers ability bar.
- **HIER-SCAN-PATH:** Health → ammo → objective follows edge HUD / F-pattern.

---

## Contrast as separation under pressure

Contrast is local and **worst-case** — not a spot sample on the quietest plate.

### Floors (sight heuristics)

| Receptor | Intent | Fail tell |
|----------|--------|-----------|
| CTRST-BODY-45 | ~4.5:1 body/HUD vs local plate | Mid-grey on dark grey timer |
| CTRST-LARGE-30 | ~3:1 large/display | Decorative grey title |
| CTRST-ICON-30 | ~3:1 non-text chrome (WCAG 1.4.11) | Grey-on-grey toggle |
| CTRST-FOCUS-30 | Focus ≥~3:1 vs unfocused | 1px hue shift only |
| CTRST-DISABLED-30 | Disabled still readable | Disabled = background |
| CTRST-HC-MODE | If HC shown: ~7:1 borders+text | Cosmetic recolor only |

### Plates / scrims / outlines

| Receptor | PASS | FAIL |
|----------|------|------|
| CTRST-PLATE-OPACITY | ~70–85% plate; glyphs crisp | 15% haze or 95% sticker |
| CTRST-PLATE-EDGE | Shadow/bevel vs world | Plate = sky luminance |
| CTRST-SCRIM-DEPTH | Modal 50–70% dim | Gameplay highlights bleed through |
| CTRST-OUTLINE-WEIGHT | Shared 1–2px @1080 | 4px glow on ammo, none on HP |
| CTRST-GRAD-WORST | Text on darkest stop; all stops pass | Text crosses failing gradient band |
| CTRST-SIMULTANEOUS | Plate over grass/sky | Raw white on snow/cloud |

### Device class & FX

| Receptor | PASS | FAIL |
|----------|------|------|
| CTRST-TV-LOUNGE | Couch-readable labels | 12px primary on living-room capture |
| CTRST-HANDHELD-SUN | Extra plate/shadow outdoors | Thin white on bright sky |
| CTRST-FX-BLOOM | Damage vignette edges; UI intact | Bloom washes ammo numerals |
| CTRST-FX-CHROMA | Enemy FX ≠ interact/damage UI hex | Red explosion = damage UI |
| CTRST-SEMANTIC-NONCOLOR | Poison = icon+label+pattern | Red/green buff identical shape |
| CTRST-OVERLAP-LEG | Stacked bars offset | Two labels same pixel row intersect |

### Score language

Cite receptor ID + pixel evidence:

- `HIER-WEIGHT-MATH=0` — health, quest, and shop icons same size and saturation; no squint primary.
- `CTRST-GRAD-WORST=0` — objective text crosses light→dark sky gradient; mid stop fails.

---

## Sources

- Sidebearings — Game UI Type Systems (angular size, roles, diegetic split)
- Nasty Rodent — HUD design (peripheral vs foveal)
- NN/G — Visual hierarchy; Gestalt proximity / common region
- WCAG 2.2 — 1.4.3 Contrast; 1.4.11 Non-text; 2.4.11 Focus Appearance
- Xbox AGG — XAG-101 Text; XAG-102 Contrast
