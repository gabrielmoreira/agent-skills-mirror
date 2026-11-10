# Building and reviewing prototypes

Whoever builds or reviews a ux-brainstorm prototype follows this file, together with `decisions.md` (obey every rule), the area's entries in `references.md`, and the base or template. A builder replies with its file path and every decision a variant can't express; a reviewer fixes in place and replies with what changed and what it couldn't fix.

## The template

Start from [../assets/prototype-template.html](../assets/prototype-template.html), or from `RUN/base.html` when there is one. Its markup:

- `data-proto-variant="A"` marks a variant's block; its `data-proto-desc` is one line naming the structure and the reference it draws on ("Side panel · like Front's details pane"). The letter bar switches variants in place.
- `data-proto-state="Empty"` marks what shows only in that state. The state bar is built from the states in the markup, so declare every state there, even ones a script fills.
- `<body data-first-variant="B" data-first-state="Error">` picks the first view.
- Demo controls go in `#controls` as labeled inputs with `data-proto-control="speed"`; read them through `proto.controls`.
- Your own code goes in a `<script>` after the template's: `proto.onChange(fn)` runs `fn(proto)` on every change, and `proto.set('state', 'Error')` switches the view.
- A phone surface uses `<div class="window phone">`.

## What every prototype holds

- **Tokens**: the project's own, under its own names, light then dark, defined on `.window` (the template shows where). With no design system, the chosen direction's.
- **Icons**: the project's real icon set, inlined as `<svg>`, only the icons used. With no icon set, use Lucide: fetch each icon from `https://unpkg.com/lucide-static@1.58.0/icons/<name>.svg` and paste its `<svg>` inline, since an `<img>` can't follow `currentColor`. A glyph the set lacks gets `class="new-icon"` on its `<svg>` (a dashed outline) and " · new icon" appended to its control's tooltip (`data-tip="Archive · new icon"`); the aria-label stays "Archive".
- **Sample data**: realistic content in the user's domain, with an overflow case (a long name, many items), shared by all variants so what the user does in one carries over when they switch, plus small helpers that implement the decided rules.
- **States**: every state the decisions name, plus first use, empty, loading, error, and overflow wherever the area can reach them. When a state depends on a condition (speed, error count, entry point), add a demo control that changes it.
- **Overlays** the area uses (dialog, popover, menu, toast with Undo), inside the window with `position: absolute`.

With more than one area, build these once as `RUN/base.html`: the template with tokens, icons, data, and overlays filled in and no variants. Each area's prototype starts as a copy of it. The HTML tool receives only the file's text, so keep everything inline and link no CSS or JS files.

## Variants

Build 2–4 per area, each a different answer to the area's question: layout, hierarchy, or primary affordance. Each draws on at least one of the area's references (or the chosen direction) and names it in its `data-proto-desc`. Each element maps onto an existing project component. Every variant obeys `decisions.md`; when one can't express a decision, keep the variant and report the gap for Things to weigh.

## Lean copy

Every word on screen spends the user's attention. Keep only the words that icons and layout can't carry.

- Labels take one or two words; headings, a short noun phrase. Leave out intros, helper paragraphs, and sentences that explain the UI.
- Swap a label for an icon wherever a first-time user reads the icon the same way: search, close, back, more, add, edit, delete, share, filter, sort, settings, copy, download. The primary action keeps a short verb next to its icon, and domain-specific actions keep their words, since an icon there is a guess.
- Every icon-only control gets a tooltip (`data-tip`) and the same `aria-label`. Add a tooltip elsewhere only for context the screen can't show: what a metric means, why a control is disabled.
- Empty and error states are a single line, plus at most the one action that resolves them: "Inbox zero"; "Couldn't load tickets" with Retry. A heading and a sentence under it are two lines.
- Use the project glossary's preferred terms, in the copy and the sample data alike.

## Review

Fix what you can; report what you can't (a decision a variant can't express, a new icon) for Things to weigh.

- Preview each variant in light and dark at its first state, and another state only where it changes the layout (empty, error, an open overlay). A preview captures only the first view, so pick it with the `<body>` attributes, then reset them to the first variant and the main state. Without any preview tool, report that the visual check was skipped.
- Trigger every click handler in every variant: in a browser tool when you have one, otherwise by tracing the code.
- Check each decision is honored or reported.
- Sweep the copy and sample data against [Lean copy](#lean-copy), and the glossary's banned terms.

## Rendering

Show boards and prototypes inline with the harness's HTML tool. In T3 Code, run `html_preview` first (in both `appearance` values, `width: 390` for a phone surface; fix console errors; read `contentHeight`), then `html_render` with that height, one frame per board or prototype. The frame is 728px wide on desktop and about 360px on phones, so:

- Fit a desktop app window into about 700px, with a narrow sidebar. Keep the template's fixed pixel height, and leave `vh` units and `height: 100%` off html and body.
- Leave html and body without background, border, or padding; `.window` carries its own.
- Tooltips clip inside the window; at its edges set `data-tip-pos="start"`, `"end"`, or `"up"`.
- The HTML travels inside every preview and render call. The limit is 512K characters, but prototypes of 80–130K were already slow and error-prone to relay, so stay well under: inline only the icons used, no frameworks, nothing loaded from the network.

Without an inline HTML tool, open the saved file in the browser (`open` on macOS, `xdg-open` on Linux) and give its path.
