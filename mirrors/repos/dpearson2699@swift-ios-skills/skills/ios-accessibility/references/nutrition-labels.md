# App Store Accessibility Nutrition Labels

App Store Connect lets you declare which accessibility features your app
supports. These labels appear on your product page, helping users find apps
that meet their needs.

Docs: [Overview of Accessibility Nutrition Labels](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/overview-of-accessibility-nutrition-labels)

## The 9 Label Categories

| Label | What It Means | Key Implementation |
|-------|---------------|-------------------|
| **VoiceOver** | App is fully navigable and usable with VoiceOver | All controls have accessibility labels; images have descriptions; custom views use `accessibilityElement(children:)` |
| **Full Keyboard Access** | App supports complete keyboard navigation | All interactive elements are focusable; keyboard shortcuts for key actions; no touch-only gestures required |
| **Switch Control** | App works with external switch devices | All actions reachable through scanning; no timing-dependent interactions; custom actions via `accessibilityCustomContent` |
| **Voice Control** | App responds to voice commands | All buttons and controls have visible or accessibility labels matching voice command targets |
| **Closed Captions / SDH** | Media includes closed captions or subtitles for the deaf and hard of hearing | AVPlayer content tagged with `transcribesSpokenDialogForAccessibility` and `describesMusicAndSoundForAccessibility` |
| **Audio Descriptions** | Media includes narrated descriptions of visual content | Audio tracks tagged with `describesVideoForAccessibility` |
| **Larger Text** | App supports Dynamic Type at all sizes | All text uses `UIFont.preferredFont(forTextStyle:)` or SwiftUI's default text styles; layouts adapt without truncation through Accessibility XXL sizes |
| **Reduce Motion** | App respects the Reduce Motion setting | Check `UIAccessibility.isReduceMotionEnabled` or `@Environment(\.accessibilityReduceMotion)`; provide non-animated alternatives |
| **Increase Contrast** | App respects the Increase Contrast setting | Use semantic colors (system colors adapt automatically); check `UIAccessibility.isDarkerSystemColorsEnabled` for custom elements |

## Pass / Fail Criteria

To legitimately claim a label, your app must pass real testing with that
assistive technology. Apple may audit these claims.

### VoiceOver Pass Criteria

- Every interactive element has a meaningful `accessibilityLabel`
- Decorative images are hidden (`accessibilityHidden(true)` or `.decorative`)
- Custom views expose children or combine into logical elements
- No information is conveyed only through color, shape, or position
- All alerts, toasts, and dynamic content are announced via `UIAccessibility.post(notification:argument:)`
- Navigation order is logical (top-to-bottom, leading-to-trailing)

### Full Keyboard Access Pass Criteria

- All actions achievable without touch
- Clear focus indicators visible on all interactive elements
- Tab order follows visual layout
- Keyboard shortcuts don't conflict with system shortcuts
- No dead-end focus traps

### Closed Captions Pass Criteria

- All spoken dialog is captioned
- Sound effects relevant to comprehension are described in brackets
- Speaker identification is included when multiple speakers are present
- Captions are synchronized with audio
- Captions use `AVMediaCharacteristic.transcribesSpokenDialogForAccessibility`

### Audio Descriptions Pass Criteria

- Visual-only information (actions, scene changes, on-screen text) is narrated
- Descriptions fit between dialog without overlapping
- Audio description tracks tagged with `AVMediaCharacteristic.describesVideoForAccessibility`

### Larger Text Pass Criteria

- App uses Dynamic Type (preferred font text styles)
- No text is clipped or truncated at Accessibility sizes (up to AX5)
- ScrollViews accommodate expanded content
- Images with text provide scaled alternatives

### Reduce Motion Pass Criteria

- `@Environment(\.accessibilityReduceMotion)` or `UIAccessibility.isReduceMotionEnabled` checked
- Parallax, sliding, and spring animations replaced with fades or instant transitions
- Auto-playing animations are paused or replaced with static content

### Increase Contrast Pass Criteria

- System semantic colors used (they auto-adapt)
- Custom colors provide higher-contrast variants when `accessibilityContrast == .high`
- Borders or other visual separators added for elements that rely on subtle color differences

## SwiftUI Audit Example

```swift
struct ContentView: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.dynamicTypeSize) private var typeSize

    var body: some View {
        VStack {
            Image("hero")
                .accessibilityLabel("Mountain landscape at sunset")

            Text("Welcome")
                .font(.title)   // Uses Dynamic Type automatically

            Button("Get Started") { }
                .accessibilityHint("Opens the onboarding flow")
        }
        .animation(reduceMotion ? nil : .spring(), value: showContent)
    }
}
```
