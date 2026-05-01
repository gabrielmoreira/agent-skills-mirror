# Multi-Platform Focus Patterns

Platform-specific focus behaviors beyond the common SwiftUI and UIKit patterns
covered in the main SKILL.md.

## Contents

- [tvOS Focus](#tvos-focus)
- [watchOS Focus](#watchos-focus)
- [visionOS Focus](#visionos-focus)
- [macOS Focus](#macos-focus)

## tvOS Focus

tvOS uses a **geometric focus model**: the focus engine evaluates the spatial
positions of focusable items and moves focus in the direction the user swipes
on the Siri Remote.

### Key Differences from iOS

- All interactive elements must be focusable — there is no touch.
- The focus engine moves focus automatically based on geometry; you cannot
  programmatically set focus to an arbitrary item without the engine's consent.
- `UIFocusEnvironment.preferredFocusEnvironments` determines the preferred
  destination when focus enters a container.
- `UIFocusUpdateContext` provides `previouslyFocusedItem`, `nextFocusedItem`,
  `focusHeading`, and `animationCoordinator`.

### UICollectionView Focus on tvOS

```swift
override func collectionView(
    _ collectionView: UICollectionView,
    canFocusItemAt indexPath: IndexPath
) -> Bool {
    // Prevent focus on disabled cells
    let item = dataSource.itemIdentifier(for: indexPath)
    return item?.isEnabled ?? false
}

override func collectionView(
    _ collectionView: UICollectionView,
    didUpdateFocusIn context: UIFocusUpdateContext,
    with coordinator: UIFocusAnimationCoordinator
) {
    coordinator.addCoordinatedFocusingAnimations { _ in
        context.nextFocusedView?.transform = CGAffineTransform(scaleX: 1.1, y: 1.1)
    } completion: {}
    coordinator.addCoordinatedUnfocusingAnimations { _ in
        context.previouslyFocusedView?.transform = .identity
    } completion: {}
}
```

### focusSection() on tvOS

`focusSection()` (tvOS 15+) groups focusable children in SwiftUI so the focus
engine treats them as a navigable region:

```swift
HStack {
    VStack {
        ForEach(sidebarItems) { item in
            Button(item.title) { select(item) }
        }
    }
    .focusSection()

    LazyVGrid(columns: columns) {
        ForEach(gridItems) { item in
            CardView(item: item)
        }
    }
    .focusSection()
}
```

Without `focusSection()`, swiping right from the sidebar might land on a grid
item at the wrong vertical position.

## watchOS Focus

watchOS uses the **Digital Crown** as its primary navigation input alongside
touch. SwiftUI provides `digitalCrownRotation(_:)` to track crown input.

Docs: [digitalCrownRotation](https://sosumi.ai/documentation/swiftui/view/digitalcrownrotation(_:from:through:sensitivity:iscontinuous:ishapticfeedbackenabled:))

```swift
struct CrownScrollView: View {
    @State private var offset: Double = 0

    var body: some View {
        ScrollView {
            VStack {
                ForEach(items) { item in
                    ItemRow(item: item)
                }
            }
        }
        .digitalCrownRotation($offset, from: 0, through: 100)
    }
}
```

Focus on watchOS is simpler than tvOS — most views are linearly scrollable
and focus is implicit via the crown/scroll position.

## visionOS Focus

visionOS uses **gaze and hand tracking** for focus. The system determines
which element the user is looking at and highlights it. Pinch gestures act
as taps.

### Hover Effects

All interactive elements get automatic hover effects in visionOS. Customize
with `.hoverEffect(_:)`:

```swift
Button("Action") { }
    .hoverEffect(.highlight)  // Default for buttons
    .hoverEffect(.lift)       // Raises the element
```

### RealityKit Focus

In RealityKit scenes, use `InputTargetComponent` and `HoverEffectComponent`
to make entities respond to gaze:

```swift
let entity = ModelEntity(mesh: .generateBox(size: 0.1))
entity.components.set(InputTargetComponent())
entity.components.set(HoverEffectComponent())
entity.components.set(CollisionComponent(shapes: [.generateBox(size: [0.1, 0.1, 0.1])]))
```

### Accessibility in visionOS

Users who cannot use gaze tracking rely on Switch Control, Voice Control,
or pointer devices. Ensure all focusable elements have proper accessibility
labels and traits.

## macOS Focus

### Key View Loop

UIKit-based macOS Catalyst apps and AppKit apps use the key view loop to
determine Tab order. `NSView.nextKeyView` chains views together.

SwiftUI on macOS uses `@FocusState` identically to iOS, with Tab moving
focus between fields by default.

### NSView Focus

```swift
// AppKit: make a custom view focusable
class CustomControl: NSView {
    override var acceptsFirstResponder: Bool { true }
    override var canBecomeKeyView: Bool { true }

    override func becomeFirstResponder() -> Bool {
        needsDisplay = true
        return true
    }

    override func resignFirstResponder() -> Bool {
        needsDisplay = true
        return true
    }
}
```

### Full Keyboard Access

macOS Full Keyboard Access (System Settings → Keyboard → Keyboard Navigation)
enables Tab focus on all controls, not just text fields. Test your app with
this setting enabled.
