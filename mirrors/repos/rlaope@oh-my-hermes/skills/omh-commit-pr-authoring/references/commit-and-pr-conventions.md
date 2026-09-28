# Commit and PR Conventions

Load this while drafting a commit message or a pull-request body. OMH writes the text only: the commit, the push, and opening the PR are the user's or the executor's, and nothing here runs a command.

## 1. Read the convention before writing

| Source | What to take from it | When it is missing |
| --- | --- | --- |
| PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/`, `docs/`) | the section headings, in order, and any checkbox list | say no template was found and use a plain summary, why, and validation |
| Recent log (`git log -10 --format=%B`) | subject shape (imperative, `type(scope):`, ticket prefix), body width, trailer set | say the log is empty or unreadable, and do not import a convention |
| Contributor docs (`CONTRIBUTING.md`, `AGENTS.md`) | sign-off rule, required trailers, forbidden lines | record the rule as not found |

Record what was read and what was not in `repo_convention_read/v1`. A convention the repository does not use is not a default to fall back on.

## 2. The evidence ledger

Every command the change mentions gets one row before any text is written.

| Field | Content |
| --- | --- |
| Command | as run, with arguments |
| State | `observed` or `not_observed` |
| Result | exit status and the line that shows it, for `observed` only |
| Where seen | terminal output, CI job, or wrapper record |
| Reason | for `not_observed`: skipped, prepared only, blocked, or out of scope |

A row is `observed` only when a run record exists. "It should pass", "CI will run it", "I ran it earlier on another branch", and "the same tests passed yesterday" are all `not_observed`. Wording never promotes a row.

## 3. Projecting the ledger into the text

- `Tested:` (or the template's validation checklist) lists exactly the `observed` rows, each with what it showed.
- `Not-tested:` lists every `not_observed` row with its reason. An empty `Not-tested:` is a claim that nothing was skipped; write it only when that is true.
- A checkbox in a PR template is checked only for an `observed` row.
- CI state, review state, and merge state are stated only when observed; otherwise say which of them has not happened yet.

## 4. Subject and body

- Subject: the repository's shape, the change's effect, within the length the log uses.
- Body: why the change exists and what is now true, not a restated diff. Measured before/after values belong here when the change is about a measurement.
- `Closes #N` goes on its own line, and only when every success criterion of that issue is met; otherwise `Refs #N`.

## 5. Trailers and sign-off

| Trailer family | Example | Rule |
| --- | --- | --- |
| DCO | `Signed-off-by: Name <email>` | add only when the repository requires it, with the configured author |
| Decision trailers | `Constraint:`, `Rejected:`, `Confidence:`, `Scope-risk:`, `Directive:` | use when the log shows them; each `Rejected:` names the alternative and why |
| Evidence trailers | `Tested:`, `Not-tested:` | projected from the ledger, never written freehand |

Never add attribution lines the repository forbids, and never put credentials, tokens, private URLs, or raw transcripts in either text.
