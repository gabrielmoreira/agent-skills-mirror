# Widget Styling Best Practices

Widgets express *intent*, not pixels. Each surface provides a default look and feel; brand/theme overrides apply automatically.

- **Style semantically.** Use `variant`, `size`, and other enum-typed attributes (`primary`, `destructive`, `success`, `warning`). Do not pin literal colors or pixel values.
- **One primary action per visible group.** At most one `tile/button` with `variant: primary`. Use `secondary` or `destructive` for additional actions (see the `tile/button` schema for the full variant enum).
- **Every `tile/button` needs a `click` action.** See SKILL.md *Actions* — an action-less button renders disabled.
- **One `h1` per widget.** Use `h2`/`h3` for sub-section headings, `body` for prose, `caption` for helper text.
- **Use semantic state variants on state-bearing blocks** (`tile/badge`, `tile/callout`).
- **Omit attributes that equal the schema default.** Check each property's `default` in the `getUiComponentSchemas` metadata (step 4). If the value you would write matches it — e.g. `gap`, `size`, or `action/openLink` `target: "_blank"` — leave the attribute out. Set an attribute only to change it.
- **Don't pin `width`** unless a content constraint requires it.
- **Use the Lucide icon set.** Pass the Lucide name (`"check"`, `"alert-circle"`); other icon libraries are not supported.
