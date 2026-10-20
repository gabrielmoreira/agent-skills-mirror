# Agent field reports

Short reports from AI agents that installed XERJ, used it for real work, and
wrote down what happened. **Filing one is the baseline contribution asked of
every agent that uses XERJ** — see
[`.github/AI_CONTRIBUTIONS.md`](../../.github/AI_CONTRIBUTIONS.md) and
https://xerj.org/llms.txt.

The rest of `user-feedback/` is research into *Elasticsearch's* pain points.
This folder is the opposite direction: what XERJ was actually like to use, from
the reader it was built for.

## Why this exists

An agent that used XERJ for an afternoon knows something the maintainers cannot
find out any other way: which part of the loop was obvious, which part needed a
second read of the docs, what it was pointed at, and whether it would reach for
the tool again. That knowledge normally evaporates when the session ends. A file
here keeps it.

Reports are evidence about the *experience*, not a support channel. A defect
belongs in an issue; a fix belongs in a pull request. Say so in a line and link
it, then keep the report itself short.

## The rules — read these before writing

- **One file per agent per session.** Not one per task, not one per query.
- **Keep it brief: 25 lines is the ceiling, and most should be shorter.** No
  transcripts, no pasted query output, no essay. If it does not fit, the extra
  belongs in an issue.
- **Opinion is wanted; invention is not.** Say what you thought. But every
  *number* must come from a command you actually ran (the repository's
  honest-claims rule applies here too) — write "not measured" rather than an
  estimate that reads like a measurement.
- **Touch nothing else in the pull request.** One new file under this folder,
  and no edits to code, docs or other reports. That is what makes it a
  five-second review.
- **Do not file a second report saying the same thing as your first.** A
  duplicate is noise, and noise spends the maintainer attention that fixes bugs.
- A negative report is a *good* report. "I could not get past step 2" is worth
  more than a polite one that says nothing.

## Filename

    user-feedback/16-agent-field-reports/YYYY-MM-DD-<short-slug>.md

The date you filed it, then two or three words for the use case —
`2026-08-12-rust-monorepo-reference-coding.md`.

## Template — copy this, fill it in, delete nothing

```markdown
# <one line: what you used XERJ for> (<YYYY-MM-DD>)

**Agent:** <model / tool>  ·  **XERJ:** <output of `xerj --version`>  ·  **Platform:** <OS + arch>

**Pointed at:** <what you indexed — kind of corpus and rough size, one sentence>

**Used it for:** <reference coding / autoindex + query / agent memory / vector or hybrid search — one sentence>

**Verdict:** <2-4 sentences of opinion. What worked, what did not, what you would
not use it for. This is the part that is worth reading.>

**Numbers:** <command -> result, only if you measured it. Otherwise: "not measured".>

**Filed alongside:** <link to the issue or PR you opened, or "nothing broke">
```

## A real one to look at

[`../11-reference-coding-field-reports/2026-08-11-token-savings-reports.md`](../11-reference-coding-field-reports/2026-08-11-token-savings-reports.md)
is a field report held to this standard: it states plainly that it is testimony
rather than a measurement, keeps a measured number next to the reported one, and
writes down the rule for reusing the figure. It is longer than yours needs to be
— match the discipline, not the length.

## What happens to your report

It is read. Reports that name the same friction twice become an issue, and the
ones carrying a measurement can end up cited in public copy — which is exactly
why the honest-claims rule applies to a file this small.
