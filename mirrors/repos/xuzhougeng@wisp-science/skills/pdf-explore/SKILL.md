---
name: pdf-explore
description: "Use this skill when the user has attached a PDF, paper, report, or other document and the answer needs its content: summarize a section, compare sections, read specific pages, check the table of contents, or read a value off a figure. The `read` tool cannot parse PDF binary — python is the extraction path. Provides `pdf_pages` (pages as text or rendered PNGs, cached) and `pdf_outline` (embedded-bookmark TOC) in the persistent python kernel; load them once via the Kernel Sidecar exec line that `use_skill` appends. For PDF creation/manipulation, use reportlab/pypdf directly."
fold_cue: "instead_of=read use=pdf_pages/pdf_outline for PDFs — read cannot parse PDF binary; print ≤5 pages, else write to a file and read that"
license: Apache-2.0
---

# Read PDFs page-by-page, not wholesale

`read` chokes on PDF binary, and pasting a 50-page document costs 40K+
tokens. The sidecar parses once into the persistent Python kernel (memory +
disk cached), after which you pull exactly the pages the question needs.

**Setup, once per session:** run the `exec(...)` line from the "Python
Kernel Sidecar" section at the end of this skill's `use_skill` output.
Definitions survive across cells until the kernel restarts. `pypdfium2` is
required (`pillow` too for image mode); if the first call raises
ImportError, follow its hint and re-run.

## Pick the entry point

| call | use for | gives |
|---|---|---|
| `pdf_outline(path)` | any structured document — start here | `[{page, heading, level}]` from embedded bookmarks, `[]` + hint when absent |
| `pdf_pages(path, pages=[...], mode="text")` | the specific pages you need | `[{page, text, n_chars}]` |
| `pdf_pages(path, mode="image", dpi=200, pages=[N])` | figures, scans | one PNG per page in `.cache/pdf-explore/`, for `view_image` |
| default `mode="auto"` | unknown file | text, auto-switching to images when pages have no text layer |

## Map the document first

```python
toc = pdf_outline("report.pdf")
for entry in toc:
    indent = "  " * (entry["level"] - 1)
    print(f'p{entry["page"]:>3} {indent}{entry["heading"]}')
```

Costs nothing when bookmarks exist (LaTeX-compiled papers almost always
have them). On `[]`, there is no LLM fallback here — print the opening
lines of each page from `pdf_pages(path, mode="text")` and build the map
yourself. Watch for the `[pdf_outline]` offset warning: some PDFs bookmark
logical page numbers, which are shifted from file page numbers by the
front matter.

## A handful of pages: print them

```python
hits = pdf_pages("report.pdf", pages=[12, 13], mode="text")
for h in hits:
    print(f'\n[page {h["page"]}]\n{h["text"]}')
```

Fine up to roughly five pages (~2–4KB each). Kernel output past the
~16KB context budget is head/tail-truncated at ingestion, so anything
larger goes through a file instead.

## Whole sections: go through a file

For "summarize the methods", cross-section comparisons, or any multi-range
pull, write all wanted pages in one call and `read` the result — `read`
output enters context untruncated:

```python
section_pages = [5, *range(21, 26), 62, 63, 64]     # from the outline
chunks = pdf_pages("report.pdf", pages=section_pages, mode="text")
open("pull.txt", "w").write(
    "".join(f'\n[page {c["page"]}]\n{c["text"]}' for c in chunks))
print("bytes:", __import__("os").path.getsize("pull.txt"))
```

Then `read` `pull.txt`, with `offset`/`limit` when it's long. As text a
page runs ~800 tokens; as an attached image ~8K — and the parse is paid
once.

## Figures: render high, crop tight

A whole-page render can't resolve axis labels on a dense figure. Render at
high dpi, crop to the figure with PIL, and view the crop:

```python
page = pdf_pages("report.pdf", mode="image", pages=[7], dpi=200)[0]
from PIL import Image
Image.open(page["image_path"]).crop((x0, y0, x1, y1)).save("panel7.png")
```

`view_image` the crop (or the full `image_path` once, to locate the
figure). Every viewed image stays in context until `/compact` ages it out —
view the few crops that matter, never the whole render set.

## Boundaries

The reference host's LLM helpers (`pdf_scan` page ranking, `pdf_extract`
sweeps, `pdf_map` per-page summaries) require an in-kernel model bridge
Wisp doesn't provide, so they don't exist here. For an exhaustive pass,
dump pages to files in chunks (recipe above) and work through them, or hand
the on-disk text to the `explore` subagent.
