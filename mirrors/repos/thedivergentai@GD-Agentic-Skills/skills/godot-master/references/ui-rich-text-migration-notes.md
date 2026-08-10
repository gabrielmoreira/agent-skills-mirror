# Migration notes: godot-ui-rich-text

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is still on Godot 3.x, use the official [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html) guide first, then continue from 4.0.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `RichTextLabel.push_list` gains `bullet`; `push_paragraph` gains justification/tab_stops optionals.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `RichTextLabel.add_image` gains `key`, `pad`, `tooltip`, `size_in_percent` optionals.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- Default font outline color is black (was white) — retune dialogue/chat themes using outline-only styling.
- `auto_translate` deprecated for Node `auto_translate_mode` (inherit semantics).
- `RichTextLabel.push_meta` gains `underline_mode`.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `RichTextLabel.push_meta` gains `tooltip`; `set_table_column_expand` gains `shrink`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `add_image`/`update_image`: `size_in_percent` replaced by `width_in_percent` and `height_in_percent` — set both explicitly to restore old percent sizing.
- `push_underline`/`push_strikethrough` optional color; `add_image` `alt_text`; `push_table` `name`.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- `width_in_percent`/`height_in_percent` → `width_unit`/`height_unit` with `RichTextLabel.ImageUnit` (defaults changed).
- `ImageUpdateMask.UPDATE_WIDTH_IN_PERCENT` → `UPDATE_WIDTH_UNIT`.
- `add_image`/`update_image` width/height are `float` — **NEVER** pass bool percent flags; use `RichTextLabel.ImageUnit` values.
