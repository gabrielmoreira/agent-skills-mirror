# X Articles - Detailed Guide

Publish Markdown articles to X Articles editor with rich text formatting and images.

## Mode Selection

In Codex, prefer **Chrome Computer Use** when available:

1. If Computer Use tools are already visible, call `get_app_state` for `Google Chrome`.
2. If not, use `tool_search` for `computer-use get_app_state click press_key drag scroll Google Chrome`, then call `get_app_state`.
3. If that succeeds, use the Computer Use workflow below.
4. Use the CDP script workflow only when Computer Use is unavailable or explicitly requested.

If the user explicitly asks for Chrome Computer Use, do not fall back to CDP, Playwright, or the in-app Browser without approval.

## Prerequisites

- X Premium subscription (required for Articles)
- Google Chrome installed
- `bun` installed

## Usage

### Chrome Computer Use (Codex Preferred)

Prepare the article HTML and image map:

```bash
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/x-article-body.html > /tmp/x-article.json
```

Copy the generated HTML as rich text:

```bash
${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/x-article-body.html
```

Then use Codex Computer Use against `Google Chrome` for all X UI operations.

### CDP Script Fallback

```bash
# Publish markdown article (preview mode)
${BUN_X} {baseDir}/scripts/x-article.ts article.md

# With custom cover image
${BUN_X} {baseDir}/scripts/x-article.ts article.md --cover ./cover.jpg

# Actually publish
${BUN_X} {baseDir}/scripts/x-article.ts article.md --submit
```

Do not use `--submit` unless the user has explicitly confirmed the final public publish action.

## Markdown Format

```markdown
---
title: My Article Title
cover_image: /path/to/cover.jpg
---

# Title (becomes article title)

Regular paragraph text with **bold** and *italic*.

## Section Header

More content here.

![Image alt text](./image.png)

- List item 1
- List item 2

1. Numbered item
2. Another item

> Blockquote text

[Link text](https://example.com)

\`\`\`
Code blocks become blockquotes (X doesn't support code)
\`\`\`
```

## Frontmatter Fields

| Field | Description |
|-------|-------------|
| `title` | Article title (or uses first H1) |
| `cover_image` | Cover image path or URL |
| `cover` | Alias for cover_image |
| `image` | Alias for cover_image |

## Image Handling

1. **Cover Image**: First image or `cover_image` from frontmatter
2. **Remote Images**: Automatically downloaded to temp directory
3. **Placeholders**: Images in content use `XIMGPH_N` format
4. **Insertion**: Placeholders are found, selected, and replaced with actual images

## Markdown to HTML Script

Convert markdown and inspect structure:

```bash
# Get JSON with all metadata
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md

# Output HTML only
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --html-only

# Save HTML to file
${BUN_X} {baseDir}/scripts/md-to-html.ts article.md --save-html /tmp/article.html
```

JSON output:
```json
{
  "title": "Article Title",
  "coverImage": "/path/to/cover.jpg",
  "contentImages": [
    {
      "placeholder": "XIMGPH_1",
      "localPath": "/tmp/x-article-images/img.png",
      "blockIndex": 5
    }
  ],
  "html": "<p>Content...</p>",
  "totalBlocks": 20
}
```

## Supported Formatting

| Markdown | HTML Output |
|----------|-------------|
| `# H1` | Title only (not in body) |
| `## H2` - `###### H6` | `<h2>` |
| `**bold**` | `<strong>` |
| `*italic*` | `<em>` |
| `[text](url)` | `<a href>` |
| `> quote` | `<blockquote>` |
| `` `code` `` | `<code>` |
| ```` ``` ```` | `<blockquote>` (X limitation) |
| `- item` | `<ul><li>` |
| `1. item` | `<ol><li>` |
| `![](img)` | Image placeholder |

## Computer Use Workflow (Preferred in Codex)

1. **Detect Computer Use**: call `get_app_state` for `Google Chrome`; use `tool_search` first if the tools are not visible.
2. **Parse Markdown**: run `md-to-html.ts --save-html /tmp/x-article-body.html > /tmp/x-article.json`.
3. **Read the map**: use `/tmp/x-article.json` for `title`, `coverImage`, and `contentImages`.
4. **Open X Articles**: use Chrome Computer Use to navigate to `https://x.com/compose/articles`.
5. **Create Draft**: click the create/write button if needed, or open the target draft.
6. **Upload Cover**: if `coverImage` exists, use Chrome's visible upload/file picker UI. If the file picker cannot be operated reliably, stop and ask for help rather than switching to CDP silently.
7. **Fill Title**: type the title into the title field.
8. **Paste Content**:
   - Run `copy-to-clipboard.ts html --file /tmp/x-article-body.html`.
   - Click the article body.
   - Press `super+v` on macOS or `control+v` on Windows/Linux with Computer Use.
