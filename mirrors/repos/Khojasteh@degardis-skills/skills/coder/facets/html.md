---
title: HTML
category: Language
x-claim-provenance:
- claim: The first rule of ARIA use is to use a native HTML element or attribute with the required semantics and behavior already built in instead of re-purposing an element with an ARIA role, state, or property; interactive ARIA controls must be keyboard usable through scripted behavior, so an element with role=button must receive focus and activate with both Enter and Space.
  source: https://www.w3.org/TR/using-aria/
- claim: The button type attribute's missing value default and invalid value default are the Auto state, and a button in the Auto state without command and commandfor attributes, and whose parent is not a select element, is a submit button.
  source: https://html.spec.whatwg.org/multipage/form-elements.html
  scope: WHATWG HTML Living Standard, read 2026-09.
- claim: The p element's content model is phrasing content, and its end tag can be omitted when it is immediately followed by elements including div, table, ul, form, or a heading.
  source: https://html.spec.whatwg.org/multipage/grouping-content.html
  scope: WHATWG HTML Living Standard, read 2026-09.
---

Supported browsers, templating and sanitization boundaries, localization and writing directions, progressive-enhancement needs, and server-versus-client ownership of initial markup define the HTML environment, and element, attribute, and API availability depends on the configured browser matrix. Native elements follow from meaning and interaction contract, and headings, landmarks, lists, tables, links, buttons, forms, labels, validation, live regions, and document metadata follow from the content model.

Native semantics are preferable when they express the required contract, because they bring behavior as well as meaning. ARIA supplies only meaning: an element given `role="button"` still needs script to take focus and to activate on both Enter and Space, so ARIA fills gaps that native semantics cannot express rather than replacing them. Native behavior has defaults of its own; a `button` with no `type` inside a form, for example, is a submit button.

The rendered DOM and accessibility tree are the observable state, not template source alone. A `p` holds only phrasing content, so a `div` written inside one ends the paragraph when the parser meets it, and styles, scripts, and relationships that assume the written nesting act on a different tree. Accessible names and descriptions, roles, states, relationships, focus order, tab stops, and form error association are traced in that tree. The final markup is also shaped indirectly by:

- templates, partials, slots, and conditional rendering
- custom elements and shadow roots
- generated IDs, hydration output, sanitizers, and parser repair
- scripts or styles that hide, reorder, or repurpose elements

Characteristic failure modes involve content-model validity, duplicate IDs, nesting, landmark and heading structure, table headers, language and direction, alternative text, media captions, and keyboard-operable native behavior.

Behavioral evidence distinguishes keyboard behavior, screen-reader-relevant accessibility-tree output, form submission and validation, link and button behavior, focus restoration, zoom and reflow, localization, and server and client rendering in supported browsers. Automated validators and accessibility checks cover part of the semantic surface; names, roles, states, order, and interaction still need manual verification, and a screenshot cannot prove semantics. Escaped and untrusted content is observable only through the actual rendering and sanitization path, and a change must preserve progressive enhancement and native behavior unless altering them is part of its requested outcome.
