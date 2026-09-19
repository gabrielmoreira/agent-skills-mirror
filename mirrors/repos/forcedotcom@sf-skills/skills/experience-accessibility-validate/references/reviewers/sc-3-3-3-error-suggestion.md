## SC 3.3.3 - Error Suggestion (Level AA)

If an input error is automatically detected and suggestions for correction are known, then the suggestions are provided to the user, unless it would jeopardize the security or purpose of the content.

## SC: 3.3.3 - Error Suggestion

**What is a Sufficient Error Suggestion?**

A suggestion is sufficient if it clearly states the correction needed. You should not flag messages that are already clear just to make them more verbose. The goal is to ensure a corrective suggestion exists, not to rewrite it.

- **Sufficient Suggestion Examples (DO NOT FLAG these as violations):**

  - For an input field that requires only numbers, use a clear and direct error message. For example, "Please enter numbers only."
  - For a password confirmation that doesn't match, use a clear and direct error message: For example, "Passwords do not match."

- **Insufficient Suggestion Examples (These SHOULD BE FLAGGED):**
  - "Invalid input."
  - "Access Denied."
  - "Error."
  - "Please fix this field."

For each form field that can produce an input error, check the following:

- The form field provides a clear error message that indicates what went wrong and how it can be fixed, when an input error is detected.
- The error message includes a suggestion for correcting the error. Some examples include, requiring a specific format, requesting acceptable values, or defining a valid range of values.
- If the input requires a specific format (for example, a date or email format), the error message suggests that the user input their information using that format. The error message suggestion can be present either in input error messages or validation error messages.
- If the input requires a value from a limited set of values (for example, a drop-down menu) the error message suggests selecting from the available options.
- If the user must validate that they're above a certain age (for example, 18 years or older), the error message must explicitly state that requirement in the error message (for example, "You must be 18 or older to proceed.").
- If the input field has an error message, it must be programmatically associated with the field.
- If error messages are displayed at the top of a component without a clear and direct association to the fields that require a correction, then flag this as an accessibility improvement/violation against WCAG 3.3.1. Also, recommend moving the error messages to a location that directly associates the error to the input field that needs to be corrected.

Common violations to check:

- Missing error messages for input fields that can produce errors.
- Error messages that do not include suggestions for correction.
- Error messages that are unclear or do not guide the user on how to correct the error.
- Error messages that are not visually adjacent (exclude toast messages) to the input field(for example, error message at the top of the form), forcing users to scan the page to locate the field that needs correction.
- Error messages which includes suggestions but are not conveyed to assistive technology. For example, the error suggestion messages and the field are not programmatically associated using `aria-describedby`.

Special Rules:

- Error suggestions should be persistent enough for all users to perceive and understand without arbitrary time limits. The error message must not disappear after certain time limit and should be visible at all times.
- Toast notifications are designed to be accessible and the toast events are designed to follow accessibility guidelines.

**ABSOLUTE AND STRICT EXCLUSION RULES FOR SC 3.3.3 'Error Suggestion':**

- \*\*DO NOT flag that the field "cannot be empty" or that it needs a value for optional fields(not marked as required). The absence of a value is valid for an optional field.
- **DO NOT flag for using `aria-describedby` that references conditionally rendered error messages is valid and common. When the referenced element is not in the DOM, browsers and screen readers handle this gracefully.
  **DO NOT flag for components in the lightning namespace (prefixed with `lightning-`) if there is no form field validation or eror handling or programmatic association. They have built-in, accessible error handling and field validation that complies with WCAG standards.

Rules to follow:

- Find all violations of SC 3.3.3 'Error Suggestion' in the provided HTML and JS files (exclude CSS).
- Focus on form inputs that can produce input errors.
- If no changes or action are needed, then produce an empty list. Do not conclude 'no action is needed' or 'correctly implemented' if no violations found.
- Critically evaluate each field against the specific guidance above. Do not conclude 'no action is needed' or 'correctly implemented' if no violations found.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Associate an error suggestion with the actual focusable control. An `aria-describedby` or `aria-errormessage` on a non-focusable wrapper does not reach a composite editor's internal control unless the wrapper forwards it. A disabled control cannot expose described text on focus. Use adjacent visible guidance, a live region where appropriate, or the control's supported error-association API.
