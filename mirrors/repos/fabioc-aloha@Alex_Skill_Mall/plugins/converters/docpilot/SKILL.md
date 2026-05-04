---
type: skill
lifecycle: stable
inheritance: inheritable
name: convert-to-docx
description: Convert a Markdown file to a styled Word (.docx) document using docpilot — syntax-highlighted code blocks, blue-header tables, no Pandoc required.
tier: standard
applyTo: '**/*docx*,**/*word*,**/*loop*,**/*convert*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Convert Markdown → Word

Convert a Markdown design or dev spec into a formatted `.docx` file the user can open in Microsoft Word.

## When to Use

- User says "convert to Word", "make a docx", "export this spec to Word"
- User has a `.md` file and wants a Word document with formatted code blocks and tables
- User asks for a printable / shareable version of a Markdown document

## How to Respond

### Step 1 — If the user provided a file path

Run:

```bash
python plugins/docpilot/scripts/venv-run.py plugins/docpilot/scripts/convert.py "<input.md>" --to word --open
```

The first run installs dependencies into a per-plugin venv (one-time, ~30s). Subsequent runs are instant.

### Step 2 — If no file path was provided

1. Use the Glob tool to find `**/*.md` files under the current working directory, excluding `.git`, `.claude`, `node_modules`, and `__pycache__`. Take the 4 most recently modified.
2. Use the AskUserQuestion tool with those files as options. For each option:
   - `label`: the filename only (e.g. `spec.md`)
   - `description`: the relative directory path (e.g. `docs/` or `.` for root)
   The user can also pick "Other" to type a path manually.
3. Once chosen, run:
   ```bash
   python plugins/docpilot/scripts/venv-run.py plugins/docpilot/scripts/convert.py "<chosen_file>" --to word --open
   ```

### Step 3 — Report

Tell the user the output path and confirm whether the file opened.

## Common Variants

- **Custom output path**: add `--output <path.docx>`
- **Different code colour theme**: add `--style monokai` (or any [Pygments style](https://pygments.org/styles/))
- **Don't open after conversion**: omit `--open`

## What Gets Converted

| Markdown | Word Output |
|----------|-------------|
| `# Heading` / `## Heading` | Word Heading 1 / Heading 2 (with bookmarks for cross-references) |
| Fenced code blocks (` ```py `) | Syntax-highlighted, Consolas 9.5pt |
| Tables | Blue header row, grid borders |
| Inline images (`![alt](path.png)`) | Embedded, resized to page content width |
| Fragment links (`[text](#anchor)`) | Internal Word hyperlinks to bookmarked headings |

## Limitations

- Loop-specific output (clipboard) — use the `convert-to-loop` skill instead.
- PDF export not supported (planned future enhancement).
- Bold/italic formatting in tables may not be preserved (htmldocx limitation).

## Error Handling

- **`ImportError` mentioning `lxml` or `docx`**: the venv may have a broken install — delete `%LOCALAPPDATA%/agency-plugins/docpilot/venv` (Windows) or the equivalent cache dir (`~/Library/Caches/agency-plugins/docpilot/venv` on macOS, `~/.cache/agency-plugins/docpilot/venv` on Linux) and re-run.
- **First-run pip install fails**: ensure the user has network access to PyPI and Python 3.11+.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: convert-to-loop
description: Convert a Markdown file to styled HTML and copy it to the Windows clipboard, ready to paste into Microsoft Loop with full formatting preserved.
tier: standard
applyTo: '**/*docx*,**/*word*,**/*loop*,**/*convert*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Convert Markdown → Microsoft Loop

Convert a Markdown file to rich HTML and place it on the Windows clipboard. The user then presses **Ctrl+V** in any Loop page and the headings, tables, code blocks, and inline formatting paste with full styling.

> **Windows-only**: the Loop converter writes to the Windows clipboard via Win32 APIs. Use `convert-to-docx` for cross-platform output.

## When to Use

- User says "send this to Loop", "paste into Loop", "copy for Loop"
- User wants to share a Markdown spec in a Microsoft Loop workspace, page, or component
- User has a `.md` file open and wants its content as a Loop-ready clipboard payload

## How to Respond

### Step 1 — If the user provided a file path

Run:

```bash
python plugins/docpilot/scripts/venv-run.py plugins/docpilot/scripts/convert.py "<input.md>" --to loop
```

After it succeeds, tell the user verbatim:

> HTML copied to clipboard — open a Loop page and press Ctrl+V.

### Step 2 — If no file path was provided

1. Use the Glob tool to find `**/*.md` files under the current working directory, excluding `.git`, `.claude`, `node_modules`, and `__pycache__`. Take the 4 most recently modified.
2. Use the AskUserQuestion tool with those files as options:
   - `label`: filename only (e.g. `spec.md`)
   - `description`: relative directory (e.g. `docs/` or `.`)
   The user can also pick "Other" to type a path manually.
3. Once chosen, run:
   ```bash
   python plugins/docpilot/scripts/venv-run.py plugins/docpilot/scripts/convert.py "<chosen_file>" --to loop
   ```
4. Tell the user: "HTML copied to clipboard — open a Loop page and press Ctrl+V."

## Notes

- **Do not add `--open`** — the output goes to the clipboard, not a file.
- Single-line fenced code blocks are automatically converted to inline backtick code so they paste cleanly into Loop.
- Multi-line code blocks paste as Loop code blocks.
- Local images (`![alt](path.png)`) are embedded as base64 data URIs so they render correctly in Loop.
- Table-of-Contents section links do not navigate in Loop — a small notice is automatically inserted under any TOC heading.

## Limitations

- **Windows only**: requires `ctypes.windll` for the clipboard write. On macOS or Linux this skill will fail; suggest `convert-to-docx` instead.
- Loop's paste handler ignores some HTML attributes (e.g. inline styles on `<span>`). What you see in Word may differ from what Loop renders.

## Error Handling

- **`OSError: [WinError ...]`** while writing to the clipboard: another application may be holding the clipboard. Retry once.
- **`ImportError`**: see the `convert-to-docx` skill's error-handling section — same venv applies.
- **Skill invoked on non-Windows**: tell the user the Loop path is Windows-only and suggest `/docpilot:convert-to-docx` instead.
