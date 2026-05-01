# Troubleshooting — Markdown to Document Generation

Common issues encountered during document generation and their solutions.

---

## Installation Issues

### python-pptx fails to install

**Symptom**: `pip install python-pptx` fails with build errors.

**Solutions**:
1. Ensure Python 3.8+: `python --version`
2. Upgrade pip: `pip install --upgrade pip`
3. Install in a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   source .venv/bin/activate  # Linux/macOS
   pip install python-pptx
   ```

### WeasyPrint fails to install

**Symptom**: Installation errors related to missing system dependencies (cairo, pango, gdk-pixbuf).

**Solutions**:
- **Windows**: Install GTK3 runtime or use `pip install weasyprint` (recent versions bundle dependencies)
- **Linux (Debian/Ubuntu)**:
  ```bash
  apt install python3-pip libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2
  pip install weasyprint
  ```
- **macOS**:
  ```bash
  brew install pango
  pip install weasyprint
  ```
- Use pandoc as fallback: `pandoc input.md -o output.pdf --pdf-engine=xelatex`

### MPXJ fails — Java not found

**Symptom**: `jpype.JVMNotFoundException` or `No JVM shared library file (jvm.dll) found`.

**Solutions**:
1. Verify Java is installed: `python scripts/runtime_resolver.py java --min-version 11`
2. Install Java JDK 11+:
   - **Windows**: `choco install temurin17` or download from https://adoptium.net
   - **Linux**: `apt install openjdk-17-jdk`
   - **macOS**: `brew install openjdk@17`
3. Set `JAVA_HOME` environment variable:
   ```bash
   # Windows (PowerShell)
   $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17"
   # Linux/macOS
   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
   ```
4. Restart the terminal after setting JAVA_HOME

### docxtpl install conflict with python-docx

**Symptom**: docxtpl requires a specific python-docx version.

**Solutions**:
1. Install docxtpl first — it will pull the correct python-docx version:
   ```bash
   pip install docxtpl
   ```
2. If already installed, reinstall:
   ```bash
   pip install --force-reinstall docxtpl
   ```

---

## Template Issues

### PPTX: Placeholder not found

**Symptom**: Script raises `KeyError` or placeholders appear empty after generation.

**Solutions**:
1. List available placeholders in the template:
   ```python
   from pptx import Presentation
   prs = Presentation("template.pptx")
   for layout in prs.slide_layouts:
       print(f"Layout: {layout.name}")
       for ph in layout.placeholders:
           print(f"  [{ph.placeholder_format.idx}] {ph.name}: {ph.placeholder_format.type}")
   ```
2. Use placeholder index instead of name — names vary between templates
3. Ensure the template has **slide layouts**, not just slides — new slides inherit from layouts

### PPTX: Layout name mismatch

**Symptom**: Script uses "Title and Content" but template has "Title, Content" or a localized name.

**Solutions**:
1. Print all layout names (see above) and match exactly
2. Fall back to index-based matching: `prs.slide_layouts[1]`
3. Use fuzzy matching in your code if multiple templates are expected

### DOCX: Jinja2 tags not rendered

**Symptom**: Output contains literal `{{ variable }}` text instead of rendered values.

**Solutions**:
1. Ensure tags are in the same text run in Word — formatting mid-tag breaks parsing:
   - ❌ `{{ var` (bold) `iable }}` (normal) — Word splits into multiple runs
   - ✅ `{{ variable }}` — type the whole tag at once, then format
2. Use docxtpl's `RichText` for formatted output
3. Clear formatting on the tag text: select the tag → Clear All Formatting in Word

### DOCX: Table rows not expanding in loop

**Symptom**: `{% for %}` loop in a table only renders one row.

**Solutions**:
1. The `{% for %}` and `{% endfor %}` tags must be in cells of their own row
2. Correct table structure:
   ```
   | {% for item in items %} |              |
   | {{ item.name }}         | {{ item.val }}|
   | {% endfor %}            |              |
   ```
3. Or use docxtpl's table syntax: put tags in a single row that will be duplicated

### XLSX: Template formatting lost

**Symptom**: After writing data with openpyxl, cell formatting from the template is gone.

**Solutions**:
1. Write values only — don't overwrite formatting:
   ```python
   ws.cell(row=2, column=1).value = "New data"  # preserves existing format
   ```
2. Don't use `ws.append()` on template worksheets — it adds rows without formatting
3. Copy formatting from template rows before writing if needed

---

## Runtime Dependency Issues

### Java: JAVA_HOME set but MPXJ still fails

**Symptom**: `JAVA_HOME` is configured but jpype can't find `jvm.dll` / `libjvm.so`.

**Solutions**:
1. JAVA_HOME must point to the JDK root, not the `bin/` directory:
   - ❌ `JAVA_HOME=C:\Program Files\Java\jdk-17\bin`
   - ✅ `JAVA_HOME=C:\Program Files\Java\jdk-17`
2. Run `runtime_resolver.py` to auto-detect: `python scripts/runtime_resolver.py java`
3. On Windows, check both `jdk` and `jre` paths in Program Files

### Pandoc: "pandoc not found"

**Symptom**: `FileNotFoundError` when running pandoc commands.

**Solutions**:
1. Verify installation: `pandoc --version`
2. Install: `choco install pandoc` (Windows), `apt install pandoc` (Linux), `brew install pandoc` (macOS)
3. If recently installed, restart the terminal to reload PATH

### WeasyPrint: "cairo not found" on Linux

**Symptom**: `OSError: no library called "cairo-2" was found`.

**Solutions**:
```bash
apt install libcairo2-dev
# or
apt install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

