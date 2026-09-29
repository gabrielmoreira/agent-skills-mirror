---
name: sharepoint-analyze-custom-forms
plugin: sharepoint-discovery
description: Analyses an exported classic SharePoint custom list-form inventory -- classifying each form as out-of-box, script-based, or InfoPath/custom-layout -- and attaches a caller-supplied modernization strategy per classification. Read-only; consumes an export you provide and never contacts a tenant.
allowed-tools: Bash, Read
examples:
  - "python -c \"from forms_analysis import run; print(run(forms_path='forms.json', rules_path='rules.json', output_dir='out/').status)\""
---

# Analyze Custom Forms

## Trigger and Purpose

Use this skill when planning a classic-to-modern SharePoint migration and you
need to know which list forms are safe to carry forward as-is and which need
a replacement. It consumes a form inventory already exported from a tenant
and classifies each customized form.

It answers: is a form out-of-box, does it carry inline script, or is it an
InfoPath/custom-layout form with no script -- and what is the recommended
modernization strategy for each case.

## Rules are data, not code

`load_rules(path)` reads a caller-supplied JSON rules file
(`assets/form-classification-rules.json` ships a neutral default). The
modernization strategy text per classification is **entirely** supplied by
you -- **no site-specific migration judgement is built in.** The source
implementation this was extracted from hardcoded one organisation's strategy
text directly; that is removed.

## Honest outcomes

Every run returns a `DiscoveryOutcome` carrying a `DiscoveryStatus`:
`OBSERVED`, `EMPTY`, `PARTIAL`, `UNAVAILABLE`, `FORBIDDEN`, or `FAILED`.

A missing forms export or rules file is `UNAVAILABLE` and **no output
directory is created**. An empty forms export is `EMPTY`, never a pass. An
input that isn't a JSON array is `FAILED`.

## Read-only guarantee

No writes to any tenant, no network access. It reads the export path you name
and writes analysis artifacts to the output directory you name.

## Usage

```bash
python -c "
from forms_analysis import run
outcome = run(forms_path='forms.json', rules_path='rules.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Collecting a fresh export

`collect-sharepoint-custom-forms.ps1` connects to a live on-prem SharePoint
2016 site (REST + NTLM/Kerberos, no PnP/CSOM -- see
`.agent/rules/sharepoint-ps1-authentication-convention.md`), checks every
list/library's `Forms` folder for non-standard `.aspx` files, downloads
them, and does a best-effort classification (inline `<script>` present ->
`hasScript`; InfoPath/XSN markers -> `formType: InfoPath`) -- writing
`forms.json` in the exact `[{listName, isCustomized, hasScript, formType}]`
shape `forms_analysis.py` consumes. This classification is a heuristic
starting point, not a substitute for the rules-driven analysis this skill
performs. Read-only: calls only REST GETs, makes zero writes to the tenant.

```bash
pwsh -File scripts/collect-sharepoint-custom-forms.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir ./forms-export -UseDefaultCredentials
```

## Scripts

- `scripts/collect-sharepoint-custom-forms.ps1` -- real, read-only on-prem REST collector
- `scripts/forms_analysis.py` -- `run`, `analyse`, `generate_report`, `load_rules`
- `scripts/discovery_inputs.py` -- `DiscoveryStatus`, `DiscoveryOutcome`, `load_json_input`, `require_output_dir`

## Provenance

Adapted from `sp-discovering-forms` in the originating SharePoint migration
repository. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

