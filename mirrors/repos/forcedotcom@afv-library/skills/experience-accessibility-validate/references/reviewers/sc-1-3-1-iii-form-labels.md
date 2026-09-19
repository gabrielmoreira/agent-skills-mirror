## SC 1.3.1 - Info and Relationships (Level A)

Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

## SC: 1.3.1 (iii) - Info and Relationships - Form Labels

Key Requirements:

1. Every form control must have a programmatic label via one of these methods:

- Label must be `<label>` with matching `for`/`id` attributes.
- `aria-label`/`aria-labelledby` (when visual labels are not feasible)
- `label` attribute, on `lightning-` prefixed namespace components (when applicable).

2. Label Content:

- Must be descriptive and meaningful
- No nested interactive elements
- Not just placeholder or title text
- Group controls need group and individual labels

3. Common Issues:

- Missing or empty labels
- Non-matching `for`/`id` attributes
- Placeholder text as labels
- Nested interactive elements in labels

4. Improper Label Content: Nested Interactive Elements:

- Examine the content of all label elements.
- Ensure no `<label>` contains interactive HTML elements as direct children or descendants. This includes:
  - `<a>`, `<button>`, `<summary>` or any custom elements with interactive roles.

Following are some sufficient techniques that a user can use to meet this success criterion:

Form controls must have programmatically associated labels that clearly identify their purpose.

Required Label Associations:

1. Standard HTML Elements:
   - All input types (`text`, `date`, `email`, `number`, `password`, `search`, `checkbox`, etc.)
   - `select`, `textarea` elements

Some cases where the `label` HTML element is ignored:

- `button` element when the label is provided by the content
- `input type="button"` when the label is provided by the content
- `input type="hidden"`
- `input type="image"` when the label is provided by the `alt` attribute
- `input type="reset"` when the label is provided by the `value` attribute
- `input type="submit"` when the label is provided by the `value` attribute
- `input type="search"` when there is a `button` element with label next to search `input`

Exceptions (No Label Required):

- Buttons with descriptive content
- Hidden inputs
- Image inputs with alt text
- Submit/reset with value text

If they do not meet this success criterion, then flag this as a violation.

Trace how the control's own accessible name is provided in the source before flagging a missing or unassociated label. Valid sources include a `<label>` that contains the control, a `<label for>` / `<label htmlFor>` whose value matches the control's `id`, an `aria-label`, an `aria-labelledby` target, or a self-labeling component prop on an imported/custom control such as `<Input>` or `<TextField>` (see the general rules). An adjacent `<label>` is not sufficient unless it contains the control or has a matching `for` / `htmlFor` association. A `<fieldset><legend>` or named `role="group"` / `role="radiogroup"` supplies group context but does **not** name each descendant control. A dynamic `for` / `htmlFor` and its control's `id` bound to the **same expression** are matched, even when the literal value cannot be resolved at review time (see the general rules). Only flag when none of the valid control-level naming mechanisms supplies the name.

Rules to follow:

- Find all violations of SC 1.3.1 (iii) 'Form Labels' in the provided HTML and JS files
- Report only form label violations
- Provide specific control and issue details
- Keep reports concise and non-redundant

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- ARIA attribute spelling depends on the element type. Plain HTML elements use `aria-labelledby` and `aria-describedby`; `aria-labelled-by` or `aria-described-by` is invalid there. On an LWC component tag, however, the hyphen-split spelling can be the kebab-case binding for an `@api ariaLabelledBy` or `ariaDescribedBy` property. Do not report the component spelling as a broken association without evidence that the component fails to forward it.
- Attach label associations to the actual focusable control. A `for`, `htmlFor`, or ARIA relationship on a non-focusable wrapper around a composite editor does not label the internal control unless the wrapper forwards it. Recommend extending the control to accept or forward the association, or using its supported labeling prop.
