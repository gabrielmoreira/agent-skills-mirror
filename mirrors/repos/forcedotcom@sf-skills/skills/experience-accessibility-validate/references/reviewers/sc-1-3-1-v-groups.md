## SC 1.3.1 - Info and Relationships (Level A)

Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

## SC: 1.3.1 (v) - Info And Relationships - Groups only

Analyze the files using following context:

_Goal_: Information, structure and relationships conveyed through presentation can be programmatically determined or available in text.

_What to do_: Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 1.3.1, 'Info and Relationships' with focus on groups requirements only.

Having structures and relationships programmatically determinable ensures that important information necessary for comprehension will be perceivable to all users. Grouping controls is most important for related radio buttons and checkboxes.

Examples:

- Form fields may be positioned as groups that share text labels.
- A multiple choice test with a question and set of radio buttons to present possible answers; the radio buttons are contained within a `fieldset` while the question is tagged with `legend` element.
- A user profile page allows users to indicate personal interests using checkboxes; the checkboxes are contained within a `fieldset`, and the `legend` element prompts the user to select one or more interests.

Following are some sufficient techniques that WCAG working group deems sufficient to meet this success criterion:

- ARIA17: Using grouping roles to identify related form controls within a form. Any label associated with group also serves as a common label for individual controls in this group.
  This is a viable alternative to using `fieldset` / `legend` technique (H71). For a group of radio buttons, `role="radiogroup"` should be used instead of `role="group"` and is not meant to be used for wrapping all controls on a form within a single container with `role="group"`.

- For groups of related controls where individual labels for each control do not provide sufficient description, and additional group level description is needed
  - Check that group of logically related input or select elements are contained within an element with `role="group"`, or `role="radiogroup"` depending on the type of elements in group.
  - Check that this group has an accessible name describing it's purpose using `aria-label` or `aria-labelledby` attribute.
  - The objective of this technique is to allow users to understand the relationship of form controls by providing semantic grouping and interact quickly.
    Form controls can be grouped by enclosing them within `fieldset` element. All controls within a given `fieldset` are then related. The first element inside `fieldset` must be a `legend` element. Avoid nesting fieldsets unnecessarily, as this can lead to confusion.
    A set of radio buttons or checkboxes are said to be related when they all submit values to single named field.
  - They work same as selection lists that allow users to choose from set of options, except selection lists are single controls while radio buttons and checkboxes are multiple controls.
  - The individual label associated with each radio button or checkbox control may not fully convey group's descriptive context.
    It can also be helpful to group other sets of controls less tightly related than radio buttons and checkboxes, like form fields that collect user address might be grouped together with `legend` of "Address".
    Authors sometimes avoid using `fieldset` element because the default display style draws a border around the grouped controls. However, this style can be modified with CSS by overriding 'border' property of `fieldset` and 'position' property of `legend`.

For groups of related controls where individual labels for each control do not provide sufficient context description, and additional group level description is needed; ensure following are true:

- Check that the group of logically related elements, like either `input` or `select` elements are contained within `fieldset` elements.
- Check that each `fieldset` has a `legend` element that is first child and includes a description for the group.
- The objective of this technique is to group items in a selection list.
  A selection list is a set of allowed values for a form control such as multi-select list or combo box. In semantic HTML, the `select` element is used to create both multi-select lists and combo boxes, where various allowed options are each indicated with `option` elements, grouped together using `optgroup` element, and labeled the group with `label`.

For each selection list:

- Check the set of options within the list to see if there are groups of related options.
- If there are groups of related options, check that they are properly grouped (like using `optgroup` element)

  - The objective of this technique is to group navigation links using HTML `nav` element or similar semantic sectioning elements. Using this markup can make groups of links easier to locate and navigate.
    When such element is employed more than once on a page, distinguish navigation groups by using `aria-label` or `aria-labelledby` attribute.
    Not all groups of links need to use `nav` element for markup. For example, links maybe grouped in other structures like lists or may use ARIA markup if do not present a discrete section of the page.

- Check that links that are grouped and represent a section of page, are enclosed in a `nav` element or similar semantics.

Before flagging a group as unlabeled or improperly structured, resolve how the group is named. A `role="group"` / `role="radiogroup"` container with `aria-label` or `aria-labelledby` is a **valid and sufficient** grouping-and-naming technique (ARIA17) — it does **not** additionally require a `<fieldset>` / `<legend>`. Treat `<div role="group" aria-label={...}>` (including a dynamic `aria-label` / `aria-labelledby` expression such as `aria-label={section.title}`) as a properly labeled group; do **not** flag it for a missing `<legend>`, a missing `aria-label`, or a missing group name when an `aria-label` / `aria-labelledby` is present. Only flag a group that has **neither** a `fieldset` / `legend` **nor** a `role="group"` / `role="radiogroup"` carrying an accessible name.

_Rules to follow_:

- Require code to reinforce structure, relationships and information conveyed through presentation for groups of related elements, per this WCAG 2.2 SC 1.3.1 'Info and Relationships - Groups only' success criterion, in the provided HTML and JS files.
- Do not worry about violations of SC 1.3.1 that are not specific to groups. These will be handled by other reviewers.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
