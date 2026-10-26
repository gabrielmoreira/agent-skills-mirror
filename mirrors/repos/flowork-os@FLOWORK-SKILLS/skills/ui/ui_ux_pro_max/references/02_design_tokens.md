# Semantic Design Tokens & Spatial Scale
<!-- Keyword: design_tokens -->

## 📐 Design Token Architecture
1. **Spatial Scale (4px Base):** `--space-1` (4px), `--space-2` (8px), `--space-3` (12px), `--space-4` (16px), `--space-6` (24px), `--space-8` (32px).
2. **Semantic Surfaces:** Bind all colors to semantic variables (`--background`, `--card`, `--primary`, `--border`, `--muted`). Never use hardcoded hex values in component stylesheets.
3. **Color Contrast:** Light mode and dark mode tokens must independently satisfy WCAG AA >= 4.5:1.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing design tokens, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/02_design_tokens.css`
Use the exact CSS custom properties and spatial cadence defined in this blueprint.
