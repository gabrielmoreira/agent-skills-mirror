## SC 4.1.2 - Name, Role, Value (Level A)

For all user interface components, the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents, including assistive technologies.

## SC: 4.1.2 (ii) - Role Only

Analyze the given file using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 4.1.2, 'Role' ('Name' and 'Value' from this rule should not be considered). For all elements on the page, ensure that the element has the correct role assigned to it in order to determine if they meet SC 4.1.2. If they do not meet this success criterion, flag it as a violation.

**ABSOLUTE AND STRICT EXCLUSION RULES FOR SC 4.1.2 'ROLE' ANALYSIS:**

- **DO NOT flag semantic HTML elements (e.g., `<h1>`-`<h6>`, `<a>`, `<ul>`, `<li>`, `<button>`, `<form>`) if their native implicit role correctly matches their intended function.** These elements **automatically pass** the 'Role' criterion by default.
- **DO NOT flag generic HTML elements (`div`, `span`) used _solely_ for visual layout, styling, or as non-semantic containers.** These elements inherently have no semantic role and **do not require an ARIA role for SC 4.1.2 'Role' compliance**. Do not suggest adding `role="presentation"`, `role="group"`, `role="region"`, or any other role to them unless they are _explicitly_ implemented as a custom interactive control.
- **DO NOT suggest general "semantic structure" improvements (e.g., wrapping in `<section>`), "accessible name" issues (e.g., `aria-label`), "value" issues, or general best practices.** These are **outside the narrow scope** of SC 4.1.2 'Role' analysis.
- **Specifically for `role="separator"`**: ONLY suggest this role if the element is an interactive divider (e.g., a resizable split handle) or a critical, non-interactive semantic divider within an ARIA widget (e.g., within a menu or toolbar). DO NOT suggest it for purely visual lines or spacing.
  **DO NOT flag Salesforce Lightning Base Components (e.g., `lightning-card`, `lightning-record-edit-form`, `lightning-input-field`, `lightning-button`). Assume these components **automatically pass** the 'Role' criterion because Salesforce ensures their roles and basic accessibility are handled implicitly and correctly.** Only flag if a custom override _explicitly breaks_ their inherent role determination, which is highly unlikely in standard usage.

For each of the following role categories, make sure that the given markup contains the relevant role to its intended purpose, either implicitly via semantic HTML, or explicitly via the role attribute. For any markup that is missing a role or uses an invalid role, flag this as a violation and suggest a fix by inferring the purpose of the markup and mapping this to a relevant role or semantic HTML element.

If semantic HTML is used and the programmatic behavior of the markup via Javascript matches its usual function, then this meets the criterion implicitly. This rule targets markup that is used to create custom implementations of controls or interface elements are programmed to behave differently than their implicit purpose.

In determining this, attempt to infer the intent of the code and determine whether the code in question maps to any valid role. Given discretion, if the code reasonably maps to a valid ARIA role, then that role should be used. This means that in some cases there can be code that does not explicitly violate SC 4.1.2 but should be flagged by you to be updated.

Some examples to be considered, but not limited to: - When template loop syntax (e.g., `for:each`, `v-for`, `map()`) or some other list enumeration is present, check if any list related role should be used. Also, consider whether list children also need to be updated with the role relevant to the parent role.

The following roles should be considered:
`toolbar`
`tooltip`
`feed`
`math`
`presentation`
`note`
`application`
`article`
`cell`
`columnheader`
`definition`
`directory`
`document`
`figure`
`group`
`heading`
`img`
`list`
`listitem`
`meter`
`row`
`rowgroup`
`rowheader`
`separator`
`table`
`term`
`scrollbar`
`searchbox`
`separator`
`slider`
`spinbutton`
`switch`
`tab`
`tabpanel`
`treeitem`
`combobox`
`menu`
`menubar`
`tablist`
`tree`
`treegrid`
`banner`
`complementary`
`contentinfo`
`form`
`main`
`navigation`
`region`
`search`
`alert`
`log`
`marquee`
`status`
`timer`
`alertdialog`
`dialog`

Also make sure to check that relationships between roles are present. For roles that require some role in its descendant tree, ensure that an element in the child subtree has that role. Inversely, for roles that require some role in its ancestor tree, ensure that some parent has that role. Any case in which these requirements are not met should be flagged as a violation. For example, a `listitem` role on a child element must be matched with a `list` role on a parent element.

Do not use Abstract Roles.

Rules to follow:

- Find all violations of SC 4.1.2 'Role' in the provided HTML and JS files.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
- Prefer a real `<button>` for actions. Do not recommend `href="javascript:void(0)"` as a role fix: that value alone does not give an anchor button semantics. If converting the anchor is impossible, any anchor-based remediation must provide the complete role and keyboard behavior needed for an accessible button. Do not flag an existing `javascript:void(0)` value by itself as a role violation.
