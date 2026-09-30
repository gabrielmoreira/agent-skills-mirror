---
name: import-responses
description: Imports Microsoft Forms Excel exports or offline HTML exports into responses.json. Uses deterministic import and merge scripts. Use for "importar Forms", "import Excel", "forms-responses.xlsx", "merge offline exports", "importar respuestas de Forms", "combinar exportaciones offline".
argument-hint: path to Microsoft Forms .xlsx export or offline exports folder
---

# Skill: Import assessment responses

Use deterministic importers. Do not parse spreadsheets or JSON exports manually.

## Microsoft Forms command

```bash
python3 scripts/import_forms_excel.py forms-responses.xlsx
```

or:

```bash
make import XLSX=forms-responses.xlsx
```

## Offline form merge command

```bash
python3 scripts/merge_offline_responses.py exports/
```

or:

```bash
make merge DIR=exports/
```

The offline merge assigns unique IDs `R01`, `R02`, and so on, refuses v1 files, refuses mixed organizations unless explicitly allowed, and backs up an existing `responses.json`.

## v2 detection

The importer detects v2 exports by question header IDs such as `D4-Q3:` and profile IDs `R-Q1` to `R-Q5`. `level: null` means `NA`. A missing answer key means not answered.

## v1 behavior

Exports with v1 headers continue through the archived v1 import format.

## After import

Run:

```bash
python3 scripts/assessment_engine.py all
python3 scripts/fill_workbook.py
python3 reports/scripts/build_payload_and_render.py
```

## Chat response

Report the detected framework, respondent count, output path, warnings, and next command. Stop if the importer reports unknown headers, invalid levels, v1 files in offline merge, or mixed organizations.
