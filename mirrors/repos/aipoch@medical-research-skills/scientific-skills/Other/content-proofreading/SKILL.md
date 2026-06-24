---
name: content-proofreading
description: An academic proofreading skill for Chinese/English manuscripts, triggered when you need automated checks for spelling, grammar, terminology consistency, and formatting before submission.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


## When to Use

- You are preparing an academic paper for journal/conference submission and need a final language + formatting pass.
- You have bilingual (Chinese/English) content and want consistent punctuation, wording, and style across both languages.
- Your manuscript contains domain terminology (e.g., life sciences) and you need consistent Chinese–English term mapping and abbreviation rules.
- You need to validate references, numbers/units, and heading levels against a required style (APA/MLA/GB/T 7714).
- You want a shareable report (HTML or Markdown annotations) with precise error locations and revision suggestions.

## Agent Workflow

Follow these steps in order when the user provides text for proofreading:

### Step 1: Identify Input Source
- Determine if the user pasted text directly, provided a file path, or attached a `.docx`/`.md` file.
- If a file path is given, read the file content. If a `.docx` file, use `word_converter.py` to extract text first.
- If the user provided only text inline, use that text directly.

### Step 2: Determine Language Scope
- Check if the content is English, Chinese, or bilingual (both).
- Set language parameter accordingly: `en`, `zh`, or `both`.
- If the user did not specify, auto-detect from content.

### Step 3: Run English Checks (if applicable)
- If English content is detected, call `EnglishChecker().check(text)` to check:
  - Spelling (US/UK variants)
  - Grammar (agreement, tense, articles)
  - Punctuation (US/UK conventions)
  - Style (redundancy, passive voice)
- Collect all findings with location, type, and suggested fix.

### Step 4: Run Chinese Checks (if applicable)
- If Chinese content is detected, call `ChineseChecker().check(text)` to check:
  - Typo/misused characters
  - Grammar and collocation
  - Chinese vs English punctuation normalization
  - Academic expression optimization
- Collect all findings.

### Step 5: Run Terminology Check
- Call `TerminologyManager(domain="biology").check(text)` to verify:
  - Bidirectional Chinese–English term correspondence
  - Abbreviation rule compliance (full form on first occurrence)
  - Synonym unification to preferred standard terms
- Collect all findings.

### Step 6: Generate Report
- Feed all findings to `AnnotationGenerator(output_format="html" or "markdown")`.
- Generate the report showing:
  - Each issue with precise location (line/offset)
  - Issue type (spelling, grammar, terminology, formatting)
  - Suggested fix
- Present the report to the user. If the user requested an HTML file, save and return the file path.

### Step 7: Validate Output
- Verify all detected issues have location + type + fix.
- Confirm the output format matches the user's request (HTML/Markdown).
- If partial, label clearly as PARTIAL.

## Key Features

- **English checks**
  - Spelling (including US/UK variants)
  - Grammar (agreement, tense, articles, clause structure)
  - Punctuation conventions (US/UK)
  - Style suggestions (redundancy detection, passive voice optimization)

- **Chinese checks**
  - Typo/misused character detection (dictionary-based)
  - Grammar and collocation checks
  - Chinese vs. English punctuation normalization
  - Academic expression optimization suggestions

- **Terminology consistency**
  - Domain terminology database (life sciences by default)
  - Bidirectional Chinese–English correspondence checks
  - Abbreviation rules (require full form on first occurrence)
  - Synonym unification to preferred standard terms

- **Formatting checks**
  - Reference style validation (APA/MLA/GB/T 7714, etc.)
  - Number and unit normalization
  - Heading level consistency
  - Abbreviation consistency across the document

- **Reporting**
  - HTML interactive report or Markdown annotations
  - Precise error localization
  - Actionable revision suggestions

## Dependencies

- **Python**: `>= 3.8`

- **Python packages** (install via `pip install -r requirements.txt`)
  - `languagetool-python` (version: see `requirements.txt`) — English grammar checking
  - `opencc` (version: see `requirements.txt`) — Traditional/Simplified Chinese conversion
  - `jieba` (version: see `requirements.txt`) — Chinese tokenization
  - `pyenchant` (version: see `requirements.txt`) — spelling checks
  - `markdown` (version: see `requirements.txt`) — Markdown rendering
  - `python-docx` (version: see `requirements.txt`) — `.docx` reading
  - `docx2pdf` (version: see `requirements.txt`) — Word-to-PDF conversion

