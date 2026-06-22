# Design Token Reference

Update this file whenever a new token is added to `tailwind.config.ts`, so the skill stays accurate.

## Color tokens
| Token | CSS variable | Usage |
|---|---|---|
| `primary` | `--primary` | Primary actions, links |
| `secondary` | `--secondary` | Secondary actions |
| `destructive` | `--destructive` | Delete/error states |
| `muted` | `--muted` | Disabled/secondary text, subtle backgrounds |
| `border` | `--border` | Default border color |

## Spacing
Use the default Tailwind scale (`p-4`, `gap-6`, etc). Only add custom spacing tokens for values used in 3+ places that don't map to the default scale.

## Typography
| Token | Usage |
|---|---|
| `font-sans` | Default body text (set via `next/font`) |
| `text-2xl font-semibold tracking-tight` | Page-level H1 |
| `text-lg font-medium` | Section H2 |
| `text-sm text-muted-foreground` | Helper/caption text |
