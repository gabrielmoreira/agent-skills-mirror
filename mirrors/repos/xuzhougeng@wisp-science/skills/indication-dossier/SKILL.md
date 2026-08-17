---
name: indication-dossier
description: Build a sourced research dossier for one therapeutic indication — patient population, epidemiology, disease biology, standard of care, regulatory path, and landmark trials. Use when the user asks for an indication overview, disease landscape, or trial-design background.
license: Apache-2.0
---

# Indication dossier

Five research phases, each writing one waypoint JSON under
`<workdir>/waypoints/`, ending in a cited Markdown report. Waypoints make the
run resumable: a later invocation reads which files exist and continues from
the first missing one. The only pause for user input is after Phase 1.

## The framing rule

Treat the indication as a *patient population*, not a disease entry. Every
section answers a population question — who are these patients, how are they
identified and managed, which trials would help them — rather than a textbook
question about the condition. Nesting is population nesting: everyone in the
child indication is in the parent.

Some inputs are not billable diagnoses at all: a biological state
("immunosenescence"), a non-accepted indication ("ageing"), an iatrogenic
population ("GLP-1 induced sarcopenia"). Detect and label this early — it
changes the epidemiology evidence base, the regulatory path, and what a
"complete" dossier even looks like.

## Inputs

| Input | Required | Meaning |
|---|---|---|
| `indication` | yes | e.g. "sarcopenia", "idiopathic pulmonary fibrosis" |
| `additional_context` | no | focus areas, parent indication, framing |
| `workdir` | no | waypoint/report location; default `./do_not_commit/indication-dossier-<slug>/` |

## Tooling

Preferred: `clinical-trials` MCP for CT.gov, `pubmed` MCP for literature,
`WebSearch`/`WebFetch` for FDA guidance, specialty-society guidelines
(NCCN, AASLD, …), and CDC/WHO data; `WebFetch` for remote PDFs, `Read` for
local ones; `Agent` subagents for parallel evidence gathering. When a listed
MCP is not connected, say so and fall back to `WebSearch` against the public
site itself.

## Run protocol

Read `references/standards.md` first — it defines what counts as a citable
finding, the anti-fabrication rules, and the report style. Phase-by-phase
instructions live in `references/phases.md`; waypoint formats in
`references/waypoints.md`.

1. **Identity.** Resolve definition, ICD codes, aliases, parent, diagnostic
   status; quick CT.gov landscape count. Write `meta.json`. Then show the
   resolved identity and end the turn asking **Proceed / Revise identity /
   Stop** — the expensive phases wait for the answer (Wisp has no separate
   interactive-question tool, so this is a normal turn end).
2. **Epidemiology.** Case definition, prevalence/incidence, demographics,
   natural history → `epidemiology.json`.
3. **Biology & standard of care.** Mechanism, biomarkers, approved
   therapies, guidelines, unmet need → `biology_soc.json`.
4. **Regulatory & trials.** Accepted endpoints, precedents, design
   parameters, landmark trials, failures → `regulatory_trials.json`.
5. **Synthesis.** No new research threads (single targeted gap-fills only).
   Write `indication_dossier_report.md` and `research_output.json`, then
   mark `progress.json` complete.

After each of phases 2–5, write the waypoint, emit a ≤200-word summary of
findings and open uncertainties, and continue directly.

## Resuming

When `workdir` already contains waypoints: list which phases are complete
(file exists and is non-empty), show the meta summary, and ask which phase to
run. Never overwrite an existing waypoint without confirmation.

## Output layout

```
<workdir>/waypoints/
├── progress.json                 # loop control, flipped last
├── meta.json                     # phase 1
├── epidemiology.json             # phase 2
├── biology_soc.json              # phase 3
├── regulatory_trials.json        # phase 4
├── sources_evaluated.json        # appended by every phase
├── research_output.json          # phase 5, structured
└── indication_dossier_report.md  # phase 5, the deliverable
```
