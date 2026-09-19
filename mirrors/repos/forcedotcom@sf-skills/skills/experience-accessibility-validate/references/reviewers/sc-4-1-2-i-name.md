## SC 4.1.2 - Name, Role, Value (Level A)

For all user interface components, the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents, including assistive technologies.

## SC: 4.1.2 (i) - Name Only

Analyze the files using following context:

_Goal_ : People, including users using assistive technology understand the intent of all user interface components

_What to do_ : Review provided HTML and JS code for accessibility violations per WCAG 4.1.2 (i) Name to ensure components have an accessible name. Ignore the Roles, States and Values parts of the Success Criterion for this review

Name could be visible or invisible. Sometimes, name are required to be visible, in which case it is identified using attributes such as `label` or `aria-label`.

Following are some preferred sufficient techniques that can help satisfy name-only success criterion:

- ARIA14: Using `aria-label` attribute to provide an invisible label where a visible label cannot be used. For sighted users, the context and visual appearance can provide sufficient cues to determine the purpose and presence of control element on component. In other situations, elements are given `aria-label` to provide an accessible names when native labeling element is not supported by control. For elements that use `aria-label`, check that the value of attribute property properly describes the purpose of elements where user input is required

- Note that `aria-label` may be disregarded in some situations where `aria-labelledby` is used for same object and for overriding native name, including `alt` and/or other attributes related authoring techniques
  - ARIA16: Using `aria-labelledby` attribute to provide a name for user interface controls. For each user interface control element where an `aria-labelledby` attribute is present, check that the value of the `aria-labelledby` attribute is an id of an element or a space separated list of ids referenced on the web page. Also check that the text of the referenced element or elements accurately labels the user interface control
- Like `aria-describedby`, `aria-labelledby` can accept multiple reference ids using a space seperated list, such as `label` and other elements, to allow for additional detail by concatenating multiple sources of information. This is useful in situations where sighted users use information from the surrounding context to identify a control. Also, a `label` element will always be exposed by accessibility API, while a `span` could have been used, it would lose the advantage of the larger clickable region
- While `aria-labelledby` appears similar to native HTML `label` element, there are some differences:
  - `aria-labelledby` can reference more than one text element while `label` element can only reference one
  - `aria-labelledby` can be used for variety of elements while `label` element can only ever be used on form elements
  - Clicking on a `label` element focussed the associated form field. Same is not true with `aria-labelledby` use. If focus behavior is required, use `label` or implement this using JS scripting
  - G108: Use markup to expose name, or related user-settable properties to be set. Check for proper markup, such that the name for each user interface component can be determined and that user interface components that accept user input can all be operated from Assistive Technology
- H91: For each instance of links and form elements, check that the name, value, and state are specified. In some instances, the text is associated with the control through a required HTML attribute. Like, Submit buttons using the button element text or image `alt` attribute as the name. In case of form control, label elements; `aria-label` or `aria-labelledby` properties; or the `title` attribute is used
- H44: Use `label` elements to associate text labels with form controls. The objective is to use the label element to explicitly associate a form control with a label. A label is attached to a specific form control through the use of the `for` attribute. The value of the `for` attribute must be the same as the value of the `id` attribute of the form control. The `id` attribute may have the same value as the `name` attribute, but both must be provided, and the `id` must be unique in the same DOM tree
  - Elements that use explicitly associated labels are as follows:
    - input type(s) for text
      - `input type="date"`
      - `input type="datetime-local"`
      - `input type="email"`
      - `input type="month"`
      - `input type="number"`
      - `input type="password"`
      - `input type="search"`
      - `input type="tel"`
      - `input type="text"`
      - `input type="time"`
      - `input type="url"`
      - `input type="week"`
    - `input type="checkbox"`
    - `input type="color"`
    - `input type="file"`
    - `input type="radio"`
    - `input type="range"`
    - `select`
    - `textarea`
  - Some cases where the `label` HTML element is ignored:
    - a `button` element when the label is provided by the content
    - `input type="button"` when the label is provided by the content
    - `input type="hidden"`
    - `input type="image"` when the label is provided by the `alt` attribute
    - `input type="reset"` when the label is label provided by the `value` attribute
    - `input type="submit"` when the label is label provided by the `value` attribute
  - For all input elements of type `text`, `file` or `password`, for all `textarea` elements, and for all `select` elements in the Web page
    - Check that there is a `label` element that identifies the purpose of control before `input`, `textarea` or `select` element
    - Check that `for` attribute of `label` element matches `id` of `input`, `textarea` or `select` element
    - Check that the `label` element is visible
  - And, for all input elements of type `checkbox` or `radio` in Web page:
    - Check for the presence of a `label` element that identifies the purpose of the control after the input element
    - Check that the `for` attribute of the `label` element matches the `id` of the `input` element
    - Check that `label` element is visible
