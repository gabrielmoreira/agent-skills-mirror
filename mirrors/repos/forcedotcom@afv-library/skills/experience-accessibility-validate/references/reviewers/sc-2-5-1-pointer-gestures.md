## SC 2.5.1 - Pointer Gestures (Level A)

All functionality that uses multipoint or path-based gestures for operation can be operated with a single pointer without a path-based gesture, unless a multipoint or path-based gesture is essential.

## SC: 2.5.1 - Pointer Gestures

Analyze the given files using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 2.5.1, 'Pointer Gestures'.

Identify functionality that relies on:

1. **Multipoint gestures:** Interactions requiring more than one pointer simultaneously (e.g., pinch-to-zoom, two-finger swipe).
2. **Path-based gestures:** Interactions where the path of the pointer matters, not just the start and end points (e.g., swiping in a specific direction like on a carousel or map, drawing shapes).

For any functionality identified above, determine if it can _also_ be operated using a **single pointer without a path-based gesture**. Examples of single-pointer operations include:

- Taps / Clicks
- Double-taps / Double-clicks
- Long presses / Click-and-hold
- Activating simple controls like buttons, links, or checkboxes.

If functionality requires a multipoint or path-based gesture AND **cannot** be operated by a single pointer alternative (and the complex gesture is not essential\*), then flag this as a violation.

_Essential_: If removing the gesture would fundamentally change the information or functionality, and it cannot be achieved in another way that would conform (e.g., drawing a signature).

Common Violations:

- A carousel that can only be navigated by swiping/dragging, with no previous/next buttons.
- A map that only allows zooming via pinch gestures, with no (+) or (-) buttons.
- An image gallery that requires swiping to browse through images, with no navigation buttons.
- Interactive diagrams that can only be manipulated with multi-touch gestures.

Focus on custom JavaScript logic implementing gesture handling (e.g., touchstart, touchmove, touchend, mousedown, mousemove, mouseup listeners that calculate paths or use multiple points).

Standard browser/OS gestures (like scrolling, history navigation swiping) or AT gestures are not covered by this rule.

Rules to follow:

- Find all violations of SC 2.5.1 'Pointer Gestures' in the provided HTML and JS files.
- If functionality requires multipoint or path-based gestures, verify if a single-pointer alternative exists.
- If no single-pointer alternative exists and the gesture is not essential, report it as a violation.
- If no violations are found, produce an empty list.
- For each issue found, provide a separate, detailed report explaining the gesture and the lack of a single-pointer alternative.
- Assume that imported base components (like lightning-\*) are compliant unless their usage clearly introduces a violation.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
