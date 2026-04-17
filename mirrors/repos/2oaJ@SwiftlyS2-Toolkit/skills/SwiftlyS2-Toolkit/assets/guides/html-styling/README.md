# SwiftlyS2 HTML Styling Guide

Official docs sections:
- `HTML Styling`
- `Menus`

This page is not meant to merely remind you that “HTML is supported”. Its real purpose is to distill the **practical, directly usable rules for SwiftlyS2 / Panorama rich text** so an agent can apply them directly when generating `SendCenterHTML`, menu formatting, dynamic text, and prompt-style UI.

## Three conclusions to remember first

1. **Panorama is not a browser.** Do not copy ordinary web HTML/CSS habits verbatim.
2. **Styling is not `style="..."`.** Panorama UI usually uses direct attributes plus built-in classes.
3. **Complex effects must be tested in game.** A fragment being parseable does not guarantee that it renders as expected.

## Supported scope

### Common tags explicitly listed by the official docs

The official `HTML Styling` page clearly lists the common Panorama UI tags that are usually available:

- `div`
- `span`
- `p`
- `a`
- `img`
- `br`
- `hr`
- `h1-h6`
- `strong`
- `em`
- `b`
- `i`
- `u`
- `pre`

### Recommended default tags

If there is no special need, prefer using only:

- `span`: inline color, font size, emphasis
- `br`: line breaks
- `div` / `p`: block segmentation

Why:

- `span + br` covers most center prompts, menu helper text, and status text.
- Fewer tags usually means less rendering drift.
- The agent is more likely to generate stable, usable fragments.

### Patterns you should not use by default

- Do not default to ordinary web-style `style="..."`
- Do not default to tags not explicitly listed by the official docs
- Do not assume `<font>` is always reliable

> Toolkit convention: if the task is only text coloring, font sizing, or emphasis, prefer `<span ...>` and do not generate `<font ...>`.

## Panorama styling syntax

### 1) Use direct attributes instead of `style="..."`

Correct example:

```csharp
var html = "<span color=\"red\">Danger prompt</span>";
```

Incorrect example:

```csharp
var html = "<span style=\"color:red\">Danger prompt</span>";
```

The official docs emphasize that Panorama UI styling is usually written as direct tag attributes rather than packed into `style`.

### 2) Prefer built-in classes

Correct example:

```csharp
var html = "<span class=\"fontSize-l fontWeight-bold\">Large bold text</span>";
```

Common benefits:

- more stable than manually scattering style attributes
- more consistent with the built-in game styling system
- easier to adjust consistently when the UI evolves

### 3) Attributes and classes can be combined

```csharp
var html = "<span color=\"green\" class=\"fontSize-l\">Ready</span>";
```

Typical use:

- use `class` for font size / style
- use `color` for dynamic color changes

## Common styling elements

### Colors

Common colors shown in the official examples and page include:

- `red`
- `green`
- `yellow`
- `gold`
- `lightyellow`
- `lightblue`
- `darkblue`
- `purple`
- `magenta`
- `grey`
- `silver`
- `olive`
- `lime`
- `lightred`

Hex colors can also be used, for example:

```csharp
var html = "<span color=\"#5E98D9\">CT</span>";
```

Suggestions:

- if the color is tied to team or status semantics, prefer explicit hex values
- for ordinary success / failure / warning text, semantic color names are usually sufficient

### Common font-size classes

The official page lists these font-size classes:

- `fontSize-xs`
- `fontSize-sm`
- `fontSize-m`
- `fontSize-l`
- `fontSize-xl`
- `fontSize-xxl`

Recommended convention:

- body text: `fontSize-m`
- secondary description: `fontSize-sm`
- important prompt: `fontSize-l`
- countdown / large numeric display: `fontSize-xl` / `fontSize-xxl`

### Common style classes

Common classes listed on the official page include:

- `fontStyle-m`
- `fontWeight-bold`
- `CriticalText`

Recommended use:

- `fontWeight-bold`: emphasis
- `CriticalText`: risk / warning / failure state
- `fontStyle-m`: consistent standard body style

## Typical landing scenarios

### 1) Center prompts / countdown / status broadcast

Suitable for:

- `Core.PlayerManager.SendCenterHTML(...)`
- round prompts
- ready-state summaries
- countdowns

Example:

```csharp
var timeLeft = 8;
var color = timeLeft <= 3 ? "red" : timeLeft <= 5 ? "yellow" : "green";
var html = $"<span class=\"fontSize-l\">Round starting soon</span><br><span color=\"{color}\" class=\"fontSize-xxl\">{timeLeft}</span>";

Core.PlayerManager.SendCenterHTML(html, 1);
```

Generation rules:

- put the title and the value on separate lines
- keep changing parts confined to the color and number
- design duration and refresh frequency together; do not chase visuals while ignoring spam risk

### 2) Extra menu description / dynamic summary

Suitable for:

- `TextMenuOption`
- `BindingText`
- top-of-menu summaries

