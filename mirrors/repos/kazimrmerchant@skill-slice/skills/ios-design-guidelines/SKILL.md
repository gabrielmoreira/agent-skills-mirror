---
name: ios-design-guidelines
description: "Audits native iPhone SwiftUI/UIKit chrome: 44pt hit areas, safe areas, semantic text styles, Dynamic Type reflow, semantic colors/Dark Mode, VoiceOver, and tab-bar navigation. Use for HIG and accessibility UI reviews. Not a system-intent/Shortcuts chair (ios-app-intents). Never treat responsive web CSS as a substitute."
version: 1.0.1
domain: Mobile-Development
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

# iOS Design Guidelines for iPhone

## When to Use
Use this skill when building, auditing, or refactoring native iOS interfaces (SwiftUI or UIKit) for iPhone. Apply this for mobile app UX, responsive web, touch ergonomics, safe areas, keyboard behavior, and platform-specific interface decisions. Trigger keywords: safe area, touch target, Dynamic Type, semantic colors, accessibility, VoiceOver, tab bar, NavigationStack, Dark Mode.

## Prerequisites
- Xcode with SwiftUI/UIKit support.
- Familiarity with Apple Human Interface Guidelines and W3C WCAG 2.2.
- If available, load reference files from `references/` for detailed WCAG or HIG checklists before starting an audit.

## Procedure

### 1. Layout & Safe Areas
1. **Minimum 44pt Touch Targets**: All interactive elements must have a minimum tap target of 44x44 points.
   ```swift
   Button("Save") { save() }
       .frame(minWidth: 44, minHeight: 44)
   ```
2. **Respect Safe Areas**: Never place interactive or essential content under the status bar, Dynamic Island, or home indicator. Use `.ignoresSafeArea()` only for background fills or decorative elements.
3. **Primary Actions in the Thumb Zone**: Place primary actions at the bottom of the screen. Secondary actions and navigation belong at the top.
4. **Support All iPhone Screen Sizes**: Design for iPhone SE (375pt wide) through iPhone Pro Max (430pt wide). Use flexible layouts (`maxWidth: .infinity`), avoiding hardcoded widths.
5. **8pt Grid Alignment**: Align spacing, padding, and element sizes to multiples of 8 points (8, 16, 24, 32, 40, 48). Use 4pt for fine adjustments.
6. **Landscape Support**: Support landscape orientation unless the app is task-specific (e.g., camera).

### 2. Navigation
1. **Tab Bar for Top-Level Sections**: Use a tab bar at the bottom for 3 to 5 top-level sections. Each tab represents a distinct category.
2. **Never Use Hamburger Menus**: Hamburger menus hide navigation and reduce discoverability. Use a tab bar or "More" tab.
3. **Large Titles in Primary Views**: Use `.navigationBarTitleDisplayMode(.large)` for top-level views. Titles transition to inline when scrolling.
4. **Never Override Back Swipe**: The swipe-from-left-edge gesture is a system-level expectation. Never attach custom gesture recognizers that interfere with it.
5. **Use NavigationStack**: Use `NavigationStack` (not deprecated `NavigationView`) for drill-down content. Use `NavigationPath` for programmatic navigation.
6. **Preserve State Across Navigation**: Restore scroll position and input state using `@SceneStorage` or state structures.
7. **Prefer Recognition Over Recall**: Keep current location, recent choices, and available destinations visible.

### 3. Typography & Dynamic Type
1. **Use Built-in Text Styles**: Always use semantic text styles (`.headline`, `.body`, `.caption`) rather than hardcoded sizes.
2. **Support Dynamic Type**: Layouts must reflow at accessibility sizes (up to ~200%) without truncating or clipping. Use `@Environment(\.dynamicTypeSize)` to adapt layouts.
3. **Custom Fonts Must Scale**: If using a custom typeface, scale it relative to a text style.
   ```swift
   // SwiftUI
   .custom("CustomFont-Regular", size: 17, relativeTo: .body)
   // UIKit
   let metrics = UIFontMetrics(forTextStyle: .body)
   label.font = metrics.scaledFont(for: customFont)
   ```
4. **SF Pro as System Font**: Use the system font unless brand requirements dictate otherwise.
5. **Minimum 11pt Text**: Never display text smaller than 11pt. Prefer 17pt for body text.
6. **Hierarchy Through Weight and Size**: Establish visual hierarchy through font weight and size, not solely color.

### 4. Color & Dark Mode
1. **Use Semantic System Colors**: Use system-provided semantic colors (`.primary`, `.secondary`, `Color(.systemBackground)`) that adapt to light/dark modes.
2. **Provide Light and Dark Variants**: Define custom colors in the asset catalog with both Any Appearance and Dark Appearance variants.
3. **Never Rely on Color Alone**: Pair color with text, icons, or shapes to convey meaning.
4. **4.5:1 Contrast Ratio Minimum**: All text must meet WCAG AA contrast ratios: 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt+ bold).
5. **Support Display P3 Wide Gamut**: Use Display P3 color space for vibrant, accurate colors on modern iPhones.
6. **Background Hierarchy**: Use `systemBackground`, `secondarySystemBackground`, and `tertiarySystemBackground` for depth.
7. **One Accent Color**: Choose a single tint/accent color for all interactive elements.

