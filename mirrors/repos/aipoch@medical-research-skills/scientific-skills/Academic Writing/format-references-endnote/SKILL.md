---
name: format-references-endnote
description: EndNote reference formatting workflow — converts [PMID: xxxx] markers in Markdown manuscripts to Word (.docx) using EndNote CWYW-recognized {Author, Year, Title} placeholders, while generating .ris files for automatic import into the local EndNote library. Users click "Update ...
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


# Medical Literature Reference Formatter

This skill automates the step of turning rough `[PMID: xxxx]` citation markers into professionally formatted Word documents that work with EndNote's one-click bibliography generation. No COM automation or macros — purely file-based, stable on any machine with Python + Pandoc.

## When you're invoked

The user has a Markdown manuscript with inline `[PMID: xxxx]` markers and wants a `.docx` with citation placeholders that EndNote can resolve into a formatted bibliography.

## Workflow

### Step 0 — Check environment (first time or on error)

If this is the first run, or the user reports any unexpected error, run the bundled check script first:

```bash
python "<skill_dir>/scripts/check_env.py"
```

It verifies: Python 3.7+, Pandoc, PubMed API connectivity, EndNote installation, and `.ris` file association.

If the output shows `.ris not associated with EndNote`, ask the user: "Would you like to set .ris files to open with EndNote by default? This will allow generated files to trigger automatic import." If they agree, run:

```bash
python "<skill_dir>/scripts/check_env.py" --fix-ris
```

### Step 1 — Confirm the target file

If the user didn't specify a full path, ask. If they give a vague location like "on my Desktop", resolve it:
- Windows: `C:\Users\<username>\Desktop\<filename>.md`
- macOS: `/Users/<username>/Desktop/<filename>.md`

### Step 2 — Run the bundled processing script

The Python script is at `scripts/process_references.py` inside this skill's directory. Find the skill directory from the path this SKILL.md was loaded from, then run:

```bash
python "<skill_dir>/scripts/process_references.py" "<absolute_path_to_file.md>"
```

The script handles the entire pipeline: PMID extraction → PubMed API fetch → placeholder substitution → Pandoc compile → RIS generation → auto-open both files.

**Caching mechanism**: After the first run, a `<stem>_pubmed_cache.json` file is generated. Subsequent runs automatically reuse the cache to avoid redundant PubMed fetches. When new PMIDs are added, only the new ones are fetched.

**Force refresh**: `python process_references.py "<file>" --force-refresh` clears the cache and re-fetches all records.

### Step 3 — Handle failures gracefully

**Pandoc not found**: Tell the user to install it from https://pandoc.org/installing.html, then re-run.

**PubMed API unreachable**: The script fills failed PMIDs with `{PMIDxxxxx, n.d., [fetch failed]}` so the document is still generated. Offer to retry when network is available.

**File path issues**: Confirm the path exists and has the `.md` extension, then re-run.

**EndNote not opening automatically**: The `.ris` file association may not be configured. Tell the user to open EndNote manually and drag `references_temp.ris` into the library window.

### Step 4 — Deliver the result

After the script exits successfully, say:

> References have been automatically imported into EndNote and the document is open. Switch to the EndNote tab in Word and click "Update Citations and Bibliography" to complete formatting.

Also note the output files are saved **in the same directory as the original .md file**.

## Output files

| File | Purpose |
|------|---------|
| `<stem>-endnote.docx` | Word doc with `{Author, Year, Title}` unformatted citation placeholders |
| `<stem>.ris` | All references in RIS format — opening this imports them into EndNote |
| `<stem>_pubmed_cache.json` | PubMed metadata cache — avoids repeated network fetches |

## Why this approach works

EndNote's CWYW (Cite While You Write) engine recognizes `{Author, Year, Title}` as an "unformatted citation". When the user clicks **Update Citations**, EndNote scans the document, matches placeholders against the library, and formats them according to the selected style. This is entirely text-based — no macros, no COM, no risk of security dialogs or permission prompts.

## Title normalization

The script automatically normalizes titles to ensure EndNote CWYW can match citation placeholders against the RIS-imported library:

| Transformation | Example |
|---|---|
| Greek letters → Latin | `α-synuclein` → `alpha-synuclein` |
| Smart quotes → ASCII | `'` `"` → `'` `"` |
| Em/en dashes → hyphens | `—` → `--`, `–` → `-` |
| Brackets stripped | `[Ca²⁺]` → `Ca²⁺` |
| Commas stripped | (field delimiter in `{Author, Year, Title}`) |
| Trailing period stripped | (some libraries omit it) |

Both the docx placeholder and the RIS file (TI field) use the **identical normalized title**.

## Troubleshooting

**"Update Citations" cannot find many references**: Caused by title mismatch between docx and RIS. Re-run with `--force-refresh` to regenerate with normalized titles. Verify all records imported into EndNote.

**EndNote crashes during Update**: Split the work — select half the document, update, then the other half.

## Requirements

- **Python 3.7+** with standard library only (no pip installs needed)
- **Pandoc** for `.md → .docx` conversion
- **Internet access** for NCBI PubMed API calls
- **EndNote** installed, with `.ris` file association configured

## Input Validation

This skill accepts requests that match the documented purpose of `format-references-endnote` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `format-references-endnote` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
