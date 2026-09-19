## SC 3.3.2 - Labels or Instructions (Level A)

Labels or instructions are provided when content requires user input.

## SC: 3.3.2 - Labels or Instructions

Analyze the given files using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 3.3.2, 'Labels or Instructions'. For all form fields and controls that require user input, ensure that a clear, descriptive label or instruction is provided.

You should analyze all elements in the HTML and identify any controls that require user input, such as inputs, selects, checkboxes, comboboxes, and so on. For each of these controls identified, ensure that a clear and sufficiently contextual label or instruction is provided. These must provide the user with enough information to understand how to successfully input data into the field.

Issues to look for on the page that might signal that labels or instructions are not sufficient, and thus a violation of SC 3.3.2:

- Lack of visible labels on controls
- Missing instructions regarding the expected format for inputs with very specific requirements
- Missing guidance about about allowed characters or constraints for fields with strict requirements
- Labels or instructions conveyed only via placeholder text, which is not visible during input
- Missing required field indicators
- Related field groups lacking proper group labels or individual field identification

The best practice to solve a violation is to **provide descriptive labels/instructions** and do one of the following\*\*:

- Use `aria-describedby` to provide a descriptive label
- Use `aria-labelledby` to concatenate a label from several text nodes
- Use grouping roles to identify related form controls
- Provide expected data format and example
- Providing text instructions at the beginning of a form or set of fields that describes the necessary input

Some common implementations of the aforementioned patterns are:

- Visible text labels using `<label>` with proper `for`/`id` relationships
- Specific text instructions for controls with specific requirements/constraints
- Mark required fields clearly with visual indicators (\*, Required) in the label or instructions
- Group related fields using `fieldset`/`legend` or appropriate ARIA grouping roles
- For design-constrained situations, use appropriate combinations of `title`, `aria-label`, or `aria-labelledby`
  - These could be situations where a visible label can not be specifically assigned to each control in a grouped interface

Rules to follow:

- Find all violations of SC 3.3.2 'Labels or Instructions' in the provided HTML and JS files.
- If no changes are needed, then produce an empty list.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Attach instructions to the actual focusable control. An `aria-describedby` on a disabled control cannot expose the instructions on focus, and an association on a non-focusable wrapper does not reach a composite editor's internal control unless the wrapper forwards it. Use adjacent visible instructions or the control's supported association API instead.
