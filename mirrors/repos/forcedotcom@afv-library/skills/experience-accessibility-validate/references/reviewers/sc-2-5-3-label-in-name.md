## SC 2.5.3 - Label in Name (Level A)

For user interface components with labels that include text or images of text, the name contains the text that is presented visually.

## SC: 2.5.3 - Label In Name

Analyze the given file using the following framework:

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 2.5.3, 'Label in Name'. For all controls on the page, compare the visible label with the associate accessible name as defined below, and determine if they meet SC 2.5.3. If they do not, then flag this as a violation.

The visible label is the label that is rendered to the DOM and associated with a control.

The accessible name is the value computed by assistive technology associated with a control.

You must use the following algorithm to compute the accessible name for comparison with the visible label:

```text
  1. Initialize: Set the root node to the given element, the current node to the root node, and the total accumulated text to the empty string ("").
  2. Compute the text alternative for the current node:
    A. If the current node is hidden and is not directly referenced by aria-labelledby, nor directly referenced by a native host language text alternative element (e.g. label in HTML) or attribute, return the empty string.
    B. Otherwise:
      - If the current node has an aria-labelledby attribute that contains at least one valid IDREF, and the current node is not already part of an aria-labelledby traversal, process its IDREFs in the order they occur:
         i. Set the accumulated text to the empty string.
        ii. For each IDREF:
            a. Set the current node to the node referenced by the IDREF.
            b. Compute the text alternative of the current node beginning with step 2. Set the result to that text alternative.
            c. Append the result, with a space, to the accumulated text.
       iii. Return the accumulated text.
    C. Otherwise, if the current node has an aria-label attribute whose value is not the empty string, nor, when trimmed of white space, is not the empty string:
      - If traversal of the current node is due to recursion and the current node is an embedded control as defined in step 2E, ignore aria-label and skip to rule 2E.
      - Otherwise, return the value of aria-label.
    D. Otherwise, if the current node's native markup provides an attribute (e.g. title) or element (e.g. HTML label) that defines a text alternative, return that alternative in the form of a flat string as defined by the host language, unless the element is marked as presentational (role="presentation" or role="none").
    E. Otherwise, if the current node is a control embedded within the label (e.g. the label element in HTML or any element directly referenced by aria-labelledby) for another widget, where the user can adjust the embedded control's value, then include the embedded control as part of the text alternative in the following manner:
      - If the embedded control has role textbox, return its value.
      - If the embedded control has role menu button, return the text alternative of the button.
      - If the embedded control has role combobox or listbox, return the text alternative of the chosen option.
      - If the embedded control has role range (e.g., a spin button or slider):
        - If the aria-valuetext property is present, return its value,
        - Otherwise, if the aria-valuenow property is present, return its value,
        - Otherwise, use the value as specified by a host language attribute.
    F. Otherwise, if the current node's role allows name from content, or if the current node is referenced by aria-labelledby, or is a native host language text alternative element (e.g. label in HTML), or is a descendant of a native host language text alternative element:
         i. Set the accumulated text to the empty string.
        ii. Check for CSS generated textual content associated with the current node and include it in the accumulated text. The CSS :before and :after pseudo-elements [CSS2] can provide textual content for elements that have a content model.
           - For :before pseudo-elements, User agents MUST prepend CSS textual content, without a space, to the textual content of the current node.
           - For :after pseudo-elements, User agents MUST append CSS textual content, without a space, to the textual content of the current node.
       iii. For each child node of the current node:
          a. Set the current node to the child node.
          b. Compute the text alternative of the current node beginning with step 2. Set the result to that text alternative.
          c. Append the result to the accumulated text.
        iv. Return the accumulated text.

  Important: Each node in the subtree is consulted only once. If text has been collected from a descendant, but is referenced by another IDREF in some descendant node, then that second, or subsequent, reference is not followed. This is done to avoid infinite loops.

    G. Otherwise, if the current node is a Text node, return its textual contents.
    H. Otherwise, if the current node is a descendant of an element whose Accessible Name is being computed, and contains descendants, proceed to 2F.i.
    I. Otherwise, if the current node has a Tooltip attribute, return its value.

  Append the result of each step above, with a space, to the total accumulated text.

  After all steps are completed, the total accumulated text is used as the accessible name of the element that initiated the computation.
```

For every element in the component, determine both its visible label and its accessible name using the aforementioned algorithm. If the two values are unique, then this must be flagged as a violation. For example, `aria-label` uses different wording to add additional context for screen readers, but it fails to include or prefix the visible text, such as when the visible text displays "nonstandard" and the `aria-label` uses "this field is not standard".

This is ONLY about accessible name computation. Details regarding accessible description should be ignored. Eg. an `aria-describedby` attribute/value should not be considered for the accessible name, and should be ignored in this case.

Rules to follow:

- Find all violations of SC 2.5.3 'Label in Name' in the provided HTML file.
  - For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
