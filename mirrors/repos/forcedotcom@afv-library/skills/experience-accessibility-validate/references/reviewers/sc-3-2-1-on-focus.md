## SC 3.2.1 - On Focus (Level A)

When any user interface component receives focus, it does not initiate a change of context.

## SC: 3.2.1 - On Focus (Level A)

Analyze the files using following context:

_Goal_: Ensure components behave predictably when receiving focus. Avoid unexpected context changes triggered by focus alone; as it can disorient users, especially those using assistive technologies or with cognitive limitations.

_What to do_: Review the provided HTML and JS code to identify instances where a component receiving focus initiates a change of context **without** explicit user activation, by use focus event handlers (e.g., onfocus, addEventListener('focus', ...)).

- _Key Definitions_:

  - _Change of Context_: Major changes that can disorient users if unexpected. For SC 3.2.1, this includes actions like automatically submitting a form, launching a new window, or moving focus _away_ from the currently focused component _solely because_ it received focus. Minor changes like opening a tooltip, displaying a non-modal dialog related to the component, or visual styling changes (e.g., focus indicators) are generally **not** considered context changes in this scenario.
  - _Explicit User Activation_: A deliberate action by the user, such as clicking a button, pressing Enter or Space on a focused interactive element. This is distinct from merely setting focus on an element programmatically or via navigation (like tabbing). Context changes should only occur upon explicit user activation.

- _Event Handling Context_: Pay close attention to event handling patterns:
  - Inline handlers in HTML templates (e.g., 'onfocus = { handler }').
  - Imperative listeners added in the JavaScript file (e.g., 'element.addEventListener('focus', ...)', methods bound to focus events).

Some examples of violations:

- Form submission triggered automatically on focus of a control.
- Modal dialog opened on focus, before the user activates it.
- Dropdown menu opened on focus.
- When a component gains focus, it unexpectedly opens new windows.
- Programmatic focus movement to another element as a result of an element receiving focus.
- Script removing focus when an element receives it (e.g., using `onfocus="this.blur()"`).

Following are some sufficient techniques, or combinations of techniques that WCAG working group deems sufficient to meet this success criterion:

- G107: Using "activate" rather than "focus" as a trigger for changes of context. Using a keyboard, cycle focus through all content. Check that no changes of context occur when any component receives focus, including content that normally would otherwise receive focus when accessed by accessible keyboard interactions

Additional advisory techniques (informative):

- G200: Opening new windows and tabs from a link only when necessary
- G201: Giving users advanced warning when opening a new window

Note: Highlighting elements or showing transient tooltips on focus is acceptable if focus alone does not trigger context changes.

_Rules to follow_:

1. Receiving focus must not initiate a change of context. **Context changes require explicit user activation** per sufficient technique G107
2. For each component that violates #1, compile a concise list of issues for user to review, along with an action report on sufficient technique that can help resolve violation for component under review.
3. Keep issues concise and specific to focus-triggered context changes.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