### 5. Accessibility
1. **VoiceOver Labels**: Every interactive element must have a meaningful accessibility label.
2. **Logical Navigation Order**: Ensure VoiceOver reads elements in logical order. Use `.accessibilitySortPriority()`.
3. **Support Bold Text**: Use `@Environment(\.legibilityWeight)` in SwiftUI or check `UIAccessibility.isBoldTextEnabled` in UIKit.
4. **Support Reduce Motion**: Disable decorative animations and parallax when Reduce Motion is enabled using `@Environment(\.accessibilityReduceMotion)`.
5. **Support Increase Contrast**: Use `@Environment(\.colorSchemeContrast)` to detect contrast configuration.
6. **Alternative Interactions**: Every custom gesture must have an equivalent tap-based or menu-based alternative.
7. **Support Switch Control and Full Keyboard Access**: Ensure all interactions work with external switches and Bluetooth keyboards.

### 6. Gestures & Input
1. **Use Standard Gestures**: Tap, long press, swipe, pinch, rotate.
2. **Never Override System Gestures**: Do not intercept swipe from left edge, swipe down from top-left/right, or swipe up from bottom.
3. **Custom Gestures Must Be Discoverable**: Provide visual hints and a visible button alternative.
4. **Support All Input Methods**: Touch, hardware keyboards, assistive devices, pointer input.

### 7. Components
1. **Button Styles**: Use `.borderedProminent` for primary, `.bordered` for secondary, `.borderless` for tertiary, `.destructive` for delete/remove.
2. **Alerts**: Use sparingly for critical information. Prefer 2 buttons; maximum 3.
3. **Sheets**: Present sheets for self-contained tasks. Always provide a dismiss path. Use `.presentationDetents()` for half-height.
4. **Lists**: Use `.insetGrouped` as default. Support swipe actions. Minimum row height is 44pt.
5. **Tab Bar Behavior**: Use SF Symbols (filled for selected, outline for unselected). Never hide the tab bar when navigating deeper. Use `.badge()`.
6. **Search**: Place search using `.searchable()`. Provide search suggestions and recent searches.
7. **Context Menus**: Use for secondary actions (long press). Never as the only way to access an action.
8. **Progress Indicators**: Determinate for known duration, indeterminate for unknown. Never block the entire screen.
9. **SF Symbols**: Use appropriate rendering modes (Monochrome, Hierarchical, Palette, Multicolor).

### 8. Privacy & System Integration
1. **Permissions in Context**: Request permissions in context, not at launch. Show a custom explanation before the system dialog.
2. **Sign in with Apple**: Offer alongside other providers. Allow app usage without an account for basic features.
3. **App Tracking Transparency**: Show ATT prompt if tracking, and respect denial.
4. **System Integration**: Provide glanceable widgets, index content for Spotlight, support Share Sheet, and handle interruptions gracefully.

## Pitfalls
1. **Hamburger menus**: Use a tab bar. Hamburger menus hide navigation and reduce feature discoverability by up to 50%.
2. **Custom back buttons that break swipe-back**: Ensure the swipe-from-left-edge gesture still works via `NavigationStack`.
3. **Full-screen blocking spinners**: Use skeleton views or inline progress indicators.
4. **Splash screens with logos**: The launch screen must mirror the first screen of the app.
5. **Requesting all permissions at launch**: Guarantees most will be denied.
6. **Hardcoded font sizes**: Use text styles. Hardcoded sizes ignore Dynamic Type and accessibility preferences.
7. **Using only color to indicate state**: Red/green for valid/invalid excludes colorblind users. Always pair with icons or text.
8. **Alerts for non-critical information**: Use banners, toasts, or inline messages.
9. **Hiding the tab bar on push**: Tab bars should remain visible throughout navigation within a tab.
10. **Ignoring safe areas**: Using `.ignoresSafeArea()` on content views causes text and buttons to disappear under the notch, Dynamic Island, or home indicator.
11. **Non-dismissable modals**: Every modal must have a clear dismiss path.
12. **Custom gestures without alternatives**: Provide a visible button or menu item as well.
13. **Tiny touch targets**: Buttons and links smaller than 44pt cause mis-taps.
14. **Stacked modals**: Use navigation within a single modal instead of presenting a sheet on top of a sheet.
15. **Dark Mode as an afterthought**: Always use semantic colors.

## Verification
- [ ] All interactive elements have a minimum tap target of 44x44 points.
- [ ] Safe areas are respected (no content under status bar, Dynamic Island, or home indicator).
- [ ] Dynamic Type scales text up to 200% without truncating or clipping.
- [ ] All text meets WCAG AA contrast ratios: 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt+ bold).
- [ ] VoiceOver reads elements in a logical order with meaningful labels.
- [ ] Reduce Motion disables decorative animations.
- [ ] Increase Contrast variant exists for custom colors.
- [ ] All gestures have alternative access paths.
- [ ] Alerts are used only for critical decisions.
- [ ] Sheets have a dismiss path (button and/or swipe).
- [ ] List rows are at least 44pt tall.
- [ ] Tab bar is never hidden during navigation.
- [ ] Destructive buttons use the `.destructive` role.
- [ ] Permissions are requested in context, not at launch.
- [ ] Custom explanation shown before each system permission dialog.
- [ ] Sign in with Apple offered alongside other providers.
- [ ] App is usable without an account for basic features.
- [ ] ATT prompt is shown if tracking, and denial is respected.
- [ ] Widgets show glanceable, up-to-date information.
- [ ] App content is indexed for Spotlight.
- [ ] Share Sheet is available for shareable content.
- [ ] App handles interruptions (calls, background, Siri) gracefully.
