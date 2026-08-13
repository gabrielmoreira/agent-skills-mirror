# Color & icon receptors (deep criteria)

> Supports **COLOR-*** and **ICON-*** rows in [taste-receptors.md](taste-receptors.md). Score from pixels only.

---

## Color as feedback language

Games train players: **red → damage/danger**, **gold/yellow → reward/XP**. Violating that without diegetic retrain burns trust.

### Role map (COLOR-ROLES / COLOR-LAYERS)

Typical production set: **4–6 semantic roles** (+ tints for states). Players cannot learn 12+ competing meanings mid-combat.

| Role | Typical hues | Must NOT also mean |
|------|--------------|--------------------|
| Danger / damage / blocked | Red, crimson | Bonus pickup, primary brand spam |
| Reward / value | Gold, yellow | Map hazard, error |
| Heal / safe (if used) | Green / cyan — **with shape backup** | Enemy telegraph |
| Interactable / action | Accent distinct from danger/reward | Decorative chrome |
| Caution / objective | Mid-urgency yellow — sparingly | Equal scream to danger |
| Neutral / structure | Muted family | Competing with accents |

**Four-layer UI stack:** deep base → panel → muted info → vivid action. Action hues must not match world props (false affordance).

### Accent budget (COLOR-BUDGET / COLOR-ACC-JOB)

| Rule | Target | Fail |
|------|--------|------|
| Accent area | ~5–15% UI surface at full chroma | &gt;~30% saturated chrome |
| Accent jobs | Urgency, primary CTA, rare/special | Neon borders on all cards |
| Glow | Optional local highlight | Box-glow-as-structure |

### CVD / simultaneous / tokens

| Receptor | PASS | FAIL |
|----------|------|------|
| COLOR-ONLY / COLOR-CB | Shape/icon/pattern/text twin | Color-only team/rarity/error |
| COLOR-DL | Competing meanings also differ in value | Same-value hue swap |
| COLOR-SIM | Roles survive brightest+darkest BG | Status hue mush vs world |
| COLOR-TOK | States are tints of role tokens | Per-widget random hues |
| COLOR-RED / COLOR-GOLD | Reserved meanings | Red accent tourism; gold as hazard |
| COLOR-UI-WORLD / COLOR-FX / COLOR-COUNT | Same family; FX on-brand; limited feel | SaaS kit; unbound FX; infinite lottery |

### Contrast floors (shared with CTRST)

- Body text vs local plate: ~**4.5:1** intent.
- Non-text UI components: ~**3:1** intent (WCAG 1.4.11).
- Icons vs BG: ≥ ~**3:1**.

Unsafe alone: red↔green, magenta↔cyan extremes, blue↔purple low ΔL, yellow↔lime on bright BG, health bar hue-only G→Y→R.

---

## Icon set discipline

**Unit of design is the set**, not a single icon.

### Grid & stroke (ICON-GRID / KEYLINE / STROKE / CORNER / PIXEL-LOCK / OPSZ)

| Icon CSS size (approx) | Stroke heuristic |
|------------------------|------------------|
| ~16px | ~1–1.5px (heavier opsz) |
| ~24px | ~2px |
| ~32px | ~2–2.5px |
| ~48px | ~3px |

Shared: canvas, padding, stroke, corner/terminal, detail level, light direction. Circles optically larger than squares on keylines. On-pixel at target HUD size.

### Silhouette / metaphor / perspective

1. Mentally fill solid black (**ICON-SIL**).
2. At ~24–32px: sword ≠ axe ≠ potion?
3. Twin blobs → **0**.

**ICON-META / ICON-PERSP:** one skeuomorph dial; front/¾ agreement — not Lucide next to painted RPG loot next to neon glass.

### Category / chrome / state

- **ICON-CAT:** category frames include **shape** backup (not hue-only rarity).
- **ICON-CHROME:** shared radius/border/shadow across buttons/panels.
- **ICON-STATE:** default / selected / disabled (and pressed if shown).
- **ICON-LUCIDE:** Lucide-in-gradient-squares as whole identity → **0**.
- **ICON-DETAIL:** detail that only reads at 2K fails inventory size.

### Scoring tips

- `COLOR-RED=0` — shop sale badge red while damage numbers also red; no shape difference.
- `ICON-SIL=0` — two inventory weapons identical in black-fill mental test.
- `COLOR-BUDGET=0` — &gt;30% of chrome at full chroma.

---

## Sources

- GameJuice — Color as a Feedback Language
- Made Good Designs — Game icon sets, silhouette test
- Material Design — System icons (grid, keylines, optical corrections)
- WCAG 1.4.1 Use of Color; 1.4.11 Non-text Contrast
- ColorPick / ColorArchive — game UI palette roles, 4-layer stack
- Xbox / PlayStation accessibility culture — colorblind modes + non-color cues