---

## Encoding Issues

### Non-ASCII characters garbled in output

**Symptom**: Accented characters, CJK, or emoji appear as `?` or boxes in generated documents.

**Solutions**:
1. Ensure JSON input is UTF-8:
   ```python
   with open("data.json", encoding="utf-8") as f:
       data = json.load(f)
   ```
2. For PPTX/DOCX: python-pptx and docxtpl handle Unicode natively — the issue is usually in the input file
3. For PDF: ensure the CSS specifies a font that supports the characters:
   ```css
   body { font-family: "Noto Sans", "Arial Unicode MS", sans-serif; }
   ```
4. For Excel: openpyxl handles Unicode natively

### PDF: Fonts not rendering correctly

**Symptom**: PDF uses fallback font; custom fonts from CSS are ignored.

**Solutions**:
1. Install the font on the system — WeasyPrint uses system fonts
2. Use `@font-face` in CSS with a local file path:
   ```css
   @font-face {
       font-family: "Custom Font";
       src: url("fonts/CustomFont.ttf");
   }
   ```
3. On Linux, run `fc-cache -fv` after installing fonts

---

## Format-Specific Issues

### PPTX: Images not appearing

**Symptom**: Slides are generated but images referenced in JSON are missing.

**Solutions**:
1. Verify image paths are absolute or relative to the script's working directory
2. Supported formats: PNG, JPEG, GIF, BMP, TIFF — SVG is not supported by python-pptx
3. Check image dimensions — very large images may cause memory issues

### DOCX: Page breaks ignored

**Symptom**: Content runs together without page breaks.

**Solutions**:
1. Use python-docx page breaks:
   ```python
   from docx.enum.text import WD_BREAK
   doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
   ```
2. In docxtpl templates, insert a Word page break in the template itself

### XLSX: Numbers stored as text

**Symptom**: Excel shows a green triangle warning; numbers won't calculate.

**Solutions**:
1. Ensure values are Python numbers, not strings:
   ```python
   ws.cell(row=2, column=1, value=42)      # ✅ number
   ws.cell(row=2, column=1, value="42")     # ❌ text
   ```
2. Parse from JSON with type conversion:
   ```python
   value = float(raw_value) if raw_value.replace(".", "").isdigit() else raw_value
   ```

### PDF: Tables break across pages badly

**Symptom**: Table rows are split mid-cell at page boundaries.

**Solutions**:
1. Add CSS to prevent row splitting:
   ```css
   tr { page-break-inside: avoid; }
   ```
2. For very long tables, consider splitting into sections with headers repeated:
   ```css
   thead { display: table-header-group; }
   ```
3. Use `page-break-before: always;` on section headings to control flow

### MSPDI: MS Project won't import the XML

**Symptom**: MS Project shows import error or ignores tasks.

**Solutions**:
1. Ensure the XML uses the correct MSPDI namespace — MPXJ handles this automatically
2. Check date formats: MSPDI expects ISO 8601 (`2026-03-11T08:00:00`)
3. Verify task UIDs are unique — MPXJ generates them automatically
4. Try opening in Project Professional instead of Project Online — online has stricter validation
