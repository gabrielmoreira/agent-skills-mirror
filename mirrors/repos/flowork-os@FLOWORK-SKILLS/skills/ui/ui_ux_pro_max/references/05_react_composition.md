# React Compound Component Architecture
<!-- Keyword: react_composition -->

## ⚛️ Component Composition Invariants
1. **Compound Pattern:** Avoid mega-components with 20+ boolean props. Deconstruct into subcomponents (`Card`, `Card.Header`, `Card.Body`, `Card.Footer`).
2. **Accessible Keyboard Navigation:** Modals, dropdowns, and tabs must manage focus trapping and Escape key closures automatically.
3. **Prop Invariants:** Explicit TypeScript interface for every component. Never use `any` for props or state events.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing React components, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/05_react_compound_card.tsx`
Mirror the compound context provider architecture and typed props defined in this blueprint.
