---
title: CSS
category: Language
x-claim-provenance:
- claim: The cascade sorts declarations by origin and importance before cascade layers, and by layers before specificity; for normal declarations the last layer wins and unlayered declarations are treated as an implicit final layer, while for important declarations the first layer wins.
  source: https://www.w3.org/TR/css-cascade-5/
- claim: In forced colors mode the user agent forces the color components of properties including color, background-color, border-color, and outline-color, computes box-shadow and text-shadow to none, removes background images that are not url() references, and forced-color-adjust none exempts an element.
  source: https://www.w3.org/TR/css-color-adjust-1/
- claim: WCAG 2.2 success criterion 1.4.10 Reflow requires content to be presented without loss of information or functionality and without two-dimensional scrolling at a width equivalent to 320 CSS pixels for vertical-scrolling content or a height of 256 CSS pixels for horizontal-scrolling content, and 320 CSS pixels equals a 1280 CSS pixel viewport at 400% zoom.
  source: https://www.w3.org/WAI/WCAG22/Understanding/reflow.html
---

The supported browsers, viewport and input ranges, writing modes, zoom and text scaling, color schemes, forced-colors behavior, reduced-motion preference, and build or scoping pipeline define the CSS environment. Properties, selectors, queries, and value syntax are available only where the project's supported browser versions and transformation pipeline establish support.

Among competing declarations, origin and importance are compared before cascade layers, and layers before specificity and source order. A simple selector in a later layer therefore beats a more specific one in an earlier layer, unlayered styles act as the last layer, and for `!important` declarations the order reverses so the earliest layer wins. Selector specificity, layers, custom properties, containment, and component boundaries together form a cascade contract, and local patches against that contract accumulate conflicts. Layout primitives follow the content relationship, and the result runs through inheritance, computed values, formatting context, containing block, stacking context, overflow, intrinsic sizing, and replaced-element behavior.

Styles are also applied indirectly, through:

- global resets and normalized styles
- CSS modules or generated class names, shadow roots, and component encapsulation
- inline styles and runtime class toggles
- animation and transition rules and media or container queries

User settings override author styles in ways a default rendering hides. In forced colors mode the browser replaces the author's colors for text, backgrounds, borders, and outlines and computes `box-shadow` and `text-shadow` to `none`, so a focus indicator drawn only with a shadow disappears. Characteristic failures arise where DOM order, accessible states, focus indication, hidden content, fonts, localization, long content, and browser defaults interact with the visual result.

Cross-environment evidence comes from each affected supported browser with representative viewports, zoom, text scaling, input modes, themes, fonts, writing direction, content lengths, and interaction states. Accessibility tooling and direct interaction are the evidence for keyboard focus, contrast, forced colors, reduced motion, reflow, clipping, hit targets, and DOM-versus-visual order; WCAG's reflow criterion, for example, is judged at a width of 320 CSS pixels, which a 1280-pixel viewport reaches at 400% zoom. Computed-style, layout, paint, and performance evidence from the actual browser shows what the cascade produced, a screenshot does not prove semantic or interactive behavior, and an optimization must preserve cascade boundaries.