## Example Usage

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2) Run (basic)

```bash
python scripts/init_run.py --input <paper_file_path> --output <output_path>
```

### 3) Run (advanced)

```bash
python scripts/init_run.py \
  --input paper.md \
  --output report.html \
  --lang en \
  --style apa \
  --terminology biology \
  --format html
```

### 4) CLI parameters

| Parameter | Description | Default |
|---|---|---|
| `--input` | Input file path | Required |
| `--output` | Output report path | Generates an HTML report by default |
| `--lang` | Language to check (`en` / `zh` / `both`) | `both` |
| `--style` | Reference style (`apa` / `mla` / `gb`) | `apa` |
| `--terminology` | Domain terminology set | `biology` |
| `--format` | Output format (`html` / `markdown`) | `html` |
| `--no-pdf` | Skip PDF generation during Word→PDF conversion | `false` |

### 5) Use as a Python module (end-to-end)

```python
from scripts.english_checker import EnglishChecker
from scripts.chinese_checker import ChineseChecker
from scripts.terminology_manager import TerminologyManager
from scripts.annotation_generator import AnnotationGenerator

text = """
Messenger RNA (mRNA) is transcribed in the nucleus.
"""

en_checker = EnglishChecker()
zh_checker = ChineseChecker()
term_manager = TerminologyManager(domain="biology")

results = []
results.extend(en_checker.check(text))
results.extend(zh_checker.check(text))
results.extend(term_manager.check(text))

generator = AnnotationGenerator(output_format="html")
report = generator.generate(results)

with open("report.html", "w", encoding="utf-8") as f:
    f.write(report)
```

## Implementation Details

### Architecture / Core Modules

- `english_checker.py`
  - Core engine for English spelling/grammar/style checks.
  - Designed to be rule-extensible (add or register new rule sets).

- `chinese_checker.py`
  - Core engine for Chinese typo/grammar/style checks.
  - Includes a library of common academic writing error patterns.

- `terminology_manager.py`
  - Terminology database management (import/export/query/update).
  - Performs term consistency checks, bilingual mapping validation, and abbreviation policy checks.

- `annotation_generator.py`
  - Converts detected issues into a visual report (HTML) or annotated Markdown.
  - Ensures issues include **location**, **type**, and **suggested fix**.

- `word_converter.py`
  - Extracts text from `.docx`.
  - Optionally converts Word to PDF (can be disabled via `--no-pdf`).

### Terminology database format (JSON)

Organized by domain; each entry can include bilingual forms and abbreviation metadata:

```json
{
  "biology": {
    "cell": {
      "en": "cell",
      "abbrev": null,
      "full_form": null
    },
    "mrna": {
      "en": "mRNA",
      "abbrev": "mRNA",
      "full_form": "messenger RNA"
    }
  }
}
```

**Checking logic (typical):**
- If an abbreviation (e.g., `mRNA`) appears, verify the **full form** appears at first mention (e.g., `messenger RNA (mRNA)`).
- If both Chinese and English terms appear, verify they match the configured mapping for the selected domain.
- If synonyms are detected, prefer the standardized term defined in the database.

### Rule database format (JSON)

Rules are grouped by language and category:

```json
{
  "english": {
    "spelling": [],
    "grammar": [],
    "style": []
  },
  "format": {
    "references": [],
    "numbers": [],
    "units": []
  }
}
```

**How rules are applied (high level):**
- Load rule sets by `--lang` and `--style`.
- Run language-specific checks (English/Chinese) and formatting checks.
- Merge results into a unified issue list.
- Render issues into the selected output format (`html` / `markdown`) with location-aware annotations.

### Extensibility

- **Add new rules**
  1. Create a rule file under `assets/rules/`.
  2. Implement rules following the project’s rule template.
  3. Register the rule set in the rule index.
  4. Run tests to validate precision/recall and avoid false positives.

- **Add new terminology sets**
  1. Create a terminology JSON under `assets/terminology/`.
  2. Follow the domain structure shown above.
  3. Register the new domain in the terminology index so it can be selected via `--terminology`.

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.


## Input Validation

This skill accepts requests that match the documented purpose of `content-proofreading` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `content-proofreading` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
