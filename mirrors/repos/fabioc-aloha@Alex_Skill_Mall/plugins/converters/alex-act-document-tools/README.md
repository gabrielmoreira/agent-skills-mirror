# Alex ACT Document Tools

Optional document conversion plugin for the Alex ACT constellation. It converts
among Markdown, Word, HTML, RFC 5322 email, and plain text through six tested
skills, one `/convert` workflow, and a shared Pandoc-based runtime.

## Status

**Released as `v0.1.0`.** Source:
[`fabioc-aloha/Alex_ACT_Document_Tools`](https://github.com/fabioc-aloha/Alex_ACT_Document_Tools).
Install from the Alex ACT Mall as `alex-act-document-tools@alex-mall`.

## Install

```powershell
copilot plugin marketplace add fabioc-aloha/Alex_Skill_Mall
copilot plugin install alex-act-document-tools@alex-mall
```

Reload the host, then invoke `/alex-act-document-tools convert`.

## Why This Plugin Exists

The published Core payload reached the observed Copilot CLI Windows ceiling of
100 files. Document conversion is useful but optional executable capability,
not baseline reasoning or lifecycle maintenance. Extracting it preserves the
tested converters while returning 17 payload slots to Core after the eventual
coordinated migration.

| Component | Responsibility |
| --- | --- |
| Core | Runtime identity, ACT reasoning, safety, and frequent baseline skills |
| Manager | Install, update, repair, and remove plugins |
| Document Tools | Convert documents and validate generated artifacts |
| Illustrator | Author or verify visual assets embedded in documents |
| Mall | Publish the approved plugin payload after release |

## What Ships

| Skill | Conversion |
| --- | --- |
| `docx-to-md` | Word to clean Markdown with extracted images |
| `html-to-md` | HTML to clean Markdown |
| `md-to-eml` | Markdown to RFC 5322 email with inline CSS and CID images |
| `md-to-html` | Markdown to standalone HTML with diagrams and embedded assets |
| `md-to-txt` | Markdown to plain text |
| `md-to-word` | Markdown to professional Word with diagrams and formatting |

The `/convert` prompt routes requests to the matching skill. Four modules under
`.github/scripts/shared/` provide process execution, Markdown preprocessing,
Mermaid handling, and data-URI support.

Mall packaging must include that directory explicitly as `scripts/shared`.
Without the mapping, structural packaging passes while every converter loses
its runtime dependency. The source manifest records the required include.

## Runtime Prerequisites

| Tool | Requirement | Used by |
| --- | --- | --- |
| Node.js 24+ | Required | All converter scripts |
| Pandoc 2.19+ | Required | All six converters |
| Mermaid CLI | Optional | PNG diagrams in HTML and Word |
| JSZip | Optional | Word OOXML post-processing |
| svgexport | Optional | SVG rasterization |

Missing optional tools reduce output capability and must produce explicit
diagnostics. The plugin does not silently install external dependencies.

## Development

Run the source contract and startup tests:

```powershell
npm test
```

The test suite verifies component inventory, the 100-file ceiling, phantom
component prevention, and that all six scripts reach usage without a missing
module or pre-parser crash. Steward's integration suite also packages a
temporary 22-file Mall payload and executes all six converters from that
packaged location.

## Provenance

The converter scripts and shared runtime were ported byte-for-byte from
`Alex_ACT_Core` commit `47ef71ccab23b5e43a0170cb0449708c5f91629b` on
2026-08-03. Skill bodies were then adapted only to replace broken
Core-relative links with explicit optional composition guidance. The source
inventory is recorded in `manifest.json`.

Existing individual Mall converter entries are not the source for this plugin.
Four overlap by name but have drifted from current Core, and two formats have no
same-named Mall entry. Reconciliation and deprecation require a later Mall
publication proposal.

## Governance

`Alex_ACT_Steward` owns architecture, approval, release coordination, and
cross-repository coherence. Changes to converter behavior require evidence,
tests, and an approved Steward proposal. Core converter removal remains a
separate compatibility release.

## Would Revise If

Revisit by **2026-11-03** or sooner if fewer than two real conversions use the
plugin, the shared runtime proves inseparable from Core, the bundle duplicates
maintained Mall converters without a retirement path, or runtime dependencies
make installation materially less reliable than the current Core delivery.
