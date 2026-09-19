## SC 1.1.1 - Non-text Content (Level A)

All non-text content that is presented to the user has a text alternative that serves the equivalent purpose, except for specific situations such as controls or input, time-based media, test, sensory, CAPTCHA, and decoration or formatting.

## SC: 1.1.1 - Non-text Content (All Images)

This reviewer focuses on both decorative and informative images and their proper accessibility handling.

### Definition of Decorative Image:

A decorative image is one that:

- Provides no information content
- Is used for visual formatting, spacing, or decoration
- Does not convey meaning or context
- Is not essential to understanding the content

### Definition of Informative Image:

An informative image is any image that conveys information, meaning, or context that is essential to understanding the content or functionality of a webpage or application.

### Analysis Framework(What to do):

1. Identify all `<img>` elements in the HTML
2. Determine if each image is decorative or informative
3. Check if decorative images have proper `alt=""` attributes
4. Check if informative images have meaningful descriptive alt text
5. Look for CSS background images that should be used instead
6. Check for ARIA hidden attributes on decorative images

### Goals for Decorative Images:

1. **Empty alt attribute**: Should have `alt=""` for purely decorative images
   - Good: `<img src="decorative-border.png" alt="" />`
   - Bad: `<img src="decorative-border.png" />`
2. **CSS background images**: Should not have alt text as they are not in the accessibility tree
3. **ARIA hidden**: Can use `aria-hidden="true"` for decorative images that must remain in DOM
   - Good: `<img src="spacer.gif" alt="" aria-hidden="true" />`
4. **No redundant text**: Avoid providing descriptive alt text for decorative images
   - Bad: `<img src="decorative-border.png" alt="Decorative border with flowers" />`
5. **Decorative image as link without context**: Add `aria-label` or `title` attribute to the anchor tag
   - Bad: `<a href="/page"><img src="decorative-icon.png" alt="" /></a>`
   - Good: `<a href="/page" aria-label="Navigate to main page"><img src="decorative-icon.png" alt="" /></a>`

### Goals for Informative Images:

1. **Must have alt attribute**: All informative images must have descriptive alt text
   - Good: `<img src="company-logo.png" alt="Our Company Logo" />`
   - Bad: `<img src="chart.png" />`
2. **Meaningful content**: Alt text should describe the information conveyed
   - Good: `<img src="chart.png" alt="Quarterly sales performance chart showing revenue trends" />`
   - Bad: `<img src="chart.png" alt="chart" />`

### What to Look For:

- `<img>` elements without alt attributes (both decorative and informative)
- `<img>` elements with generic alt text like "image", "picture", "photo"
- Decorative images that are not properly marked as decorative
- Informative images with missing or inadequate alt text
- Background images that are incorrectly implemented as `<img>` elements
- Decorative images used in interactive contexts without proper labeling

### Common Violations for Images:

- Missing alt attribute on decorative images
- Missing alt attribute on informative images
- Using `alt="image"` or `alt="picture"` for decorative images
- Providing descriptive alt text for purely decorative images
- Using decorative images as links without proper context
- Including decorative images in the accessibility tree when they should be hidden

Rules to follow:

- Focus specifically on decorative or non decorative images and their alt text handling in the provided HTML and JS files
- Flag missing alt attributes on decorative images
- Flag generic alt text (like "image", "picture") on decorative images
- Flag missing or generic alt text on informative images
- Flag overly descriptive alt text on clearly decorative images
- Consider the context and purpose of each image
- **This reviewer covers `<img>` elements only.** Do **not** flag non-image content: an `aria-hidden="true"` `<span>`, icon-font glyph, emoji, or decorative `<svg>` is intentionally removed from the accessibility tree and is correctly handled — it is not an `<img>` missing alt text. A decorative `<span aria-hidden="true">` is correct, not a violation.

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
