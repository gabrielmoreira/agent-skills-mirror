# Windows Desktop XAML & WinUI Architecture
<!-- Keyword: wpf_xaml -->

## 🪟 Windows GUI Invariants
1. **MVVM Separation:** Zero business logic in code-behind (`.xaml.cs`). Bind all view data through `DataContext` and ViewModels.
2. **WinUI 3 Modern Surfaces:** Use `Mica` or `Acrylic` background brushes with high-contrast text foregrounds.
3. **Resource Dictionaries:** Define all spatial margins and brushes in shared `ResourceDictionary` files.

### 🛠️ Mandatory Implementation Blueprint:
DO NOT IMPROVISE CODE BEFORE INSPECTING THE OFFICIAL BLUEPRINT!
Before implementing XAML desktop interfaces, you MUST inspect the official reference template via `view_file`:
`skills/ui_ux_pro_max/example/10_wpf_mica_window.xaml`
Adhere strictly to the window styling and dynamic resource bindings defined in this blueprint.
