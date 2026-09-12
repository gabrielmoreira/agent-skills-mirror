---
name: project-proposal
description: "Turn an explicit project brief into a coherent local proposal package with a README, specification, milestones, risks, and local submission copy. Use when asked to draft, refine, scaffold, or validate an offline project, hackathon, or event proposal without claiming that a prototype, repository, portal entry, or submission exists."
---

# Project Proposal

Create and refine a local documentation package from facts the user explicitly
provides. This workflow authors documents; it does not build the proposed
project or interact with a submission system.

## Boundaries

- Work only from an explicit brief. Use fictional briefs in examples and tests;
  for a real proposal, preserve the user's supplied facts and mark unsupported
  capabilities as proposed or unverified rather than inventing evidence.
- Do not claim a prototype, repository, deployment, event registration, portal
  record, invitation, or submission exists.
- Do not open portals, provision cloud resources, invite people, implement the
  app, or submit anything.
- Do not require image generation. Suggest an optional visual brief when useful,
  but do not create a placeholder image or link to nonexistent artwork.
- Do not impose a Git workflow, model choice, hosted service, or custom shell
  helper.
- Structural readiness means the package is internally complete and linked. It
  does **not** prove technical feasibility, implementation, eligibility, or
  acceptance.

## Classify every assertion

Keep these categories visibly separate:

| Category | Meaning |
| --- | --- |
| Verified capabilities | Facts established by the brief or supplied evidence |
| Proposals | Intended behavior or design that has not been implemented |
| Assumptions | Conditions used for planning but not yet verified |
| Open questions | Decisions or facts still needed |
| Completed work | Work for which the user supplied completion evidence |

Never move an item into **Verified capabilities** or **Completed work** merely
because it appears in a plan, milestone, or polished submission paragraph.
Prefer “would,” “proposes,” and “planned” for unimplemented behavior.

## Choose a layout

Use **Compact** when one proposal document remains easy to scan:

```text
README.md
PROPOSAL.md
SUBMISSION.md
.project-proposal.json
```

Use **Split** when the specification, delivery plan, or risk analysis needs
independent review:

```text
README.md
SPEC.md
DELIVERY.md
RISKS.md
SUBMISSION.md
.project-proposal.json
```

Do not create empty pitch decks, architecture documents, research logs, or
other speculative files. Promote a section into a new file only when it has
substantive content and a distinct reader.

## Brief format

The bundled scaffold accepts JSON. Start from
`examples/example-brief.json`, replacing its fictional values with the user's
explicit brief. Required fields are:

- `projectId`, `title`, `summary`, `problem`
- `audience`, `verifiedCapabilities`, `proposals`, `assumptions`,
  `openQuestions`, and `completedWork`
- `decisions` containing `decision` and `rationale`
- `milestones` containing `name` and `outcome`
- `risks` containing `risk` and `mitigation`
- `submission.body`
- `submission.shortFields`, where each item has `name`, `value`, `maxUnits`,
  and `counting`

`counting` is one of:

- `Utf16CodeUnits`: .NET/JavaScript-style UTF-16 code units
- `Characters`: Unicode scalar values (code points)
- `Graphemes`: user-perceived text elements

Limits are brief-specific configuration, not universal portal rules. If the
target system has not supplied a limit and convention, record an open question
instead of inventing either.

## Safe scaffold

The bundled scripts require PowerShell 7. They use ordinary PowerShell/.NET
APIs, not a custom profile or helper module. Run them in a fresh non-profile
shell when validating a disposable example.

Resolve bundled files from the directory containing this installed `SKILL.md`,
never from the current working directory:

```powershell
$skillRoot = '<directory-containing-this-SKILL.md>'
$newProposal = Join-Path $skillRoot 'scripts\New-ProjectProposal.ps1'

& $newProposal `
    -BriefPath 'C:\work\fictional-brief.json' `
    -Destination 'C:\work\proposal-package' `
    -Layout Compact `
    -WhatIf

& $newProposal `
    -BriefPath 'C:\work\fictional-brief.json' `
    -Destination 'C:\work\proposal-package' `
    -Layout Compact
```

Always preview first. Use a new, explicit destination. The scaffold:

- writes nothing under `-WhatIf`;
- refuses an existing directory that lacks its identity file;
- refuses a different `projectId` or layout at an existing destination;
- never overwrites an existing file;
- preserves authored refinements on same-identity reruns and creates only
  missing package files.

The identity stores fingerprints of the brief, schema, and selected templates.
A changed input causes an explicit stale-source conflict while retaining the
existing documents. Reconcile the package and source deliberately or create a
new destination; changing an identity file alone does not reconcile its prose.

First creation stages and validates complete documents before publishing the
new directory without replacement. Missing-file repair publishes complete
temporary files without replacing existing files, then validates the package;
an existing malformed authored file requires explicit repair, not overwrite.
These local publication rules are not a guarantee of power-loss durability.

The scaffold is a starting point, not the final author. Read every generated
document and improve the prose, scope, acceptance evidence, sequencing, and
cross-document consistency.

## Authoring pass

1. Restate the user problem, audience, and outcome without adding facts.
2. Put present-tense claims only in verified or completed categories.
3. Turn features into a specification with observable behavior and explicit
   non-goals.
4. Define milestones by reviewable outcomes, not dates invented by the agent.
5. Pair each material risk with a concrete mitigation or validation step.
6. Write local submission copy that is concise but does not erase uncertainty.
7. Link the README to every package document and nowhere outside the package
   unless the brief explicitly cites an external reference.

## Decision-driven refinement

When an open question becomes a decision:

1. Add or update the decision and rationale.
2. Remove the resolved question.
3. Update affected scope, requirements, milestones, risks, and submission copy.
4. Search all package documents for the superseded term or claim.
5. Re-run offline validation.

A decision is not completed implementation. Keep the classification unchanged
unless separate evidence supports moving it.

## Offline validation

Run the bundled validator against the authored package:

```powershell
$testProposal = Join-Path $skillRoot 'scripts\Test-ProjectProposal.ps1'
$result = & $testProposal -Path 'C:\work\proposal-package'
$result
```

Validation checks:

- expected documents for the selected layout;
- substantive content and required classification/plan sections;
- unresolved placeholder markers;
- configured short-field counts and limits;
- local Markdown links, including containment within the package;
- external URL links by classification only, without fetching them.

The local link validator supports simple inline and reference links and basic
ATX heading fragments, not the full Markdown language. Unsupported link syntax
is an error rather than evidence of a valid link. Paths must remain inside the
package and may not traverse reparse points; do not treat this local tool as a
security boundary against concurrent hostile filesystem changes.

Treat a successful result only as **structurally ready**. Report feasibility,
implementation, submission, and acceptance as unverified unless the user
supplies separate evidence.

## Output

Report:

- destination and chosen layout;
- documents authored;
- configured field limits, counting conventions, and measured counts;
- remaining assumptions and open questions;
- validation result and external links not fetched;
- the explicit statement that no prototype, repository, portal entry, or
  submission was created.

If the brief lacks enough information to make the proposal coherent, do not
silently fill gaps. Keep them as assumptions or open questions in the package.