- H64: Check that each `iframe` element in HTML source code for the presence of a `title` attribute. Also, that the `title` attribute contains text that describes the `iframe`'s content. Note that `title` attribute is not interchangeable with the `name` attribute. The `name` is not presented to the user, only the `title` is
- H65: For all form controls that are not associated with `label` element, check that the control has a `title` attribute, and that the purpose of form control is clear to users who can see the control and that `title` attribute identifies purpose and that it matches apparent visual purpose
- H88: For each HTML page, check that the page uses only elements, attributes that are defined in the specification, used in manner prescribed by specification and that the page can be parsed correctly, according to rules of specification - G135: Using accessibility API features to expose name, to allow user-settable name to be directly set, and to provide notification of changes by rendering content. Additionally, check that the name for each user interface component can be found - G10: Changes to the name on the component, check that the accessibility tool is alerted of change and that the component continues to work with assistive technologies
  _Rules to follow_ :

* Require programmatically determinable name for all user interface components.
* For each component that violates #1, compile a concise list of issues for user to review, along with an action report on sufficient technique that can help resolve violation for component under review.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.

**ABSOLUTE AND STRICT EXCLUSION RULES FOR SC 4.1.2 'NAME' ANALYSIS (AND WHEN NOT TO FLAG):**

- **PRIMARY RULE:** A user interface component **PASSES** the 'Name' criterion if it has _any_ programmatically determinable accessible name, whether visible or invisible, provided through valid HTML or ARIA.
- **DETERMINE HOW THE ACCESSIBLE NAME IS SUPPLIED IN THE PROVIDED MARKUP BEFORE CONCLUDING A NAME IS MISSING.** Before flagging an element for a missing name, determine its role and applicable accessible-name sources. Check for text content only when the role or host-language semantics support naming from content; otherwise look for a native labeling mechanism, `aria-label`, `aria-labelledby`, or a valid `<label>` association. Proximity alone is not a naming relationship: an adjacent `<label>`, heading, or text node names a control only when the markup explicitly associates them. A named `<fieldset>`, `<section>`, `role="group"`, or `role="radiogroup"` provides group context but does **not** supply an accessible name to each descendant control; every descendant input, button, or other control still needs its own valid name. Evaluate the group container separately: a `<legend>` names its containing `<fieldset>`, while `aria-label` or `aria-labelledby` names the group element on which it appears. Also do not flag an icon or `<svg>` marked `aria-hidden="true"` or `role="presentation"` for a missing name: it is intentionally removed from the accessibility tree, while the interactive parent must provide its own name.
- **DO NOT FLAG:** If an element already has a programmatically determinable name via:
  - Its text content when its role or host-language semantics support naming from content (e.g., button text, heading text, link text).
  - An associated `<label>` element.
  - An `aria-label` attribute.
  - An `aria-labelledby` attribute (and the referenced ID exists within the provided code).
  - An `alt` attribute for `<img>` elements (unless decorative `alt=""`).
  - A `title` attribute for `<iframe>` elements or form controls not associated with a `<label>`.
