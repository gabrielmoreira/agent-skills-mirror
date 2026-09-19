## SC 1.3.1 - Info and Relationships (Level A)

Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

## SC: 1.3.1 (iv) - Info And Relationships - Regions (A)

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 1.3.1 (iv), 'Info and Relationships'
(Only regions from this rule should be considered). For all regions on the page, ensure that any information conveyed through presentation is programmatically determinable in order to determine if they meet SC 1.3.1 (iv).
If they do not meet this success criterion, flag it as a violation.

Rules to follow:

- Find all violations of SC 1.3.1 'Info and Relationships - Regions' in the provided HTML and JS files.
- Do not worry about violations of SC 1.3.1 that are not specific to regions. These will be handled by other reviewers.
- Use semantic HTML elements (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`, `<section>`) to mark up regions. There cannot be more than one `<main>` element that does not have a hidden attribute specified.
- When semantic elements cannot be used, use ARIA landmark roles (`role="banner"`, `role="navigation"`, `role="main"`, `role="complementary"`, `role="contentinfo"`, `role="region"`).
- Each region should have a descriptive label or heading that identifies its purpose.
- Regions should be properly nested and not overlap.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
