# Templates Guide — Creating Effective Document Templates

How to create and use templates for each supported format. Templates produce polished, branded output with minimal effort.

---

## Why Templates?

Templates separate **content** from **presentation**. Instead of coding fonts, colors, and layouts programmatically, you design once in the native application (PowerPoint, Word, Excel) and inject data at generation time.

| Approach | Pros | Cons |
|----------|------|------|
| With template | Branded, professional output; designers can create templates; content injection is simple | Requires upfront template creation; placeholder mapping |
| Without template | Quick; no dependencies on template files; fully programmatic | Generic appearance; styling requires code; harder to maintain consistency |

**Recommendation**: Always ask the user for a template. Most organizations have branded templates already.

---

## PowerPoint Templates (.pptx)

### How It Works

python-pptx opens the template file and uses its **slide layouts** to create new slides. Each layout has named **placeholders** (title, body, image, etc.) that receive content.

### Creating a Template

1. **Open PowerPoint** → Create a new presentation
2. **View → Slide Master** → Design your master layouts:
   - Title Slide (layout 0 by default)
   - Title and Content (layout 1)
   - Section Header (layout 2)
   - Custom layouts as needed
3. Each layout should have **named placeholders**:
   - Title placeholder (always index 0)
   - Content/body placeholder (typically index 1)
   - Additional placeholders for images, captions, etc.
4. **Set fonts, colors, backgrounds** in the Slide Master — these will be inherited
5. **Save as .pptx**

### Placeholder Discovery

To see what placeholders a template offers:

```python
from pptx import Presentation

prs = Presentation("template.pptx")
for i, layout in enumerate(prs.slide_layouts):
    print(f"Layout {i}: {layout.name}")
    for ph in layout.placeholders:
        print(f"  [{ph.placeholder_format.idx}] {ph.name} ({ph.placeholder_format.type})")
```

### Mapping Rules

| JSON Field | Maps To |
|-----------|---------|
| `layout` | Slide layout name (matched against `layout.name`) |
| `title` | Placeholder index 0 (title) |
| `body` | Placeholder index 1 (content) |
| `notes` | Notes slide text frame |
| `image_path` | Added as picture shape (if no image placeholder exists) |

### Best Practices

- **Name your layouts clearly** (e.g., "Title Slide", "Content with Image", "Two Column") — the script matches by name
- **Keep placeholder indices consistent** — title always 0, body always 1
- **Include a blank layout** for slides that need full custom content
- **Test with a sample slide** before generating 50 slides from a template
- **Don't delete the default layouts** even if unused — some themes reference them

---

## Word Templates (.docx)

### How It Works

docxtpl uses **Jinja2 template syntax** directly inside the Word document. You type `{{ variable }}` and `{% for %}...{% endfor %}` blocks right in Word, and docxtpl replaces them with data at render time.

### Creating a Template

1. **Open Word** → Create your document layout
2. **Type Jinja2 tags** where data should appear:
   - Simple variable: `{{ title }}`
   - Loop: `{% for item in items %}`...`{% endfor %}`
   - Conditional: `{% if show_chart %}`...`{% endif %}`
3. **Format the surrounding text** — the format of the tag text is inherited by the rendered content
4. **Save as .docx**

### Common Tag Patterns

**Simple variables:**
```
Report Title: {{ title }}
Date: {{ date }}
Author: {{ author }}
```

**Lists:**
```
{% for item in items %}
• {{ item.name }}: {{ item.description }}
{% endfor %}
```

**Tables (row repetition):**
```
| Name            | Status          | Notes           |
| --------------- | --------------- | --------------- |
{% for row in rows %}
| {{ row.name }}  | {{ row.status }}| {{ row.notes }} |
{% endfor %}
```

**Conditionals:**
```
{% if include_appendix %}
Appendix A: Detailed Data
{{ appendix_content }}
{% endif %}
```

**Images:**
```python
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm

doc = DocxTemplate("template.docx")
image = InlineImage(doc, "chart.png", width=Mm(120))
doc.render({"chart": image})
doc.save("output.docx")
```
In the template, use `{{ chart }}` where the image should appear.

### Critical Rules

