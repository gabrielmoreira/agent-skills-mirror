# Widget Localization with Custom Labels

A widget shows translated text by referencing a Salesforce Custom Label instead of a hardcoded string.

---

## Syntax

```text
{!$Label.c.<LabelName>}
```

- `c` is the org's default namespace. Always write it.
- The label name is static. Never build it from data — `{!$Label.c.$attrs.key}` can't be validated when the widget is saved.
- A `$Label` reference is not a `$attrs` binding and has no entry in `schema.json`.

---

## What to localize

Replace every static, user-visible string in an allowed attribute, unless the user limited the request to specific strings.

**Allowed**

- Display text: `text`, `label`, `placeholder`, `title`, and other free-form string attributes (per `getUiComponentSchemas`)
- Text results inside a formula, e.g. the branches of an `IF` or `CASE`

**Not allowed**

- `meta` directives (`if`, `forEach`, `forItem`)
- Enum-valued attributes (`variant`, `size`, `color`, `gap`, `align`, `justify`) and icon names
- Anything inside `actions` (`url`, `target`, `sendMessage` `content`)
- Data bound with `$attrs` / `$item` — payload values are not translated
- `schema.json` and the `-meta.xml`

---

## Label names

Reuse existing labels first. If the user names labels, or the project's CustomLabels file (`labels/CustomLabels.labels-meta.xml`) already has a label whose value matches the text, reference that label's `fullName` verbatim. Otherwise propose `<WidgetName>_<Role>`.

---

## Combining labels with data

- Join a label and data with `&` (see `references/widget-formulas.md`):
  `"text": "{!$Label.c.<LabelName> & ' ' & TEXT($attrs.<attrName>)}"`
- Choose between labels with `IF` / `CASE`:
  `"label": "{!IF($attrs.<booleanAttr>, $Label.c.<LabelWhenTrue>, $Label.c.<LabelWhenFalse>)}"`

---

## Creating labels

This skill gives no guidance on authoring label metadata, and the widget is complete without it. Create labels only when the user asks you to. When you do, add them to the project's existing CustomLabels file instead of overwriting it, and never redefine a label that already exists. The user is responsible for checking the labels and any translations in the org and for deploying them with or before the widget.

---

## Label report

End the response with this report:

```markdown
### Custom Labels used by this widget

These labels must exist in the target org before you deploy — deploying a widget that references a missing label fails.

| Label name | Value (default language) | Status | Used in |
|---|---|---|---|
| OrderStatus_Heading | Order status | Existing | `tile/text` `text` (widget heading) |
| OrderStatus_TrackButton | Track order | To create | `tile/button` `label` |
```

- List each distinct label once, in the order it first appears in the widget.
- **Label name** is the `fullName`, without the `c.` prefix.
- **Value** is the literal text the label replaced.
- **Status** is `Existing` (already in the project or named by the user), `Created` (you wrote it), or `To create` (the user must create it).
- **Used in** names the block definition and attribute.
