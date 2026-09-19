## SC 1.4.3 - Contrast (Minimum) (Level AA)

The visual presentation of text and images of text has a contrast ratio of at least 4.5:1, except for large text (at least 3:1), incidental text (part of inactive components, purely decorative, not visible, or part of a picture containing significant other visual content), and logotypes.

## SC: 1.4.3 - Contrast (Minimum) (Level AA)

This reviewer focuses on ensuring enough contrast between text and its background so that it can be read by people with moderately low vision (who do not use contrast-enhancing assistive technology) as well as those with color deficiencies.

### Analysis Framework (What to do):

1.  Identify all visible text elements (e.g., in tags like `<h1>`, `<div>`, `<p>`, `<label>`, `<button>`, etc.).
2.  Determine the **color** (foreground) and **background color** (background) for each text element.
3.  Determine the **font size** and **weight** to classify the text as Standard or Large-Scale.
4.  Calculate the contrast ratio using the WCAG formula: $(L1 + 0.05) / (L2 + 0.05)$, where L1 is the relative luminance of the lighter color, and L2 is the relative luminance of the darker color.
5.  Check if the calculated ratio meets the required threshold (4.5:1 or 3:1).

> **Do not estimate luminance by hand.** Mentally approximating relative luminance is unreliable — it has produced false positives and even different ratios for the _same_ color. Compute the WCAG formula exactly, or for the common grayscale-text-on-white case use this verified reference (sRGB gray `#NNNNNN` on `#FFFFFF`):
>
> | Gray      | Ratio | Standard (4.5:1) | Large (3:1)     |
> | --------- | ----- | ---------------- | --------------- |
> | `#595959` | 7.00  | pass             | pass            |
> | `#666666` | 5.74  | pass             | pass            |
> | `#767676` | 4.54  | pass (boundary)  | pass            |
> | `#777777` | 4.48  | **fail**         | pass            |
> | `#808080` | 3.95  | fail             | pass            |
> | `#959595` | 3.00  | fail             | pass (boundary) |
> | `#999999` | 2.85  | fail             | **fail**        |
> | `#AAAAAA` | 2.32  | fail             | fail            |
> | `#BBBBBB` | 1.92  | fail             | fail            |
>
> Rule of thumb for grayscale on white: `#767676` is the standard-text boundary — anything **darker** (lower hex value) passes 4.5:1; `#959595` is the large-text boundary for 3:1. In particular, **`#666666` and darker pass standard-text contrast — do not flag them.** For non-grayscale colors, non-white backgrounds, gradients, or alpha compositing, compute the exact ratio; if you cannot, do not guess — only flag when you are confident the ratio is below threshold.

### Goals for Contrast Compliance:

1.  **Standard Text (Ratio 4.5:1):**
    - **Good:** Black text on a white background (Ratio 21:1).
    - **Bad:** Light gray text on a white background (e.g., #AAAAAA on #FFFFFF, Ratio 2.32:1).
2.  **Large-Scale Text (Ratio 3:1):**
    - **Good:** Medium gray text on a white background (e.g., #808080 on #FFFFFF, Ratio 3.95:1 — passes large-text 3:1 but fails standard-text 4.5:1).
    - **Bad:** Light gray text on a white background (e.g., #BBBBBB on #FFFFFF, Ratio 1.92:1).
3.  **Focus/Hover States:** While the primary check is for the default state, flag any explicit color changes defined in CSS that might reduce contrast below the minimum thresholds during focus or hover states. _(Note: Full dynamic state checking is complex, but hard-coded poor contrast colors must be flagged.)_

### What to Look For:

- Text elements where the foreground color is too similar to the background color.
- Hard-coded color combinations in CSS or inline styles that fail the 4.5:1 or 3:1 ratio.
- Text sizes that are small (Standard Text) but have a contrast ratio less than 4.5:1.
- Text sizes that are large-scale but have a contrast ratio less than 3:1.
- Usage of transparency/opacity that negatively impacts the calculated contrast ratio.

### Common Violations for Contrast:

- **Placeholder Text:** Placeholder text should have enough contrast.
- **Secondary/Hint Text:** Secondary text (e.g., helper text or captions) styled with low-contrast gray colors.
- **Disabled/Inactive Elements:** Though exempt under strict rules, _functional_ elements styled to look inactive when they are not.
- **Text on Complex Backgrounds:** Text placed over gradient or patterned backgrounds where the minimum contrast requirement is not met across the entire text area.

### To fix the Contrast Violations, Use the following techniques:

• **Foreground Color (Text) Fix:**

- **Action:** Locate the style rule (inline style, CSS file, or JS variable) defining the text color.
- **Correction:** If the current color is a light color (e.g., #AAAAAA), change it to a darker, compliant color (e.g., #595959).
- **Priority:** Prioritize using standard, dark text colors (e.g., #333333 or #000000) for accessibility whenever possible.

• **Background Color Fix:**

- **Action:** Locate the style rule defining the element's background-color.
- **Correction:** If the current background-color is a dark color (e.g., #333333), change it to a lighter, compliant color (e.g., #CCCCCC).
- **Priority:** Prioritize using standard, light background colors (e.g., #FFFFFF or #F5F5F5).

• **Inline Style Correction Example:**

- **Violation:** `<div style="color: #AAAAAA; background-color: #FFFFFF;">Low Contrast Text</div>`
- **Fix:** `<div style="color: #444444; background-color: #FFFFFF;">Compliant Contrast Text</div>`

• **Placeholder/Secondary Text Fix:**

- **Action:** For elements like `<input placeholder="text">` or secondary helper text, find the dedicated style (often `:placeholder` or a class for secondary text).
- **Correction:** Ensure the foreground color of the placeholder/secondary text is adjusted to meet at least the 4.5:1 ratio against the background of the input/container.

• **Remediation Strategy:**

- **Goal:** Modify the least number of color declarations (either `color` or `background-color`) necessary to achieve the target ratio (4.5:1 for standard text, 3:1 for large text).
- **Method:** If foreground text is light, darken it. If foreground text is dark, lighten the background.
- **Context:** Only modify color values (#RRGGBB, rgb(), hsl()) found in inline styles or referenced CSS blocks identified by the analysis.

## Exemptions (DO NOT FLAG):

1.  **Decorative:** Text used purely for decorative purposes, where its specific lettering is not essential to understanding the content (e.g., text used as a stylized border).
2.  **Logotypes:** Text that is part of a logo or brand name.
3.  **Inactive UI Components:** Text in components that are disabled (e.g., a grayed-out button).

Rules to follow:

- Focus specifically on **visible text** in HTML and JS files.
- Only flag when the computed ratio falls below 4.5:1 for standard text or 3:1 for large-scale text
- Flag color combinations that result in a contrast ratio **below 4.5:1 for Standard Text**.
- Flag color combinations that result in a contrast ratio **below 3:1 for Large-Scale Text**.
- **Ignore** text clearly marked as decorative, part of a logo, or permanently disabled/inactive components.
- Do not assume or estimate the contrast ratio — compute it exactly, or use the grayscale-on-white reference table above. When the exact ratio is uncertain (gradients, alpha compositing, images behind text, unknown background), do not flag.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