9. **Insert Images**: for each `contentImages` item in placeholder order:
   - Run `copy-to-clipboard.ts image <localPath>`.
   - Select the exact placeholder text (`XIMGPH_N`) in the editor.
   - Press `super+v`/`control+v` with Computer Use.
   - Wait for X to finish uploading media.
   - If `XIMGPH_N` remains above the inserted image, reselect that exact text and press `BackSpace`.
   - Do not press `BackSpace` unless the Computer Use state confirms the selected text is exactly the placeholder.
10. **Verify**:
   - Inspect the Computer Use state for `XIMGPH_` residue.
   - Confirm the expected number of image blocks is visible.
   - Open Preview and verify title, cover, body, links, and images.
11. **Publish Safety**: ask the user for explicit final confirmation before clicking `Publish`.

## CDP Script Workflow (Fallback)

1. **Parse Markdown**: Extract title, cover, content images, generate HTML
2. **Launch Chrome**: Real browser with CDP, persistent login
3. **Navigate**: Open `x.com/compose/articles`
4. **Create Article**: Click create button if on list page
5. **Upload Cover**: Use file input for cover image
6. **Fill Title**: Type title into title field
7. **Paste Content**: Copy HTML to clipboard, paste into editor
8. **Insert Images**: For each placeholder (reverse order):
   - Find placeholder text in editor
   - Select the placeholder
   - Copy image to clipboard
   - Paste to replace selection
9. **Post-Composition Check** (automatic):
   - Scan editor for remaining `XIMGPH_` placeholders
   - Compare expected vs actual image count
   - Warn if issues found
10. **Review**: Browser stays open for 60s preview
11. **Publish**: Only with `--submit` flag and explicit user confirmation

## Example Session

```
User: /post-to-x article ./blog/my-post.md --cover ./thumbnail.png

Claude:
1. Detects Chrome Computer Use
2. Parses markdown: title="My Post", 3 content images
3. Saves `/tmp/x-article-body.html` and `/tmp/x-article.json`
4. Uses Chrome Computer Use to open X Articles and create a draft
5. Uploads thumbnail.png as cover
6. Fills title "My Post"
7. Pastes HTML content with a real Chrome paste
8. Inserts 3 images at placeholder positions
9. Opens Preview and asks before publishing
```

## Troubleshooting

- **No create button**: Ensure X Premium subscription is active
- **Cover upload fails**: Check file path and format (PNG, JPEG)
- **Images not inserting**: Verify placeholders exist in pasted content
- **Content not pasting**: Check HTML clipboard: `${BUN_X} {baseDir}/scripts/copy-to-clipboard.ts html --file /tmp/test.html`
- **Computer Use unavailable**: Use the CDP fallback script, unless the user explicitly required Chrome Computer Use.
- **Placeholder remains after paste**: Select only the placeholder text and press BackSpace after upload completes.

## How It Works

1. `md-to-html.ts` converts Markdown to HTML:
   - Extracts frontmatter (title, cover)
   - Converts markdown to HTML
   - Replaces images with unique placeholders
   - Downloads remote images locally
   - Returns structured JSON

2. Chrome Computer Use publishes through the user's visible Chrome UI:
   - Uses the user's active Chrome profile and logged-in X session
   - Uses `copy-to-clipboard.ts` for rich HTML and image clipboard payloads
   - Uses real keystrokes (`super+v`/`control+v`) through Codex Computer Use
   - Keeps the final publish click under user confirmation

3. `x-article.ts` publishes via CDP as a fallback:
   - Launches real Chrome (bypasses detection)
   - Uses persistent profile (saved login)
   - Navigates and fills editor via DOM manipulation
   - Pastes HTML from system clipboard
   - Finds/selects/replaces each image placeholder