- **Type the entire tag in one go.** If you type `{{ `, apply bold, then type `title }}`, Word creates multiple text runs and docxtpl can't parse the tag.
- **Fix broken tags**: Select the tag → Clear All Formatting → Retype if needed
- **Use Word's Find & Replace** to verify all tags are intact: search for `{{` and count matches
- **Test with minimal data first** before passing the full dataset

---

## Excel Templates (.xlsx)

### How It Works

openpyxl opens the template with `load_workbook()`, preserving all formatting, formulas, charts, and styles. You then write data into specific cells.

### Creating a Template

1. **Open Excel** → Design your spreadsheet:
   - Headers in row 1 with formatting (bold, colors, filters)
   - Named ranges for data areas if needed
   - Charts referencing data ranges (they update when data changes)
   - Conditional formatting rules
2. **Leave data rows empty** — the script fills them
3. **Save as .xlsx**

### Data Injection Patterns

**Direct cell writing** (best for known positions):
```python
ws["A2"] = "First value"
ws["B2"] = 42
```

**Row-by-row** (best for tabular data):
```python
start_row = 2  # row 1 is headers
for i, row_data in enumerate(data["rows"]):
    for j, value in enumerate(row_data):
        ws.cell(row=start_row + i, column=j + 1, value=value)
```

**Named ranges** (most robust):
```python
for named_range in wb.defined_names.definedName:
    if named_range.attr_text == "DataStart":
        # Parse the cell reference and start writing from there
        pass
```

### Best Practices

- **Don't use `ws.append()`** on template sheets — it ignores existing formatting
- **Preserve chart references**: If the template has charts pointing to `A1:C10`, make sure data fills that exact range
- **Use number formats**: Set cell format in the template (currency, percentage, date) — openpyxl preserves them
- **Auto-filter**: If the template has auto-filters, they stay active after data injection
- **Hidden columns/rows**: They remain hidden — useful for intermediate calculation columns

---

## CSS Templates for PDF

### How It Works

WeasyPrint renders HTML to PDF using CSS for styling. The CSS file acts as your template — controlling fonts, margins, headers, footers, and page layout.

### Creating a CSS Template

```css
/* Page setup */
@page {
    size: A4;
    margin: 2.5cm 2cm;

    @top-left { content: "Company Name"; font-size: 9pt; color: #666; }
    @top-right { content: string(section-title); font-size: 9pt; color: #666; }
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 9pt; }
}

/* First page — no header */
@page :first {
    @top-left { content: ""; }
    @top-right { content: ""; }
}

/* Typography */
body {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #1a5276;
    font-size: 24pt;
    border-bottom: 3px solid #1a5276;
    padding-bottom: 0.3em;
    string-set: section-title content();
}

h2 {
    color: #2e86c1;
    font-size: 16pt;
    margin-top: 1.5em;
    page-break-after: avoid;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    page-break-inside: avoid;
}

th {
    background-color: #1a5276;
    color: white;
    padding: 8px 12px;
    text-align: left;
}

td {
    border: 1px solid #ddd;
    padding: 8px 12px;
}

tr:nth-child(even) { background-color: #f8f8f8; }

/* Code blocks */
pre {
    background-color: #f4f4f4;
    padding: 1em;
    border-radius: 4px;
    font-size: 10pt;
    overflow-x: auto;
    page-break-inside: avoid;
}

code {
    font-family: "Cascadia Code", "Fira Code", monospace;
    font-size: 10pt;
}

/* Page breaks */
.page-break { page-break-before: always; }
```

### Best Practices

- **Use `@page` rules** for margins, headers, and footers — they appear on every page
- **Use `page-break-inside: avoid`** on tables and code blocks
- **Use `page-break-after: avoid`** on headings so they don't end up alone at page bottom
- **Font availability**: WeasyPrint uses system fonts — install the font or use `@font-face`
- **Test incrementally**: Generate a short PDF first, then style, then generate the full document

---

## General Template Best Practices

1. **Version control your templates** — store them alongside the project in Git
2. **Document placeholder names** — maintain a table of `{{ tag }}` → meaning for each template
3. **Test with edge cases**: empty data, very long text, special characters, missing optional fields
4. **Keep templates simple** — complex nested loops and conditionals are hard to debug
5. **Provide sample JSON** alongside each template so users know the expected data shape
