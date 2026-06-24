---
name: format-references-zotero
description: Zotero reference formatting workflow. Converts [PMID: xxxx] markers in Markdown manuscripts to Word (.docx) with native Zotero field codes (ADDIN ZOTERO_ITEM / ADDIN ZOTERO_BIBL). Users click "Refresh" once in Word to complete formatting. Includes search_styles.py for searchin...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Medical Literature Reference Formatter — Zotero Edition

Converts `[PMID: xxxx]` markers directly to native Word Zotero field codes, maintaining full editability: users can switch citation styles in Zotero at any time and Refresh once in Word to update the entire document.

## Workflow

### Step 0 — Check Environment (first run or on error)

```bash
python "<skill_dir>/scripts/check_env.py"
```

Checks: Python, python-docx, Pandoc, PubMed API, Zotero installation and running status.

If it reports `.ris not associated with Zotero`, ask the user if they want to fix it. If they agree, run:

```bash
python "<skill_dir>/scripts/check_env.py" --fix-ris
```

### Step 1 — Confirm Target File

Ask when user has not provided a full path. Desktop path: `C:\Users\<username>\Desktop\<filename>.md`

### Step 2 — Confirm Citation Style

Default is `nature`. If the user specifies another style (e.g., Vancouver, Elsevier, APA), first confirm it is installed:

```bash
python "<skill_dir>/scripts/search_styles.py" <keyword>          # search available styles
python "<skill_dir>/scripts/search_styles.py" --install <style-id>  # download and install
```

Styles are automatically installed to Zotero's local styles directory (located via `prefs.js`, cross-platform).

### Step 3 — Run Processing Script

```bash
python "<skill_dir>/scripts/process_references.py" "<absolute_path>" [--style <style-id>]
```

Default style is `nature`; you can specify any installed style ID:

```bash
python "<skill_dir>/scripts/process_references.py" "paper.md" --style elsevier-harvard
python "<skill_dir>/scripts/process_references.py" "paper.md" --style vancouver
```

Script completes: PMID extraction → PubMed metadata → generate .docx with Zotero fields (including ZOTERO_PREF) → generate .ris → auto-open.

### Step 3.5 — Change Style / Force Refresh Cache

```bash
python "<skill_dir>/scripts/process_references.py" "paper.md" --style vancouver
python "<skill_dir>/scripts/process_references.py" "paper.md" --force-refresh   # clear cache, re-fetch from PubMed
```

Cache file `<stem>_pubmed_cache.json` is auto-generated in the same directory as the `.md` file, avoiding redundant PubMed fetches. After adding new PMIDs, just run normally — existing references use cache, only new ones are fetched.

### Step 4 — Integrity Check

After fetching from PubMed, the script automatically checks: if any PMID fetch failed, it lists the specific IDs and suggests retrying with `--force-refresh`.

### Step 5 — Common Issues

**Pandoc not installed**: https://pandoc.org/installing.html

**python-docx not installed**: `pip install python-docx`

**PubMed inaccessible**: Network issue, retry later.

**Zotero not running**: Open Zotero desktop app — Word Refresh requires it to format citations.

**Style not installed**: Run `search_styles.py --install <style-id>` to auto-download and install.

### Step 6 — Inform User

> Document generated, .ris imported into Zotero library. Click "Refresh" in the Zotero tab in Word to complete formatting. To change styles later, run change_style.py with the new style, then Refresh once to update the entire document.

## Output Files

| File | Description |
|------|------|
| `<stem>-zotero.docx` | Word document with Zotero field codes |
| `<stem>.ris` | Reference data for Zotero library import (shared with EndNote edition) |
| `<stem>_pubmed_cache.json` | PubMed metadata cache to avoid redundant fetches |

## Citation Style Management (search_styles.py)

This skill includes `search_styles.py` for searching and installing CSL citation styles — **no need to leave the command line or manually download .csl files**.

### Search Available Styles

```bash
python "<skill_dir>/scripts/search_styles.py" <keyword>
```

Keywords can be journal names or style names, for example:

```bash
python "<skill_dir>/scripts/search_styles.py" science       # search Science-related styles
python "<skill_dir>/scripts/search_styles.py" nature        # search Nature-related styles
python "<skill_dir>/scripts/search_styles.py" vancouver     # search Vancouver numbered styles
python "<skill_dir>/scripts/search_styles.py" elsevier      # search Elsevier journal styles
python "<skill_dir>/scripts/search_styles.py" chinese       # search Chinese journal styles
```

### Install Style to Zotero

Find the desired `style ID` from search results, then install:

```bash
python "<skill_dir>/scripts/search_styles.py" --install <style-id>
```

Examples:

```bash
python "<skill_dir>/scripts/search_styles.py" --install science         # Science journal
python "<skill_dir>/scripts/search_styles.py" --install vancouver-nlm   # Vancouver numbered
python "<skill_dir>/scripts/search_styles.py" --install nature          # Nature
python "<skill_dir>/scripts/search_styles.py" --install elsevier-harvard # Elsevier Harvard
```

Styles are automatically downloaded to Zotero's local styles directory (`~Zotero/styles/`). After restarting Zotero, they become available in Word.

### Generate Word Document with Installed Style

After installing a style, specify the installed style ID via `--style` in Step 3's `process_references.py`:

```bash
python "<skill_dir>/scripts/process_references.py" "paper.md" --style science
python "<skill_dir>/scripts/process_references.py" "paper.md" --style vancouver-nlm
```

### Supported Style Sources

The script searches from the Zotero official style repository (`https://www.zotero.org/styles`), **covering 9000+ journal and institution CSL styles**, including but not limited to:

- Science / Nature / Cell / PNAS / JAMA / NEJM / Lancet / BMJ
- APA / MLA / Chicago / Vancouver / Harvard
- University thesis formats
- Chinese journals (Chinese Science Bulletin, Science China, etc.)
- Publisher-specific formats (Elsevier, Springer, Taylor & Francis, etc.)

## Field Code Mechanism

The script replaces each `[PMID: xxxx]` with an `ADDIN ZOTERO_ITEM CSL_CITATION` field containing complete CSL JSON metadata, and inserts an `ADDIN ZOTERO_BIBL` field at the end. Zotero's Word plugin recognizes these fields and formats all citations and bibliography according to the current style on Refresh.

Process:
1. Pandoc compiles Markdown to intermediate .docx (with `ZRCITE{pmid}` markers)
2. python-docx opens .docx, replaces markers with Word field codes (w:fldChar / w:instrText)
3. Injects ZOTERO_PREF field to ensure style persistence after Refresh

## Requirements

- **Python 3.7+**
- **python-docx** — `pip install python-docx`
- **Pandoc** — https://pandoc.org/installing.html
- **Zotero desktop** + Word plugin (Zotero must be running during Refresh)
- **Network** — access to PubMed API

## Input Validation

This skill accepts requests that match the documented purpose of `format-references-zotero` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `format-references-zotero` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
