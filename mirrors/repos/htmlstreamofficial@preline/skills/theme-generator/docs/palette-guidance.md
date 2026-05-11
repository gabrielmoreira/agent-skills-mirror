# Palette guidance

Use this file for color-direction heuristics only.

Important: references below to custom palettes like `--color-<name>-*` or `--color-<name>-gray-*` describe draft palette exploration and shared-palette design patterns. They do NOT override `docs/final-output-style.md`, which defines how the final `<name>.css` file should be structured.

## Contents

- [Hue reference](#hue-reference-for-workflow-normalization)
- [Mood and palette guidance](#mood-and-palette-guidance)
- [Accessibility and contrast guidelines](#accessibility-and-contrast-guidelines-wcag)
- [Palette types](#palette-types)
- [Custom gray palettes](#custom-gray-palettes-neutral-matching)

## Hue reference (for workflow normalization)

| Color | Hue Range | Tailwind Gray |
|-------|-----------|---------------|
| Red/Coral | 0-30 | neutral |
| Orange/Amber | 30-60 | stone |
| Yellow/Gold | 60-90 | stone |
| Green/Lime/Avocado | 90-150 | stone |
| Teal/Cyan | 150-200 | zinc |
| Blue/Azure | 200-260 | slate |
| Violet/Purple | 260-300 | zinc |
| Magenta/Pink/Rose | 300-360 | neutral |

## Mood and palette guidance

### Color psychology reference

| Mood | Primary Hues | Neutral Family | Characteristics |
|------|--------------|----------------|-----------------|
| Professional | Blue, Slate, Indigo | gray, slate | Clean, trustworthy, corporate |
| Creative | Purple, Pink, Orange | neutral | Innovative, artistic, expressive |
| Natural | Green, Teal, Brown | stone | Organic, sustainable, calm |
| Energetic | Orange, Yellow, Red | neutral | Bold, active, attention-grabbing |
| Luxurious | Gold, Purple, Black | zinc | Premium, elegant, sophisticated |
| Playful | Pink, Cyan, Yellow | neutral | Fun, youthful, approachable |
| Tech/Cyber | Cyan, Green, Purple | slate, zinc | Modern, digital, futuristic |
| Warm | Orange, Amber, Brown | stone | Cozy, inviting, comfortable |
| Cool | Blue, Teal, Slate | gray, slate | Calm, refreshing, serene |
| Minimal | Gray, White, Black | gray | Simple, focused, uncluttered |

### Building cohesive palettes

1. Pick a primary: the hero color for buttons, links, CTAs
2. Choose matching neutrals: warm primaries -> stone/neutral; cool primaries -> gray/slate
3. Define contrast: bold brands -> high contrast; soft aesthetics -> low contrast
4. Consider dark mode: primary often shifts lighter; neutrals shift to darker family

### Accessibility and contrast guidelines (WCAG)

Ensure themes meet WCAG 2.1 AA contrast requirements:

| Element | Minimum Ratio | OKLCH Rule of Thumb |
|---------|---------------|---------------------|
| Body text on background | 4.5:1 | Lightness difference >= 50% |
| Large text (18pt+) | 3:1 | Lightness difference >= 40% |
| UI components (buttons, inputs) | 3:1 | Lightness difference >= 40% |
| Focus indicators | 3:1 | Use distinct color + lightness |

OKLCH lightness thresholds:

| Context | Light Mode | Dark Mode |
|---------|------------|-----------|
| Background | L >= 95% | L <= 25% |
| Text on light bg | L <= 45% | -- |
| Text on dark bg | -- | L >= 85% |
| Primary button text | Check against primary-500/600 | Check against primary-400 |

Readable primary foreground:
- Do not decide from hue alone.
- Compare candidate text colors against the actual generated primary shades used by the theme.
- For light mode, check the generated `primary-600` and `primary-700` states.
- For dark mode, check the generated `primary-400` and `primary-500` states.
- Choose the text color with the stronger worst-case contrast across those states.
- White usually wins for medium or dark primaries; dark gray should only be used when the generated brand states are genuinely light.
- In dark mode, it is valid to shift the primary button one step deeper (for example `500/600` instead of `400/500`) when that keeps white text readable and better matches the design system.

Readable inverse and decorative accents:
- `--foreground-inverse` is not just for neutral inverse surfaces. In Preline it is also used on vivid utility colors such as red/orange badges and chips.
- In dark mode, prefer keeping `--foreground-inverse` white unless contrast checks prove a darker value is still safe across those saturated utility colors.
- Do not let dark mode inherit very deep brand steps for decorative tokens such as `--chart-5` when those tokens are likely to appear in gradient text or accent UI.
- For dark decorative/chart tokens, prefer mid-to-light brand steps that stay clearly visible on dark backgrounds.

Quick check: If |L_text - L_background| >= 50%, contrast is likely sufficient for body text.

## Palette types

When generating custom themes, there are TWO distinct types of custom color palettes:

| Palette Type | Example Variable | Purpose | Chroma Level |
|--------------|------------------|---------|--------------|
| Brand palette | `--color-<name>-*` | Primary/accent colors, buttons, links, CTAs | Vibrant (high chroma) by default |
| Gray palette | `--color-<name>-gray-*` | Backgrounds, surfaces, borders, dark mode neutrals | Soft (low chroma 0.002-0.035) |

### When to create each palette

ALWAYS create TWO palettes in `@theme inline { }`:
1. Brand palette (`--color-<name>-*`) for primary/accent colors
2. Gray palette (`--color-<name>-gray-*`) for backgrounds, surfaces, borders

Both palettes are used in light mode for a cohesive feel.

Dark mode behavior depends on user request:

| User Request | Light Mode Uses | Dark Mode Uses |
|--------------|-----------------|----------------|
| "soft rose theme" (default) | Custom gray (`--color-<name>-gray-*`) | Tailwind gray (`zinc`, `stone`, etc.) |
| "soft rose theme with matching dark mode" | Custom gray (`--color-<name>-gray-*`) | Custom gray (`--color-<name>-gray-*`) |

Trigger phrases for custom dark mode palette:
- "matching dark mode"
- "cohesive dark mode"
- "consistent dark colors"
- "unified light and dark"
- "matching neutrals"

If none of these phrases appear -> light mode uses custom gray, dark mode uses Tailwind grays.

### Brand color style (vibrant vs soft)

Brand palettes are vibrant by default (like Tailwind's blue, green, orange). Only reduce chroma if user explicitly requests:

| User Says | Brand Palette Style | Chroma Level |
|-----------|---------------------|--------------|
| Default (no modifier) | Vibrant, follow Tailwind color saturation | 0.10-0.20+ |
| "soft", "muted", "ash", "pastel", "dusty", "desaturated" | Soft, reduced chroma like lavender/khaki | 0.02-0.05 |

Example comparison:

```css
/* Vibrant brand (default) */
--color-<name>-500: oklch(55% 0.14 <hue>);

/* Soft/muted brand (if requested) */
--color-<name>-500: oklch(55% 0.04 <hue>);
```

## Custom gray palettes (neutral matching)

When a theme benefits from unique neutrals, generate a custom neutral palette that harmonizes with the primary color. These are NOT pure grays; they have subtle warmth or coolness.

### Palette characteristics

| Palette Type | Hue Range | Chroma Range | Use With |
|--------------|-----------|--------------|----------|
| Warm neutrals | 60-100 degrees (yellow/brown) | 0.002-0.035 | Orange, amber, brown, gold primaries |
| Cool neutrals | 200-260 degrees (blue/slate) | 0.002-0.030 | Blue, cyan, teal, indigo primaries |
| Rose neutrals | 330-360 degrees (pink) | 0.002-0.040 | Pink, rose, magenta primaries |
| Green neutrals | 120-160 degrees (sage) | 0.002-0.030 | Green, emerald, teal primaries |

### OKLCH pattern for gray palettes (bell curve chroma)

Gray palettes use a bell curve chroma pattern: very low at extremes (light AND dark), peaking at mid-tones. This ensures:
- Light mode backgrounds (50-200) look clean with subtle tint
- Dark mode backgrounds (800-950) look sophisticated, not muddy

```css
--color-<name>-gray-50:  oklch(98%   0.002 <hue>);  /* Almost neutral */
--color-<name>-gray-100: oklch(95.5% 0.004 <hue>);
--color-<name>-gray-200: oklch(89.7% 0.008 <hue>);
--color-<name>-gray-300: oklch(82.7% 0.012 <hue>);  /* Building up */
--color-<name>-gray-400: oklch(73%   0.018 <hue>);  /* Approaching peak */
--color-<name>-gray-500: oklch(62.5% 0.020 <hue>);  /* PEAK chroma */
--color-<name>-gray-600: oklch(52.8% 0.016 <hue>);  /* Starting to fade */
--color-<name>-gray-700: oklch(41.4% 0.012 <hue>);  /* Fading */
--color-<name>-gray-800: oklch(34.6% 0.008 <hue>);  /* Very low */
--color-<name>-gray-900: oklch(30.6% 0.005 <hue>);  /* Almost neutral */
--color-<name>-gray-950: oklch(20.1% 0.003 <hue>);  /* Nearly pure dark */
```

Critical: Dark mode backgrounds (800-950) need very low chroma:

| Shade | Chroma | Why |
|-------|--------|-----|
| 950 | 0.003 | Dark backgrounds must be nearly neutral |
| 900 | 0.005 | Avoids muddy/colored appearance |
| 800 | 0.008 | Just a hint of warmth/coolness |
| 500 | 0.020 | Peak, midtones carry color identity |
| 50 | 0.002 | Light backgrounds stay clean |

Key principles:
- Chroma peaks at mid-tones (400-600), very low at BOTH extremes
- Dark end (800-950) must have lower chroma than light end for clean dark mode
- Hue stays consistent across the scale (±5 degrees variation is acceptable)
- Lightness follows standard 50-950 scale

### Placement of custom palettes

Custom color palettes MUST be defined in the `@theme theme-<name> inline { }` block:

```css
@theme theme-<name> inline {
  /* Custom neutral palette for this theme */
  --color-<name>-50: oklch(98% 0.003 88);
  --color-<name>-100: oklch(95.5% 0.005 88);
  /* ... full 50-950 scale ... */
}
```

Then reference these in the theme selector blocks using `var()`:

```css
[data-theme="theme-<name>"] {
  --background: var(--color-<name>-50);
  --background-1: var(--color-<name>-100);
  /* ... */
}

[data-theme="theme-<name>"].dark {
  --background: var(--color-<name>-950);
  --background-1: var(--color-<name>-900);
  /* ... */
}
```

### When to create custom palettes

| Scenario | Action |
|----------|--------|
| Primary is warm (orange/amber/brown) | Create warm neutral palette OR use `stone` |
| Primary is cool (blue/cyan/indigo) | Use `slate` or `gray` (usually sufficient) |
| Primary is unique (gold, khaki, etc.) | Create matching custom neutral palette |
| User explicitly requests | Always create to match their vision |
| Theme needs distinctive personality | Create for cohesion |

### Using custom palettes in both modes

Soft gray palettes work seamlessly across light and dark modes:
- Light mode: use 50-300 for backgrounds, 600-950 for text
- Dark mode: use 800-950 for backgrounds, 50-300 for text

This creates consistent warmth/coolness across modes while maintaining readability.
