## SC 2.4.4 - Link Purpose (In Context) (Level A)

The purpose of each link can be determined from the link text alone or from the link text together with its programmatically determined link context, except where the purpose of the link would be ambiguous to users in general.

## SC: 2.4.4 - Link Purpose (In Context)

Analyze the given file using the following framework:

Review the provided HTML file for accessibility violations per WCAG 2.2 SC 2.4.4, 'Link Purpose (In Context)'. For all anchor elements (`<a>`) and other interactive elements that function as links, ensure that the link text is descriptive enough to convey the purpose of the link, either on its own or with its immediate context (such as the same sentence, list item, or table cell). If the link purpose cannot be determined, flag this as a violation.

Common modes of failure for this rule are:

- Using vague link text such as 'click here', 'read more', or 'more' without sufficient context. (Type: "Vague Link Text")
- Relying on context that is not programmatically associated with the link (e.g., context that is visually near but not in the same sentence, list item, or table cell).
- Using only an icon or image as a link without accessible text or an appropriate accessible name, such as an `aria-label`. (Type: "Non-descriptive Icon Link")
- Multiple links using the same non-descriptive text (e.g., "Read more") but pointing to different destinations. (Type: "Duplicate Link Text")

For each violation, provide:

- The exact type as listed above.
- A detailed description of why it is a problem, referencing accessibility best practices.
- An intent analysis explaining what the developer likely intended.
- A suggested action, with precise recommendations (e.g., for icon links, recommend adding an `aria-label`, not just alt text).
- For duplicate link text, identify and report all instances, not just the first.

Rules to follow:

- Find all violations of SC 2.4.4 'Link Purpose (In Context)' in the provided HTML file.
- If no changes are needed, then produce an empty list.
- Use the exact terminology for issue types as listed above.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Judge whether link text describes its destination, not whether the destination opens in a new window. `target="_blank"` and click handlers that call `window.open(...)` are not SC 2.4.4 failures. If new-tab behavior is mentioned, describe indicating it as an optional enhancement rather than a warning or violation.
