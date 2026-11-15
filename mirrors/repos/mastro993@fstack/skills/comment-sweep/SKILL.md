---
name: comment-sweep
description: Use when the user wants the comments in their branch, diff, or whole repository cleaned up or audited, such as "clean up the comments I added before review", "strip the AI slop", "remove the commented-out code", "sweep every comment in the repo", or "do these comments earn their place?".
compatibility: Needs git and python3. Big sweeps go faster with subagents.
---

# Comment sweep

Every comment costs the reader time and goes stale the moment the code moves on; generated code adds them by the dozen. You sweep comments: delete each one that doesn't earn its place, change nothing but comments, and prove it. Code that leans on a comment to make sense is a **reshape target**: you report it, and the user decides whether to fix the code.

Three kinds of work, three workers. Bookkeeping is `scripts/sweep.py`, in this skill's directory: what is in scope, the routine deletions, the proof. Finding the comments is reading, and no script reads every syntax, so the **inventory** is taken by you on a small sweep and by cheap **scouts** on a big one. Judging each comment is yours alone.

## 1. Scope

```bash
python3 <skill-dir>/scripts/sweep.py scope [--full] [--base REF] [PATH ...]
```

- **Branch scope**, the default: every comment on a line the branch adds or changes since its merge-base with origin's default branch, staged, unstaged, and untracked work included. Pass `--base` when the branch merges somewhere else.
- **Full scope**, `--full`: every comment in the repo, when the user asks for it: "the whole repo", "every comment", "not just my changes".

Paths narrow either scope to what the user names.

`scope` prints a work directory, a `skip:` line for each generated, vendored, minified, lock, binary, or migration file (the sweep leaves those alone), the batches, and `small` or `big`. The work directory holds a snapshot of the files for step 5 and, per batch, a `batch-<n>.files` list and in branch scope a `batch-<n>.diff`, whose `+` lines are the lines in scope.

In branch scope, comments the branch didn't touch stay exactly as they are, even in files it did touch: sweeping them bloats the diff, buries the blame, and puts unrelated risk in the PR. When the user names a file or directory without asking for a full sweep, sweep what the branch changed there, and tell them the older comments are out of scope unless they want a full sweep of it.

Done when `scope` has run on the final scope.

## 2. Inventory

The inventory is one line per comment in scope, `path:line: kind: text`, taken by following `references/inventory.md`. `kind` is `comment`, `doc` (a docstring or doc comment on a declaration), or `directive`: a **load-bearing** comment, one a tool reads.

- **Small**: take it yourself, from `batch-1.diff` in branch scope and from the files `batch-1.files` lists in full scope. Under a few thousand lines a scout costs more than it saves, because judging has you read around every comment anyway.
- **Big**: send one scout per batch, all in one message so they run in parallel. A scout's whole prompt is the brief with its batch filled in, and it runs on the cheap model `references/models.md` names for your harness. Without subagents, take the batches yourself, one at a time.

Then, while any scouts run, read the repo's own rules on comments: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, and lint config that requires docs (`jsdoc/require-jsdoc`, `#![deny(missing_docs)]`, revive or golint `exported`, ruff or pydocstyle `D` rules, checkstyle `Javadoc*`, detekt `UndocumentedPublic*`).

Scouts mislabel comments and miss some. The labels are yours to correct as you judge: a comment you'd call a directive is one, whatever the scout said. The misses are caught by step 4's `unlisted` net.

Done when the inventory covers every file of every batch, and you have noted each repo rule that requires a comment, or found none.

## 3. Judge every comment

Judge from the inventory. For each comment, read the range that settles it (`sed -n '<from>,<to>p'`): the lines around it, the declaration it documents, and for a guard its callers and history. Narration or dead code is often settled by its inventory line and a glance at the next few lines. A whole file earns a read only when a guard's truth depends on all of it. On a big sweep these ranges are the saving the scouts bought, however small each file looks.

A comment earns its place only when it tells the reader something **true** that they can't get from the code, its names and types, its tests, or `git log`, and that the code can't be made to say. Ask in order and stop at the first answer:

