## SC 1.3.1 - Info and Relationships (Level A)

Information, structure, and relationships conveyed through presentation can be programmatically determined or are available in text.

## SC: 1.3.1 (i) - Info And Relationships - Lists (A)

Review the provided HTML and JS files for accessibility violations per WCAG 2.2 SC 1.3.1 (i), 'Info and Relationships'
(Only lists from this rule should be considered). For all lists on the page, ensure that any information conveyed through presentation is programmatically determinable in order to determine if they meet SC 1.3.1 (i).
If they do not meet this success criterion, flag it as a violation.

Rules to follow:

- Find all violations of SC 1.3.1 'Info and Relationships - Lists' in the provided HTML and JS files.
- Do not worry about violations of SC 1.3.1 that are not specific to lists. These will be handled by other reviewers.
- The preferred technique for fixing SC 1.3.1 lists violations is The objective of this technique is to create lists of related items using list elements appropriate for their purposes.
  The ol element is used when the list is ordered and the ul element is used when the list is unordered.
  Description lists (dl) are used to group name-value pairs of information, for example: terms and definitions or questions and answers.
  Although the use of this markup can make lists more readable, not all lists need markup.
  For instance, sentences that contain comma-separated lists may not need list markup.
  When markup is used that visually formats items as a list but does not indicate the list relationship, users may have difficulty in navigating the information.
  An example of such visual formatting is including asterisks in the content at the beginning of each list item and using br elements to separate the list items.
  Some assistive technologies allow users to navigate from list to list or item to item.
  Style sheets can be used to change the presentation of the lists while preserving their integrity.
  The list structure, commonly unordered lists, is also useful to group hyperlinks.
  When this is done, it helps screen reader users to navigate from the first item in a list to the end of the list or jump to the next list.
  This helps them to bypass groups of links if they choose to..
- The procedure for H48 is Check that content that has the visual appearance of a list (with or without bullets) is marked as an unordered list.
  Check that content that has the visual appearance of a numbered list is marked as an ordered list.
  Check that content is marked as a description list when groups of name-value pairs, for example: terms and definitions or questions and answers, are presented in the form of a list..
- If the contents of the list are ordered, it must use the `<ol>` element.
- When a sublist is indented, use a ul or ol inside a list item to properly communicate the new list level/position within the parent.
- When creating description lists where the elements are iterated over with a template for:each loop ALWAYS insert a wrapper div element for each object in the array. Place the unique key attribute on the wrapper div element. Here is an example:

```html
<dl>
  <template for:each={entries} for:item="entry">
    <div key={entry.foo} class="entry-item">
      <dt class="foo">{entry.foo}</dt>
      <dd class="bar">{entry.bar}</dd>
    </div>
  </template>
</dl>
```

- For each issue found, provide a separate, detailed report.
- Keep issues concise, avoid duplicated issues or unnecessary or non-applicable problems.
- Assume that any imported functionality works as expected and was already analyzed.
- Components do not supplement or provide global functionalities.