Example:

```csharp
var option = new TextMenuOption
{
	BindingText = () => $"<span class=\"fontSize-sm\">Mode: <span color=\"green\">{runtime.ModeName}</span><br>Volume: <span color=\"yellow\">{runtime.Volume}</span></span>"
};
```

Suggestions:

- wrap dynamic values in inner `span` tags
- isolate frequently changing fields with their own color span
- keep `BindingText` limited to lightweight string assembly; no IO, DB, or JSON work there

### 3) Menu `BeforeFormat` / `AfterFormat`

The official menu docs state that menu options support `BeforeFormat` and `AfterFormat`. These two events often interact with HTML Styling.

Recommended split:

- `BeforeFormat`: adjust the semantic text
- `AfterFormat`: add the HTML presentation layer

Example:

```csharp
option.BeforeFormat += (_, args) =>
{
	args.CustomText = $"[VIP] {args.Option.Text}";
};

option.AfterFormat += (_, args) =>
{
	args.CustomText = $"<span color=\"#FFD700\">{args.CustomText}</span>";
};
```

Notes:

- even inside `AfterFormat`, prefer `<span>` and do not default to `<font>`
- do not query remote data from formatting events

## Common string-assembly suggestions

### Prefer `$"..."`

```csharp
var html = $"<span color=\"green\">{playerName}</span> is ready";
```

It is clearer than string concatenation and easier for the agent to extend safely.

### Split title / detail / value first, then compose

```csharp
var title = "<span color=\"yellow\" class=\"fontSize-l\">Server Rules</span>";
var line1 = "<span>• No cheating</span>";
var line2 = "<span>• No malicious boosting</span>";
var html = $"{title}<br><br>{line1}<br>{line2}";
```

This is better for:

- translation replacement
- conditional assembly
- inserting or removing a specific line based on player state

### Compute dynamic color first, then interpolate it

```csharp
var statusColor = isReady ? "green" : "red";
var html = $"<span>{playerName}</span>: <span color=\"{statusColor}\">{statusText}</span>";
```

Do not bury complex ternary logic directly inside the HTML fragment unless you want readability to tumble into the basement.

## Interaction with other assets

### Menus

- Menu template: `../../development/menus/menu-template.cs.md`
- Focus points: `BindingText`, `BeforeFormat`, `AfterFormat`, and async callback validity checks

### Translations

- Translation entry: `../../development/translations/README.md`

Suggestions:

- keep translation keys focused on semantic text fragments; apply colors and classes at the final assembly layer
- if translated text must contain HTML, define clearly which placeholders are safe to inject

### Thread safety

- HTML string assembly itself is usually not the thread-sensitive part
- but **the player / entity data used to produce that HTML** may involve thread-sensitive APIs
- when building UI text inside async callbacks, confirm first that the consumed state has already been snapshotted safely

## Where to discover classes

The official HTML Styling page points to this extension reference:

- `https://github.com/SteamDatabase/GameTracking-CS2/tree/master/game/core/pak01_dir/panorama/styles`

That directory can be used to:

- inspect built-in Panorama classes
- observe naming patterns in files such as `panorama_base.css` and `gamestyles.css`
- recheck whether new classes appear after CS2 updates

Recommended lookup order:

1. first use the common classes listed on this page
2. if they are not enough, inspect the SteamDatabase styles directory, especially `panorama_base.css` / `gamestyles.css`
3. before truly adopting a new class, validate it in game

## Agent generation rules

When the agent needs to output an HTML fragment, prefer the following rules:

1. default to `span + br`
2. default to `<span color="..."></span>` and do not generate `style="..."`
3. prefer `fontSize-*` classes for sizing rather than hand-written complex font attributes
4. prefer `fontWeight-bold` or `CriticalText` for emphasis
5. prefer `BindingText` for dynamic menu text
6. keep formatting events limited to lightweight string transformation
7. for complex layouts, explicitly note that in-game validation is required

## Common anti-patterns

### Anti-pattern 1: copying web CSS habits directly

```csharp
"<span style=\"color:red;font-size:24px\">Warning</span>"
```

Use this instead:

```csharp
"<span color=\"red\" class=\"fontSize-xl\">Warning</span>"
```

### Anti-pattern 2: heavy logic inside `BindingText` / `AfterFormat`

Do not:

- query databases
- issue HTTP requests
- serialize / deserialize large objects
- repeatedly build large complex HTML fragments inside hot-refresh UI paths

### Anti-pattern 3: deeply nested HTML for showmanship

Panorama being able to parse it does not mean the client will display it stably.

For prompt-style UI, prefer:

- one title layer
- one value / status layer
- line breaks with `br`

## Final checklist

- [ ] Is `style="..."` avoided?
- [ ] Are `span`, `br`, and built-in classes preferred?
- [ ] Are dynamic values assembled separately from fixed text?
- [ ] Is heavy logic avoided inside dynamic text callbacks?
- [ ] Is it clear whether in-game validation is required?
