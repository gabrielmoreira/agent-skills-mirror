## SC 2.4.6 - Headings and Labels (Level AA)

Headings and labels describe topic or purpose.

## SC: 2.4.6 - Headings and Labels

This success criterion strictly concerns the content itself when such content is present, and does not address the following concerns, which are handled by different criteria:

- Heading or label markup or identification. These requirements are separately covered by 1.3.1 'Info and Relationships'
- Alternative accessible name methods linked to headings or labels. These requirements are separately covered by 4.1.2 'Name, Role, and Value'
- Whether a label is present or not. 3.3.2 'Labels or Instructions' handles the use of labels.

EXTREMELY IMPORTANT: For WCAG SC 2.4.6 'Headings and Labels' (Level AA), your ONLY task is to identify if an already present and identifiable heading or label is indescriptive, unclear, or ambiguous in its purpose or topic.

You MUST NOT report any issue where an accessible name (label) is entirely absent for an interactive element (like a button or link acting as a button), regardless of whether it uses an `aria-label`, `aria-labelledby`, or visible text content via a slot.

Specifically, you MUST NOT generate an output of type: "Missing aria-label or explicit label" or type: "Missing aria-labelledby Attribute" under ANY circumstances for SC 2.4.6.

Issues where an interactive element completely lacks an accessible name (e.g., `<a class="slds-button"></a>` with an empty slot or no text) fall under WCAG SC 4.1.2 'Name, Role, Value'. These are not 2.4.6 violations. Similarly, issues of missing labels for user input are 3.3.2.

For 2.4.6, if an element has no explicit label/name at all, you are to IGNORE IT. Only if a label/name exists (e.g., `<button>Edit</button>` or `<h1 id="x">...</h1>` `<label for="y">`...), then assess if that existing label/name is descriptive enough. Do NOT suggest adding an `aria-label` or `aria-labelledby` if none is present."

Analyze the given file using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 2.4.6, 'Headings and Labels'. For all headings or labels on the page, ensure the content is clear, descriptive, and contextually describes the content with which it's associated to determine if they meet SC 2.4.6. If they do not, then flag this as a violation.

Notes:

- Headings should be descriptive such that it's easy to understand what its associated section may contain. For example, a page that displays contact information can have a heading like "Contact Information" or "Main Contact".
- Form-related labels should clearly convey what type of input is required from the user. For example, name fields can have labels like "Salutation", "First Name", and "Last Name".

When flagging a violation, you should calculate an importance level: 'low', 'medium', or 'high'. This WCAG rule is often a matter of subjectivity and context, so we only want to include violations for which there is a high level of importance that it is fixed. The following can be used to assess importance level:

- Low: A given label or heading may not technically be descriptive, but a compelling argument could also be made that the element is sufficiently descriptive given context or some other unique subjective reading of the value.
- Medium: A given label or heading is lacking some potentially minor valuable information. There are better options for the heading or label value, but it's not strictly required in order to provide an accessible experience in all scenarios.
- High: A given label or heading is vague and unclear. If this issue is not corrected, then the code at hand is to be considered an objective and outright violation of WCAG rule 2.4.6. It is definitively a violation.

IMPORTANT: When evaluating the descriptiveness of headings or labels for SC 2.4.6, if the label's value is a variable (e.g., `aria-label={someVariable}`), you MUST assume it is compliant and descriptive, and therefore, you MUST NOT report it as a violation. This is particularly true if the variable might refer to an imported label for localization or dynamic content. Your analysis of descriptiveness for 2.4.6 should ONLY apply to hardcoded string values that are visibly present in the HTML/markup provided.

Rules to follow:

- Find all violations of SC 2.4.6 'Headings and Labels' in the provided HTML and JS files.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
