# Diagram style tokens

The style follows Vercel architecture diagrams: a top-to-bottom flow, dashed containers, nodes with a Geist icon, thin gray connectors, small open arrowheads, one highlighted entry node. All tokens are CSS custom properties on `:root` in the template.

## Colors

| Token | Dark | Light | Use |
| --- | --- | --- | --- |
| `--bg` | `#000` | `#fff` | Canvas and outer container fill |
| `--panel` | `#0a0a0a` | `#fafafa` | Nested panel fill |
| `--node` | `#111` | `#fff` | Node fill |
| `--border` | `#5c5c5c` | `#b8b8b8` | Dashed borders |
| `--fg` | `#ededed` | `#171717` | Labels and headers |
| `--muted` | `#8f8f8f` | `#666` | Second line, route labels, node icons |
| `--line` | `#8f8f8f` | `#7a7a7a` | Connectors and arrowheads |
| `--line-strong` | `#ededed` | `#171717` | Main flow connectors |
| `--hl-fill` | `#0a2a5e` | `#dbe8ff` | Highlighted node fill |
| `--hl-ring` | `#1e5fd6` | `#2563eb` | Highlighted node ring |
| `--hl-icon` | `#cfe0ff` | `#1d4ed8` | Highlighted node icon |

## Background

The `html` and `body` background and the outer container fill are transparent, so an embedded diagram takes the docs page color in either site theme. `:root` also sets `color-scheme` (dark by default, light for the light theme) to match the parent page; a mismatch makes the browser paint an opaque canvas behind the iframe. Only when the file is opened directly (`window.self === window.top`) the script sets `data-top` on `:root` and the page uses `--bg`. Nested panels keep their `--panel` fill.

## Borders and shapes

- Stroke width 1 with `vector-effect: non-scaling-stroke`, so lines stay 1px at any scale.
- Dash pattern `4 4`.
- Outer container radius 8, nested panel radius 8, node radius 6.
- Nodes are 56 high and as wide as their longest line needs, usually 180 to 280. Size each node from the label: 44 for the icon and padding, then the text, then at least 20 to spare. Nodes on one row share a width and a gap of 20 to 40; the gap between rows is 34 to 44, enough for an arrow and its route label.
- Center a single node in the column. Center each row of branches under the node that fans out to it.
- Container padding is 20 to 28 from its border to the nearest node. A container header sits 28 to 32 from the top: a 20px icon in `--fg`, then the label 30 to the right of the icon's left edge.

## Typography

Font stack `Geist, "Geist Sans", system-ui, -apple-system, "Segoe UI", sans-serif`.

| Element | Size | Weight | Color |
| --- | --- | --- | --- |
| Container header | 16 | 500 | `--fg` |
| Node label | 15 | 400 | `--fg` |
| Node second line | 11.5 | 400 | `--muted` |
| Route label on an arrow | 12.5 | 400 | `--muted` |

Node text is left-aligned after the icon: label at `x + 44` and the vertical middle minus 4, second line at `x + 44` and the middle plus 13. Route labels sit beside a vertical connector, 10 to its right, or 8 above a horizontal one.

## Connectors

- Straight connectors start and end 6 away from the node edge, except where they cross a container border.
- Elbows use a 14 radius arc: `V…a14 14 0 0 1 -14 14H…`.
- Arrowhead: an open chevron marker, `viewBox 0 0 8 8`, path `M1.5 1.5 L5.5 4 L1.5 6.5`, stroke 1, round caps and joins, `refX 6`, `markerUnits="userSpaceOnUse"`, `orient="auto"`.
- Use `--line-strong` for the main path and `--line` for secondary paths.

## Icons

Icons come from the [Geist icon set](https://vercel.com/geist/icons). The docs app already ships the ones below: copy the `d` attribute (and `fill-rule="evenodd"` when the source sets `fillRule`) from `apps/docs/node_modules/@vercel/geistdocs/dist/assets/icons/icon-<name>.js`. Geist icons are 16 x 16 filled shapes, so embed each one as a nested SVG and color it with `fill`, never `stroke`:

```html
<svg class="ico" x="126" y="169" width="18" height="18" viewBox="0 0 16 16"><path d="..." fill-rule="evenodd" clip-rule="evenodd"/></svg>
```

- Node icons: 18px, `fill: var(--muted)`, at `x + 16` and centered on the node's vertical middle.
- Container header icons: 20px, `fill: var(--fg)`.
- The highlighted entry icon: 22px, `fill: var(--hl-icon)`, centered in the circle.

Pick the icon for what the node is, and keep the same icon for the same thing across diagrams:

| Thing | Icon |
| --- | --- |
| Calling agent | `robot` |
| A machine, the desktop | `device-desktop` |
| The `agent-desktop` CLI | `terminal` |
| The C library | `api` |
| `agent-desktop-core`, a crate or package | `box` |
| A trait or router that picks one implementation (`PlatformAdapter`) | `route` |
| The target app or a window | `display` |
| A snapshot or tree listing (`--skeleton`) | `logs` |
| A drilled region (`--root`) | `folder-open` |
| A ref, a ref action | `link` |
| Stored state (`RefStore`, a refmap) | `archive` |
| A record (`RefEntry`) | `file-text` |
| Strict resolution or a check | `shield-check` |
| Success or verification | `check-circle-fill` |
| An error outcome | `cross` |
| A refresh, re-read, or retry | `refresh-counter-clockwise` |

For operating systems, use the brand marks instead of a Geist icon: Apple and Linux (Tux) from [Simple Icons](https://simpleicons.org) (CC0, `viewBox="0 0 24 24"`), and the four-square Windows mark (`M0 0h7.5v7.5H0zM8.5 0H16v7.5H8.5zM0 8.5h7.5V16H0zM8.5 8.5H16V16H8.5z` in a 16 x 16 box). Color them like any node icon.

When a node needs an icon this table does not cover, choose the closest Geist icon by meaning and add it to the table in the same change.

## Highlighted node

A circle of radius 28 filled with `--hl-fill`, ringed with a 1px `--hl-ring` stroke, with the entry's icon at 22px in `--hl-icon`. Place it at the top of the diagram, above the node it enters, with its label and second line to its right (`cx + 42`). Use it once per diagram.

## Size and scaling

Lay diagrams out for the docs content column, not for a wide canvas. The column is about 720px wide at a 1440px viewport, so the target `viewBox` width is 720 and the height is whatever the top-to-bottom layout needs (the architecture diagram is 720 x 672). The font sizes above are in `viewBox` units, so at 720 wide they render at 1:1. Do not design a wider canvas and let it scale down: a 1124 wide diagram renders at 0.64 and its labels shrink to about 8px. When the content does not fit in 720, add a row instead of widening the canvas.

One SVG with a `viewBox`, `width: 100%`, `height: auto`. Keep the `viewBox` size and the `aspectRatio` prop of `<Diagram>` equal. On a phone the diagram scales down with the column; keep node text short so it stays readable.
