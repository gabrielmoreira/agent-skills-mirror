# UI taste sight (production criteria from pixels)

> Cross-check for **HIER / CTRST / AFF / SPACE / TYPE / SLOP**. Prefer production game UI criteria over SaaS “pretty.”
> Primary scores live in [taste-receptors.md](agent-vision-taste-receptors.md). This file is the narrative checklist — do not substitute it for receptor IDs.

Score only visible pixels. Tone never excuses unreadable HP/ammo.

---

## Anti-patterns (AI / default-taste tells)

Judge **co-occurrence**. One trait alone is weak; three or more without compensating art direction → crush **SLOP** and often **HIER**.

| Tell | Looks like | Maps to |
|------|------------|---------|
| Purple / indigo / pink wash | Tailwind-ish gradients | SLOP-PURPLE |
| Neon glow-as-hierarchy | Box-glow every card | SLOP-NEON / LIGHT-BLOOM-HIER |
| Cream + terracotta + italic serif | Warm field + serif + clay | SLOP-CREAM |
| Cardocalypse | Nested equal cards | SLOP-CARD / SPACE-NEST-DEPTH |
| Equal visual weight | HP=XP=social | SLOP-EQUAL / HIER-WEIGHT-MATH |
| Glassmorphism everywhere | Frosted low-contrast | SLOP-GLASS / CTRST-SCRIM-DEPTH |
| Lucide soup | Outline icons in gradient squares | SLOP-LUCIDE / ICON-LUCIDE |
| Garbled text | Fake glyphs | SLOP-FAKE-TEXT / TYPE-GLYPH-INTEGRITY |
| Style over urgency | Ornate critical readouts | TYPE-DISPLAY-HUD-SPLIT / HIER-URGENCY-LADDER |
| Input-model mismatch | Tiny corners; no focus | AFF-HIT / AFF-FOCUS |

---

## Positive criteria → receptor families

| Theme | Score in atlas |
|-------|----------------|
| Urgency → prominence | HIER-* |
| Pressure contrast / plates | CTRST-* |
| Affordances / states | AFF-* |
| Spacing / safe area | SPACE-* |
| Type system | TYPE-* |
| Tone without parse death | HIER-DIEGETIC-SPLIT + TYPE-* + CTRST-* |
| Anti-slop | SLOP-* |

Deep loads: [hier-contrast-receptors.md](agent-vision-hier-contrast-receptors.md) · [space-affordance-receptors.md](agent-vision-space-affordance-receptors.md) · [typography-sight.md](agent-vision-typography-sight.md) · [anti-slop-sight.md](agent-vision-anti-slop-sight.md)

---

## Sources

- WANDR — Game UI Design (frequency/urgency, pressure reading)
- Digest kinship: private `06-game-ui-taste.md`, `10-granular-type-hierarchy.md`
