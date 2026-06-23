# Render Test Fixture

> **STARTING-POINT NOTICE.** This file exercises every markdown feature the renderer must handle. It is not a real deliverable. Open the rendered .docx and verify each section visually.

This fixture covers:

1. Heading levels 1 through 4
2. Inline emphasis — **bold**, *italic*, _italic alt_, `inline code`
3. Bullet lists, including **bold inside bullets** and *italic inside bullets*
4. Nested numbered lists with hierarchical numbering (1.1, 1.1.1)
5. A multi-paragraph blockquote (verbatim regulation text)
6. Tables with a bold header row and **bold inside cells**
7. Horizontal rule
8. Inline literal placeholder: `[INSERT — facts]`
9. Em-dashes — like this — should not be smart-quoted away
10. Square brackets `[INSERT]` should survive

---

## 1. Headings

### 1.1 Heading level three

#### 1.1.1 Heading level four

Body paragraph following a level-four heading. The renderer should put visible spacing between the heading and the body, and headings should be in **Calibri Light** navy, not regular Calibri.

## 2. Inline emphasis everywhere

This paragraph contains **bold**, *italic*, _another italic_, and `inline code`. None of the asterisks or underscores should leak into the rendered output.

The same emphasis must work in a list item:

- A bullet with **bold text** that should render as bold, not as `**bold text**`
- A bullet with *italic text*
- A bullet with `inline code`
- A bullet with **bold** AND *italic* AND `code` mixed together
- A bullet with the literal placeholder `[INSERT — counterparty name]`

And in a numbered list:

1. **First** numbered item
2. *Second* numbered item
3. `code` numbered item
4. Bullet, *italic*, **bold**, and `code` in one item

## 3. Nested lists

- Top-level bullet
  - Second-level bullet
    - Third-level bullet
- Another top-level
  - Second level here too

Numbered with nesting:

1. Top level
   1. Sub-item one
   2. Sub-item two
      1. Sub-sub-item
2. Top level continued

## 4. Multi-paragraph blockquote (verbatim regulation)

> "Connected products shall be designed and manufactured, and related services shall be designed and provided, in such a manner that product data and related service data, including the relevant metadata necessary to interpret and use those data, are, by default, easily, securely, free of charge, in a comprehensive, structured, commonly used and machine-readable format, and, where relevant and technically feasible, directly accessible to the user."
>
> — Article 3(1) of Regulation (EU) 2023/2854.
>
> This second paragraph of the blockquote should remain on its own line in the rendered .docx, **not** merged into the first paragraph.

## 5. Tables

| Field | Article | Status | Severity |
|-------|---------|--------|----------|
| Type, format, estimated volume | **Art. 3(2)(a)** | OK | — |
| Continuous / real-time generation | **Art. 3(2)(b)** | PARTIAL | MEDIUM |
| Storage location and retention | **Art. 3(2)(c)** | GAP | **HIGH** |
| Access / retrieval / erasure means | **Art. 3(2)(d)** | OK | — |

Table cells should render with **bold** intact when the source markdown has it. Header row should be bold.

## 6. Inline-code blocks and literal placeholders

`[INSERT — Data Holder name and address]`

This `Article 25(2)(g)` reference should be in monospace.

`[INSERT — DD MMM YYYY]` should appear with brackets, em-dash, and content all intact.

## 7. Horizontal rule

Above the rule.

---

Below the rule. The renderer should emit a thin grey line, not a blank paragraph.

## 8. Defined terms section (representative)

- **"Data Holder"** — the entity identified at section 1 above.
- **"User"** — has the meaning given in Article 2(12) of the Data Act.
- **"FAQ"** — the European Commission's *Data Act Frequently Asked Questions*, version **1.4**, dated **22 January 2026** (non-authoritative).

## 9. Mixed-emphasis sentence

The lawyer should verify that **all of the following** render with proper emphasis: ***bold-italic***, **bold containing *italic*** inside, *italic containing **bold*** inside, and `code containing **stars**` (which should NOT be bold inside code).

## 10. Footnote-style cross references in line

See paragraph 1 above. See *paragraph 4.2 below*. See **section 6**.

## 11. Final paragraph

If every numbered section above renders correctly — bold is bold, italic is italic, inline code is monospace, the blockquote stays multi-paragraph, the table preserves emphasis, the horizontal rule shows as a line, em-dashes survive, square brackets survive, and headings use the navy Calibri Light style — the renderer is good to ship.