1. **Load-bearing?** A **directive** stays, and so does a **required doc**, a comment a repo rule requires, trimmed to its contract. The one exception is an **unused directive**: a suppression its own tool proves unused (step 5).
2. **True?** Read the code it describes. A false or stale comment goes, or loses its false part, and the report lists it as a **mismatch**, because the code may be the bug.
3. **Already said?** If the code, a name, a type, or a test says it, the comment goes.
4. **Could the code say it?** A rename, an extracted function or constant, a type, an assertion, or a test. Then it's a **reshape** target, and the comment stays until that code change lands: deleting it first loses the knowledge while the surprise stays.
5. Otherwise it stays, cut down to the part that earns its place.

**Noise** goes without a second look:

- **narration** of what the next lines do; a docblock with the signature **restated** (`@param id the id`, `Returns the user.`);
- **history** and conversation: "fixed the bug", "now uses X", "added for the refactor", "as requested", author and date stamps. Git keeps history;
- **dead code**: commented-out code. Git keeps that too;
- a **banner** or divider. A file that needs them wants splitting, so a long one becomes a reshape target;
- a **done todo**, whose work is already in the code, and an empty doc **stub**.

What usually stays:

- **licence**, copyright, and attribution for copied code;
- a **contract**: a doc comment on the public API that states inputs, errors, invariants, units, thread-safety;
- a **header** that says what the module or file is for, beyond what its name already says;
- a **runtime doc**, a docstring a tool reads at runtime: click, typer, and argparse print them as help, FastAPI publishes them in OpenAPI, Sphinx renders them. Search for those uses before touching a docstring;
- the **why** of a **foreign** constraint that forces this shape (a vendor bug, a platform quirk, a protocol or spec rule), best with a link;
- **evidence** the code can't carry: a benchmark, an incident, an issue, RFC, or ADR link;
- a **tracked todo**: a TODO or FIXME that links an open issue.

A **guard** warns against a real mistake: a warning (`IMPORTANT`, `do not remove`, `order matters`, `keep in sync with`), a workaround, or an untracked TODO, FIXME, or HACK. Deleting a true one costs an incident later, so investigate each: read its callers, then its history (`git log -L <start>,<end>:<file>`, the PR behind the commit, the issue it links). Every verdict on a guard names the evidence that settled it: a caller, a commit, a PR, or a version.

- A warning that is still true and that no test, type, or lint enforces is a reshape target: name the cheapest encoding (a test, an assertion, a type, a lint rule) and keep the comment until it exists. An **obsolete guard**, proven so, goes.
- A workaround for an upstream bug: compare the pinned version with the version that fixed it. Fixed upstream makes the workaround code itself a reshape target.
- An **untracked todo** that names a real open defect stays, and the report lists it so the user can file it.

When you can't settle a comment, let the cost of being wrong decide. Noise is cheap to restore from git, so it goes. A guard or a why you couldn't verify stays, as **unverified** with what you checked.

Write the inventory to `inventory.txt` in the work directory, each line ending in its verdict, `=> delete: <reason>`, `=> trim: <reason>`, or `=> keep: <reason>`:

```
src/orders.ts:12-15: doc: Gets the order. @param id the id => trim: restated
src/orders.ts:31: comment: loop over items => delete: narration
src/orders.ts:40: comment: Stripe wants minor units: https://docs.stripe.com/currencies => keep: why
```

Start the reason with the bold word above that names its case, then a comma and any detail: `check` counts the report by the words before the first comma. Line numbers and text stay as the inventory took them, from before any edit: the script works from those, and `sweep.py --help` has the rest of its contract.

Done when every line of `inventory.txt` ends in a verdict.

## 4. Edit

```bash
python3 <skill-dir>/scripts/sweep.py apply
```

`apply` first checks the inventory, and stops on a line it can't use: `UNJUDGED` and `UNPARSED` want a verdict or the format above, and `OUTSIDE` marks a comment on no line in scope, which the sweep leaves alone, so drop that line. Then it deletes each `delete` comment it can match word for word to its inventory line, and prints two lists.

