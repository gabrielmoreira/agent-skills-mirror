## SC 2.1.1 - Keyboard (Level A)

All functionality of the content is operable through a keyboard interface without requiring specific timings for individual keystrokes, except where the underlying function requires input that depends on the path of the user's movement and not just the endpoints.

## SC: 2.1.1 - Keyboard

Analyze the given file using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 2.1.1, 'Keyboard'.

**Scope — this criterion applies to _interactive_ elements only; native controls pass.** A violation requires an element that is operable by mouse/pointer (a click/pointer/mouse handler, or a custom control role) but is **not** equivalently operable by keyboard. Before flagging anything, apply these two gates — an element that clears them **passes** and must not be flagged:

- **Native interactive HTML is keyboard-operable for free.** `<a href>`, `<button>`, `<input>` (including `type="checkbox"`, `type="radio"`, `type="submit"`, etc.), `<select>`, `<textarea>`, and `<summary>` receive focus and handle keyboard activation by default. Do **not** flag a native control for a missing `tabindex`, missing keyboard handler, or keyboard inoperability unless its native behavior has been explicitly overridden or suppressed.
- **Non-interactive elements are out of scope.** A `<div>`, `<span>`, `<li>`, `<p>`, etc. that has **no** click/pointer/key handler and no interactive role is not a control — it does not need `tabindex` and must not be flagged. Only a non-semantic element that _carries a click/pointer handler_ (making it a de-facto control) needs `tabindex="0"` plus a keyboard handler.

For an element that is in scope (an interactive control), ensure it exposes via keyboard all interactivity achievable via mouse; if it does not, flag it as a violation. The exception is when the underlying functionality requires path-based movement.

Interactive controls must be accessible when using the keyboard alone, and when using a keyboard along with assistive technology, such as a screen reader, without requiring specific timings for keystrokes. The exception to this is when the underlying functionality requires path-based movement.

Common modes of failure for this rule are:

- Custom input implementations don't have an equivalent keyboard functionality. For example, an element with click or pointer handlers, but no equivalent functionality for keypress.
- Elements that can't be navigated to via the keyboard but can be interacted with via the mouse. For example, an interactive element that's missing a `tabindex`, either because it doesn't have one by default or it hasn't been explicitly assigned.
- Tooltips that are only accessible through mouse hover. For example, an element that displays a tooltip on mouse hover, however, there is no way to access the tooltip via keyboard. The tooltip should be accessible via hover, keyboard and click.
- Anchor (`<a>`) elements that are used as interactive controls (e.g., with `onclick` or have an `onclick` attribute) and don't have an `href` attribute aren't focusable or operable via keyboard. This is a violation. Use a `button` element or ensure that the anchor has an `href` and is accessible via the keyboard.
- **Incorrect Tab Indices**: When a parent element has `tabindex="0"` but its child interactive element has `tabindex="-1"`, this creates a keyboard trap. The parent becomes focusable but the child button/link cannot be activated via keyboard. Always flag this pattern as "Incorrect Tab Indices".
- **Tabindex out of sequence**: When `tabindex` values are greater than 0, they disrupt the natural keyboard navigation order. Flag any `tabindex` with positive values (1, 2, 10, etc.) as violations that need to be removed.
- **DIV elements with event handlers**: Non-semantic elements (`div`, `span`) with click handlers must have `tabindex="0"` to be keyboard accessible. Without `tabindex`, they cannot receive focus.

Given the common modes of failure, consider:

- Is the control using semantic HTML? If the semantic HTML default behaviors aren't overridden and new mouse functions aren't added, it will work with a keyboard. Don't flag this as a violation.
- Is the control focusable? If the control is focusable, it can properly handle a keyboard event. Don't flag this as a violation.
- Does anything override the focus event? If native focus is allowed, then nothing will override the focus event and elements should receive and handle focus events correctly. If the focus is altered, elements might not receive or handle focus events correctly.

**SPECIFIC TABINDEX PATTERNS TO IDENTIFY:**

1. **Parent-Child Tabindex Conflicts**: Scan for `<li tabindex="0">` containing `<button tabindex="-1">` or similar patterns where parent is focusable but child interactive element is not.
2. **High Tabindex Values**: Look for any `tabindex="X"` where X > 0 (like `tabindex="10"`, `tabindex="5"`). These disrupt natural tab order.
3. **Semantic Elements with Unnecessary Tabindex**: Buttons, links, and form controls don't need explicit `tabindex` values.

Rules to follow:

- Find all violations of SC 2.1.1 'Keyboard' in the provided HTML and JS files.
- DO NOT flag issues when native HTML elements provide sufficient keyboard accessibility.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Prefer a real `<button>` for actions. If an anchor must act as a control, use the canonical SLDS `href="#"` plus `event.preventDefault()` pattern and supply the complete button-like semantics and keyboard behavior. Do not recommend `href="javascript:void(0)"` as a first-line fix, and do not flag that value alone as a keyboard violation.
