# Blind Trial Material Rules

Read this when work adds, changes, or removes anything under `trials/`. This file owns two things and nothing else: where this repository keeps trial material, and how that material is written down.

How a trial is *run* belongs to `degardis-authoring` — authorization, check selection, fixture sufficiency and probing, evaluator selection and blinding, host capability, baselines, attribution, repairs, and the evidence a check must produce. None of that is restated here, and nothing here substitutes for reading it.

## Layout

| Path | Holds |
| --- | --- |
| `trials/fixtures/<skill-name>/<fixture-name>/` | One fixture: the project, skill source, or request material a run is handed. A fixture directory is the only thing ever copied into a trial root. |
| `trials/fixtures/<skill-name>/README.md` | The collection index — what each fixture is, what it carries, and which situations it fits. |
| `trials/pending/<skill-name>/README.md` | That skill's queue of unsettled questions, with any material a question needs beside it. |

Both a collection and a queue are named for a skill in `skills/`, and both are optional: a skill with no fixtures has no collection, and a skill with nothing unsettled has no queue.

Never put trial material under `skills/`. The collection tools, the documentation checker, and the release workflow all treat that tree as publishable, so a fixture placed there ships to users.

## A fixture

- A tracked fixture is canonical and immutable. A run copies it and works in the copy; the tracked directory never absorbs what a run did to its copy. Where a question needs different conditions, add a fixture instead of editing one — every earlier observation was recorded against the fixture as it stood.
- A deliberate defect is the point of a fixture. Never repair one to tidy the collection or to make validation pass, and never repair one because a run reported it. A later run reporting a recorded defect is agreeing with the record, not finding a regression.
- A fixture holds only what a real performer would receive: conspicuous placeholders, and no real credentials, personal information, confidential records, or internal locators.
- Nothing tracked under `trials/fixtures/` is named `AGENTS.md` or `CLAUDE.md`. A session working in this repository reads such a file as instructions to itself, and a fixture's instructions are not its own. Where a check needs the evaluator's root to carry one, write it into the prepared root rather than into the fixture.
- A fixture's own files are content, not documentation about the fixture. A `README.md`, `CONTRIBUTING.md`, or `docs/` page inside a fixture belongs to the imaginary project and is written as that project would write it — including where it is deliberately wrong.

## The collection README

One page per collection, and the only place a fixture is described. It is user-facing: someone opens it to see what is here and which fixture fits a question.

- Describe each fixture: what it is, what it carries — planted defects, deliberate conditions, expected validation failures — and the situations it suits and does not suit. Where a standing prerequisite decides whether a fixture fits, such as a language version or a tool it needs, name it.
- Nothing that only happened once. No history section, no dated entries, no run log, no token or duration figures, no account of what an evaluator did, no expected result for a particular check, no patch. A run's own observations belong to that run's record, and what a run established about a skill belongs to the commit that changed the skill.
- Where a run shows this page wrong — a condition that never fires, a defect nobody planted, a fixture that turns out unfit for the question it was built for — correct the description. That is the only thing a run adds here.
- It states no rule. Rules for trial material live in this file, and a rule copied into a README is a second copy to keep current.
- Because it describes what every fixture hides, this page is the answer key for its collection. Copy only a fixture directory into a trial root, never the collection directory or any ancestor of it, and check what a prepared root actually contains rather than only where it came from.

## The pending queue

`trials/pending/<skill-name>/README.md` is one skill's list of questions a trial raised and could not settle. It is user-facing too, so a reader should see what is still open in one pass.

- One item per question, written as the question, with what would settle it — the fixture it needs, the material it needs, or the decision it waits on.
- Group items under `## Open`, `## Needs a decision`, or `## Blocked`, and no other heading. The heading carries the state, so an item never restates it.
- A settled question leaves the page. Delete the item as soon as the answer is known, rather than marking it closed and keeping it: a closed item reads as a standing verdict, and the next change to the skill can reopen the question while the page still says it is settled. What settled it belongs in the commit that settled it, and in the source that commit changed.
- Nothing about the queue itself — no summary, no counts, no history, no roll-up of what it contains.
- Material a question needs, such as an exact prompt, a staged requester exchange, or a sanitized input, sits beside the queue in the same directory and goes when the last question needing it goes.
- Create the directory when the first question arises and delete it when the last item goes. A skill with an empty queue has no directory and no page.

## Sanitizing what gets written here

Before a field report, requester exchange, or session observation becomes a fixture or a pending question, replace whatever is specific to the reporter's own environment with a placeholder or a description of its kind — their company, their repository or project, a real person's name, an internal host, a file path, a credential. Keep only what makes the observation actionable.

Never genericize this repository's own subject matter. The skill name and version under test, the host or harness, the evaluator class, and the workflow, rule, or fixture a question names are what a trial exists to establish, and none of them is identifying information.
