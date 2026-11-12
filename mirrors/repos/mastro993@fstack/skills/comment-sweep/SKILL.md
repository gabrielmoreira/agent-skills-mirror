---
name: comment-sweep
description: Use when the user wants the comments in their branch or diff cleaned up or audited before review, such as "clean up the comments I added", "strip the AI slop", "remove the commented-out code", or "do these comments earn their place?".
compatibility: Needs python3 and git.
---

# Comment sweep

Every comment costs the reader time and goes stale the moment the code moves on; generated code adds them by the dozen. You sweep the comments in the current branch's changes: delete each one that doesn't earn its place, change nothing but comments, and prove it. Code that leans on a comment to make sense is a **reshape target**: you report it, and the user decides whether to fix the code.

`scripts/comments.py`, in this skill's directory, does the mechanical half: `list` in step 1 and `check` in step 4.

## 1. Scope

```bash
python3 <skill-dir>/scripts/comments.py list [--base REF] [PATH ...]
```

`list` prints, as `path:line: kind: text`, every comment on a line the branch adds or changes since its merge-base with origin's default branch, staged, unstaged, and untracked work included. It snapshots those files for step 4 and prints the files it skips (vendored, generated, migrations, no lexer) with the reason. Pass `--base` when the branch merges somewhere else, and paths to narrow it to part of the branch. `kind` is one of:

- `comment`: a plain comment.
- `doc`: a Python docstring.
- `directive`: a **load-bearing** comment, one a tool reads: lint and type suppressions, build tags, pragmas, doctests, licence and generated markers, JSDoc types in JavaScript.

That list is the whole scope. Comments the branch didn't touch stay exactly as they are, even in files it did touch: sweeping them bloats the diff, buries the blame, and puts unrelated risk in the PR. When the user names a file or directory, sweep what the branch changed there and tell them that older comments are out of the sweep's scope.

Then read the repo's own rules on comments: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, and lint config that requires docs (`jsdoc/require-jsdoc`, `#![deny(missing_docs)]`, revive or golint `exported`, ruff or pydocstyle `D` rules, checkstyle `Javadoc*`).

Done when `list` has run on the final scope and you have noted each repo rule that requires a comment, or found none.

## 2. Judge every comment

A comment earns its place only when it tells the reader something **true** that they can't get from the code, its names and types, its tests, or `git log`, and that the code can't be made to say. Ask in order and stop at the first answer:

1. **Load-bearing?** A `directive` stays, and so does a comment a repo rule requires, trimmed to its contract. The one exception is a suppression its own tool proves unused (step 4).
2. **True?** Read the code it describes. A false or stale comment goes, and the report lists it as a **mismatch**, because the code may be the bug.
3. **Already said?** If the code, a name, a type, or a test says it, the comment goes.
4. **Could the code say it?** A rename, an extracted function or constant, a type, an assertion, or a test. Then it's a reshape target, and the comment stays until that code change lands: deleting it first loses the knowledge while the surprise stays.
5. Otherwise it stays, cut down to the part that earns its place.

**Noise** goes without a second look:

- narration of what the next lines do; a docblock that restates the signature (`@param id the id`, `Returns the user.`);
- history and conversation: "fixed the bug", "now uses X", "added for the refactor", "as requested", author and date stamps. Git keeps history;
- commented-out code. Git keeps that too;
- banners and dividers. A file that needs them wants splitting, so a long one becomes a reshape target;
- a TODO whose work is already done, and empty doc stubs.

What usually stays:

- licence, copyright, and attribution for copied code;
- doc comments on the public API that state its contract: inputs, errors, invariants, units, thread-safety;
- docstrings a tool reads at runtime: click, typer, and argparse print them as help, FastAPI publishes them in OpenAPI, Sphinx renders them. Search for those uses before touching a `doc`;
- the reason a **foreign** constraint forces this shape (a vendor bug, a platform quirk, a protocol or spec rule), best with a link;
- a reason with evidence the code can't carry: a benchmark, an incident, an issue, RFC, or ADR link;
- a TODO or FIXME that links an open issue.

**Guards** are the comments that warn against a real mistake: warnings (`IMPORTANT`, `do not remove`, `order matters`, `keep in sync with`), workarounds, and untracked TODO, FIXME, or HACK notes. Deleting a true one costs an incident later, so investigate each: read its callers, then its history (`git log -L <start>,<end>:<file>`, the PR behind the commit, the issue it links). Every verdict on a guard names the evidence that settled it: a caller, a commit, a PR, or a version.

- A warning that is still true and that no test, type, or lint enforces is a reshape target: name the cheapest encoding (a test, an assertion, a type, a lint rule) and keep the comment until it exists. A warning proven obsolete goes.
- A workaround for an upstream bug: compare the pinned version with the version that fixed it. Fixed upstream makes the workaround code itself a reshape target.
- An untracked TODO that names a real open defect stays, and the report lists it so the user can file it.

When you can't settle a comment, let the cost of being wrong decide. Noise is cheap to restore from git, so it goes. A guard or a "why" you couldn't verify stays, listed as **unverified** with what you checked.

With more than about a hundred comments and subagents available, split the files into disjoint batches and give each subagent this section, step 3, and its batch; run step 4 yourself on the whole.

Done when every line `list` printed has a verdict: delete, keep (with its reason), reshape target, mismatch, or unverified.

## 3. Edit

Change comments and nothing else.

- Delete a comment whole: its markers, its line when nothing else is on it, and the blank line its removal doubles.
- Trim a kept comment by cutting: what remains is the part that earned its place, in its original words.
- Fix spacing by hand on the lines you touched. A formatter run over whole files reflows lines the branch never changed.

Done when every delete and trim verdict is applied.

## 4. Verify

```bash
python3 <skill-dir>/scripts/comments.py check
```

`check` compares each snapshotted file with the working tree, token by token with comments set aside, and exits 1 if any code or directive changed:

- `CODE`: you changed code. Revert that change.
- `DIRECTIVE`: revert it, unless you removed a suppression on purpose. Then prove it unused with the tool that reads it: `eslint --report-unused-disable-directives`, `tsc` (an unused `@ts-expect-error` fails it), `ruff check --select RUF100`, mypy's `--warn-unused-ignores`, or the linter's equivalent. If the tool still needs it, revert.

Read the diff of each file `list` skipped for having no lexer line by line. Then run the repo's lint and typecheck, and its tests when you changed a `doc` or a doc comment with examples in it.

Done when `check` passes, or prints only suppressions a tool proved unused; lint, typecheck, and tests pass as they did before the sweep; and `git status` shows only your comment edits, with anything your checks left behind (`__pycache__`, build output) removed.

## 5. Report

Use this shape and drop empty sections:

```
Comment sweep: <branch> vs <base>, <N> comments in <M> files

Deleted <D>: <count per kind: narration, restated signature, history, commented-out code, ...>
  each guard deleted: path:line — the evidence it was obsolete
Kept <K>: <count per reason>
  each guard or "why" kept: path:line — reason
Reshape targets:
  path:line `symbol` — the code change that makes the comment unnecessary
Mismatches:
  path:line — the comment said X, the code does Y
Untracked TODOs:
  path:line — what it says
Unverified:
  path:line — what you checked
Skipped: <files and why>
Verified: comments.py check <result>; <lint, typecheck, and test commands and results>
```

Then offer the reshape targets. If the user picks some, make each one a separate change from the sweep, with the project's tests passing, and delete the comment it replaces in the same change.
