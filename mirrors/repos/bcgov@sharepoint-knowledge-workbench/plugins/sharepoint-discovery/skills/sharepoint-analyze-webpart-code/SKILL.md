---
name: sharepoint-analyze-webpart-code
plugin: sharepoint-discovery
description: Groups classic SharePoint web parts by functional behaviour -- inline script, external helper scripts, text-only, empty, or unretrievable -- so near-duplicate instances collapse into a reviewable set. Classification knowledge is caller-supplied via a KnowledgeBase; read-only.
allowed-tools: Bash, Read
examples:
  - "python -c \"from webpart_code_analysis import run; print(run(extract_path='webparts.json', output_dir='out/').status)\""
---

# Analyze Web Part Code

## Trigger and Purpose

Classic SharePoint sites accumulate hundreds of web-part instances that are
mostly copies of a handful of real behaviours. Use this skill to collapse an
exported web-part content dump into distinct functional groups, so a
modernization review covers each *behaviour* once instead of each instance.

Produces three artifacts: a groups JSON, a Markdown analysis report, and a
per-instance review CSV.

## Categories

| Category | Meaning |
|---|---|
| `InlineLogic` | Contains inline script implementing real behaviour |
| `ExternalHelpersOnly` | References external helper scripts, no inline logic |
| `TextOnly` | Static content, no code |
| `Empty` | No meaningful content |
| `ScriptEditorMissing` | **Content could not be retrieved** -- not a classification, a gap |

`ScriptEditorMissing` is deliberately distinct. An unretrievable web part is an
unknown, not an empty one, and a run containing any of them reports `PARTIAL`
with the count -- never `OBSERVED`.

## Classification knowledge is caller-supplied

`KnowledgeBase` and `InlineLogicRule` let you supply the helper-script table
and behavioural heuristics. The source implementation hardcoded roughly thirty
helper-script names and named business-rule heuristics specific to one
organisation; **all of that site-specific knowledge is removed here.**
`DEFAULT_KNOWLEDGE_BASE` is deliberately generic.

## Read-only guarantee

No tenant contact, no writes outside the output directory you name. A missing
input is `UNAVAILABLE` and creates no output directory.

## Usage

```bash
python -c "
from webpart_code_analysis import run
outcome = run(extract_path='webpart-content.json', output_dir='out/')
print(outcome.status, outcome.detail)
"
```

## Collecting a fresh export

`collect-sharepoint-webpart-content.ps1` connects to a live on-prem
SharePoint 2016 site (REST + NTLM/Kerberos, no PnP/CSOM -- see
`.agent/rules/sharepoint-ps1-authentication-convention.md`) in two modes:
`-Mode Scan` (default) enumerates pages and queries
`GetLimitedWebPartManager` for every web part on every page, writing
`webpart-scan.csv`/`.json`; `-Mode ExtractContent` reads that CSV and pulls
each web part's full HTML/JS payload via the legacy `_vti_bin/exportwp.aspx`
handler (the only mechanism that exposes it on SP2016 -- the modern REST
`ExportWebPart` action 404s unconditionally), writing `webpart-content.json`
in the exact `[{PageUrl, WebPartId, WebPartTitle, Content}]` shape
`webpart_code_analysis.py` consumes. Read-only: calls only REST GETs, makes
zero writes to the tenant.

```bash
pwsh -File scripts/collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode Scan -UseDefaultCredentials
pwsh -File scripts/collect-sharepoint-webpart-content.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -Mode ExtractContent -UseDefaultCredentials
```

## Scripts

- `scripts/collect-sharepoint-webpart-content.ps1` -- real, read-only on-prem REST collector (Scan + ExtractContent modes)
- `scripts/webpart_code_analysis.py` -- `run`, `analyse`, `classify`, `recommend`, `generate_report`, `generate_instance_csv`, `KnowledgeBase`, `InlineLogicRule`
- `scripts/discovery_inputs.py` -- shared status vocabulary and input loading

## Stage 2 — AI-reasoning pass over this skill's output

This skill's Stage 1 grouping is deterministic, but each group's JSON also
carries `businessIntent`/`enforcementLevel`/`spfxAssessment` fields --
generic and structurally honest for Empty/TextOnly categories, caller-
supplied via `InlineLogicRule.business_intent`/`spfx_assessment` for
recognised inline logic, and an explicit "requires manual review" for
everything unrecognised. **These are a deterministic starting point, not a
substitute for real judgment** -- the full disposition (business behaviour,
MVP decision, SPFx candidacy with justification, pattern-collapse across
groups sharing one mechanism, evidence gaps) is Stage 2, agent-assisted by
design: route to `sharepoint-webpart-modernization-analysis-agent` (in
`sharepoint-page-modernization`) once this skill's grouped output exists --
that agent's per-group analysis structure and category-level defaults are
richer than anything this Python module attempts to compute on its own.

## Provenance

Adapted from `sp-discovering-web-parts` in the originating SharePoint migration
repository. Note that 6 of that skill's 19 symlinks pointed at project analysis
*data* outside the plugin boundary; that data was **not** extracted, but the
Stage-2 reasoning *framework* those analysis documents applied (per-group
disposition fields, category-level defaults, and the pattern-collapse
discipline) was later generalized into
`sharepoint-webpart-modernization-analysis-agent` after a Phase 9 audit
follow-up confirmed it was a distinct, valuable, reusable pattern separate
from the project-specific data it had originally been applied to. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

