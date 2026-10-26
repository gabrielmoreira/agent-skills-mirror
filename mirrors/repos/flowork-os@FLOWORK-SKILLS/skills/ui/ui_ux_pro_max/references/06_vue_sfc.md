# Vue 3 SFC & Reactive Component Architecture
<!-- Keyword: vue_sfc -->

## 💚 Vue 3 Script Setup Invariants
1. **Script Setup:** Always use `<script setup lang="ts">`. Avoid Options API.
2. **Typed Props & Emits:** Use `defineProps<{ title: string; variant?: string }>()` and `defineEmits<{ (e: 'submit', val: string): void }>()`.
3. **Scoped CSS:** All components must use `<style scoped>` bound to design tokens via `var(--primary)`.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing Vue components, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/06_vue_reactive_card.vue`
Follow the script setup structure and scoped token styling defined in this blueprint.
