# Android Jetpack Compose Architecture
<!-- Keyword: android_compose -->

## 🤖 Jetpack Compose Invariants
1. **Material 3 Theming:** Wrap UI in `MaterialTheme` with dynamic color tokens from `ColorScheme`.
2. **State Hoisting:** Stateless composables receive state down and bubble events up via lambda parameters.
3. **Scaffold Layout:** Always use `Scaffold` with proper `contentPadding` applied to inner elements.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing Jetpack Compose screens, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/13_android_scaffold.kt`
Apply the Scaffold padding and MaterialTheme typography specified in this blueprint.