- **SPECIFIC EXCLUSIONS (DO NOT FLAG):**
  - **Semantic HTML elements (e.g., `<h1>`-`<h6>`, `<a>`, `<button>`, `<form>`, `<iframe>`, `<img>`)** used with their native naming mechanisms (text content, `alt`, `title`). These automatically pass.
  - **Generic HTML elements (`div`, `span`)** used _solely_ for visual layout, styling, or as non-semantic containers. They do not require an accessible name unless they are _explicitly_ implemented as a custom interactive control (e.g., a custom button).
  - **Crucially, if an element uses `aria-label` or `aria-labelledby` to provide an accessible name, it **automatically passes** the 'Name' criterion.** DO NOT flag these elements for "missing labels" or "missing visible labels," as `aria-label` / `aria-labelledby` are valid ways to provide a programmatic name.
    - The only exception is if the _value_ of `aria-label` or the ID(s) referenced by `aria-labelledby` are clearly empty, nonsensical, or refer to non-existent elements within the provided code snippet.
  - **DO NOT flag any issues related to 'Role', 'State', or 'Value'.** Focus **exclusively** on 'Name' as defined by WCAG 4.1.2 (i).
  - **DO NOT suggest general "semantic structure" improvements or general best practices that are not directly related to a missing or incorrect accessible name.**
  - **Specifically for `<a>` (link) elements:** If an `<a>` element has its accessible name provided by its text content or `aria-label`/`aria-labelledby`, it **passes** the 'Name' criterion. DO NOT flag its `href` attribute (e.g., `href="#"` or `href="javascript:void(0)"`) as a 'Name' issue; this relates to link purpose or behavior, not its accessible name.
  - **Specifically for ARIA attributes**:
    - **`aria-label` and `aria-labelledby`**: These are valid ways to provide an accessible name. Only suggest them if a user interface component _truly lacks a programmatically determinable accessible name_ through any other means.
    - **`alt` attribute for `<img>`**: Flag missing `alt` attributes for `<img>` elements that convey information. If the image is purely decorative, suggest `alt=""`.
    - **`title` attribute**: Only suggest the `title` attribute for form controls that are _not_ associated with a `<label>` element, and ensure its purpose is clear and matches visual intent. Also, ensure `<iframe>` elements have a descriptive `title` attribute.
    - **For `spinbutton` and similar roles (e.g., `slider`, `progressbar`)**: Ensure `aria-valuemin`, `aria-valuemax`, and `aria-valuenow` use **numeric** values. Flag as an error if non-numeric values are used.
- **Focus strictly on identifying where a user interface component's _accessible name_ cannot be programmatically determined, or where an explicit ARIA naming attribute (if used) is invalid or misleading (e.g., empty `aria-label`, `aria-labelledby` referencing non-existent ID).**
  - **DO NOT flag Salesforce Lightning Base Components (e.g., `lightning-card`, `lightning-record-edit-form`, `lightning-input-field`, `lightning-button`). Assume these components **automatically pass** the 'Name' criterion because Salesforce ensures their accessible names are handled implicitly and correctly.** Only flag if a custom override _explicitly breaks_ their inherent name determination, which is highly unlikely in standard usage.
- **ARIA SPELLING IS ELEMENT-SPECIFIC:** Plain HTML elements use `aria-labelledby` and `aria-describedby`; the hyphen-split `aria-labelled-by` or `aria-described-by` spelling is invalid there. On an LWC component tag, however, the hyphen-split spelling can be the kebab-case binding for an `@api ariaLabelledBy` or `ariaDescribedBy` property. Do not conclude that the component lacks a name from the spelling alone.
- **ASSOCIATE THE ACTUAL CONTROL:** An accessible name attached to a non-focusable wrapper around a composite editor does not name the editor's internal control unless the wrapper forwards it. Recommend extending the control to accept or forward the naming relationship, or using its supported labeling prop.