`unlisted` is the net under the inventory, and the cross-check on the scouts: each line in scope that holds a comment marker and that no inventory line covers. Markers turn up in strings too, so read each one. For a comment the inventory missed, add its line to `inventory.txt` with a verdict and run `apply` again: it skips what is already edited. A batch with many misses was read badly: take its inventory again yourself.

`by hand` is the rest of the edits: every trim, and the deletes `apply` won't guess at, such as a docstring, a comment in the middle of a line, a nested block, a notebook cell, or an inventory line whose number or words are off. Make those edits yourself, comments only:

- Delete a comment whole: its markers, its line when nothing else is on it, and the blank line its removal doubles.
- Trim a kept comment by cutting: what remains is the part that earned its place, in its original words.
- Fix spacing by hand on the lines the sweep touched. A formatter run over whole files reflows lines the branch never changed.

Done when `apply` has run, every `unlisted` line is settled, and every `by hand` line is edited.

## 5. Verify

```bash
python3 <skill-dir>/scripts/sweep.py check
```

`check` compares the working tree with the snapshot and the inventory, and prints a line per finding:

- `CODE`: a changed line that no delete or trim verdict covers. Revert it when it is code, or a comment outside the inventory. When it is the comment itself and the inventory had its line wrong, correct `inventory.txt` and run `check` again.
- `DIRECTIVE`: a changed directive. Revert it, unless you removed a suppression on purpose. Then prove it unused with the tool that reads it: `eslint --report-unused-disable-directives`, `tsc` (an unused `@ts-expect-error` fails it), `ruff check --select RUF100`, mypy's `--warn-unused-ignores`, or the linter's equivalent, and give it the verdict `delete: unused directive`. If the tool still needs it, or can't run here, revert.
- `CUT`: an edit `check` couldn't match to the inventory's words, with what went. Read each one: only comment text may be gone.
- `UNAPPLIED`: finish that edit. `UNJUDGED`, `UNPARSED`, `OUTSIDE`: as in step 4, and revert any edit made to an `OUTSIDE` comment.
- `STRAY`: a file outside the scope changed. Remove what your own checks left behind (`__pycache__`, build output) and revert anything else.

`check` has read the whole diff, so its findings are all of it you need to read: it proves the sweep touched nothing but inventoried comments. A comment edit can still trip three of the repo's own tools, so run those that apply, once, after the sweep:

- its linter, when a rule requires docs and you deleted or trimmed a `doc`;
- the tool that reads a directive you removed;
- its tests, when you changed a docstring or a doc comment with examples in it.

Run a tool the repo already has set up. One that would need a toolchain or the dependencies installed first is reported as not run, with the command for the user to run: a comment sweep doesn't earn the cost of installing it. A failure on a line the sweep left alone predates it: name it in the report and move on.

Done when `check` ends in `ok` with every `CUT` and `DIRECTIVE` it printed read and sound, and each tool that applies has passed or is reported as not run, with its command.

## 6. Report

`check` printed the counts, and then the inventory with each surviving comment at its line now and each deleted one at its old line, marked `(before)`. It computed those lines from the diff, so take every number and location in the report from that output as printed. Use this shape and drop empty sections:

```
Comment sweep: <branch> vs <base> (or: full, <paths>), <N> comments in <M> files

Deleted <D>: <count per reason: narration, restated, history, dead code, ...>
  each guard deleted: path:line (before) — the evidence it was obsolete
Kept <K>: <count per reason>
  each guard or why kept: path:line — reason
Trimmed <T>:
  path:line — what went, and why
Reshape targets:
  path:line `symbol` — the code change that makes the comment unnecessary
Mismatches:
  path:line — the comment said X, the code does Y
Untracked TODOs:
  path:line — what it says
Unverified:
  path:line — what you checked
Skipped: <files and why>
Verified: sweep.py check <result>; <lint, typecheck, and test commands and results>
```

Then offer the reshape targets. If the user picks some, make each one a separate change from the sweep, with the project's tests passing, and delete the comment it replaces in the same change.
