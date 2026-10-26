# Svelte 5 Runes & Reactive Architecture
<!-- Keyword: svelte_runes -->

## 🧡 Svelte 5 Runes Invariants
1. **Modern Runes:** Use `$state()`, `$derived()`, and `$effect()`. Eliminate legacy Svelte 4 `let:` and `$: reactive declarations`.
2. **Component Snippets:** Use modern `{#snippet name()}` and `render` blocks for clean template slot composition.
3. **Event Directives:** Use standard `onclick={handler}` instead of legacy `on:click`.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing Svelte components, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/07_svelte_runes_card.svelte`
Adhere strictly to the modern runes and event bindings demonstrated in this blueprint.
