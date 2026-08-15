---
name: crit
description: "Drives the crit CLI blocking-review loop: GitHub-style inline comments on diffs, plans, live URLs, or local HTML, then applies unresolved review.json comments; also covers UI/UX accessibility and responsive design review. Use when the user asks to review, critique, revise UI, or run crit. Not for /better quality passes, GitHub PR reviews that never launch crit (github-code-review), or WCAG-only audits."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - ui-ux
  - design
  - accessibility
  - visualization
  - code-review
  - crit
tools:
  - gemini
  - codex
---

# Review with Crit

`crit` opens a browser-based review surface where a human leaves GitHub-style inline comments, then writes them to a structured JSON file you read and act on. This skill covers both the `crit` CLI workflow and modern UI/UX design review guidance.

## When to Use

Use this skill when the user wants to:

- **Run a code or plan review** using the `crit` tool — reviewing diffs, plan files, live dev-server URLs, staging URLs, or local HTML files.
- **Review or revise UI/UX designs** — interface design, accessibility, responsive layouts, design systems, component behavior, interaction states, visual hierarchy, or usability improvements.
- **Address inline review comments** left by a human via `crit` and apply fixes.
- **Push or pull review comments** to/from GitHub PRs.
- **Share a review** via a public URL or QR code.

Trigger keywords: review, critique, crit, inline comments, UI review, UX review, accessibility check, design review, design system, responsive layout, interaction states, plan review.

## Prerequisites

- The `crit` binary must be on `PATH`. If missing, point the user at the [crit README](https://github.com/tomasz-tomczyk/crit) install instructions.
- GitHub PR sync additionally needs the `gh` CLI installed and authenticated.
- Windows host is primary (PowerShell). Adjust shell quoting for PowerShell when running `crit` commands (single quotes work in PowerShell for literal strings, but `echo` piping uses different syntax — prefer `--file` for JSON on Windows).

## Procedure

### Part A: Running a Crit Review Session

#### Step 1 — Pass arguments to `crit`

The CLI auto-detects the review mode from its arguments. **Do not ask the user which mode to use.** Pass arguments through:

```bash
crit <arguments>               # file, dir, URL, .html — CLI auto-detects mode
crit --pr <num|url>             # GitHub PR (range mode)
crit --range <base>..<head>     # commit range (range mode)
crit                            # no args → branch diff
```

If no arguments are provided, check conversation context:

1. If a plan file was written earlier in this conversation → `crit <plan-file>`
2. Otherwise → bare `crit` (branch diff)

#### Step 2 — Launch crit and block until review completes

**CRITICAL — you MUST run this step. Do NOT skip it. Do NOT proceed without it.**

Run `crit` in the foreground and block until it exits:

```bash
crit <plan-file>   # specific file
crit               # git mode
```

If a crit server is already running from earlier in this conversation, `crit` automatically connects to it. Starting from scratch, it spawns the daemon, opens the browser, and blocks until the user clicks "Finish Review".

`crit` prints the review URL on startup (e.g. `Started crit daemon at http://localhost:<port>`). Relay it verbatim:

> **"Crit is open at http://localhost:\<port\>. Leave inline comments, then click Finish Review."**

**Do NOT proceed until `crit` completes.** Do NOT ask the user to type anything. Do NOT read the review file early. Wait for the foreground command to finish — that is how you know the human is done reviewing.

#### Step 3 — Read the review output

When `crit` completes, its stdout includes the path to the review file (e.g. `Review comments are in /path/to/review.json`). Read it.

The file contains structured JSON with three comment scopes:

- `review_comments` (top-level array, `r_`-prefixed IDs) — general feedback
- File comments (per-file `comments` array, `start_line: 0`) — about the file as a whole
- Line comments (per-file `comments` array, with `start_line`/`end_line`) — about specific lines

Identify all comments where `resolved` is `false` or **missing** — both mean unresolved. Only `true` means resolved.

Comment fields to watch:

- `quote`: the specific text the reviewer selected — focus changes on the quoted text, not the entire line range
- `anchor`: full text of the commented lines when placed — use it to locate current position; line numbers may be stale after edits
- `drifted: true`: original content was removed or heavily rewritten — line numbers are approximate at best
- `replies`: check before acting — if you already replied, the reviewer may be following up rather than requesting a new change

**Review file format:**

```json
{
  "review_comments": [
    {
      "id": "r_f1e2d3",
      "body": "Overall the architecture looks good",
      "scope": "review",
      "author": "User Name",
      "resolved": false,
      "replies": [
        { "id": "rp_b4a5c6", "body": "Thanks, addressed it", "author": "Agent" }
      ]
    }
  ],
  "files": {
    "path/to/file.go": {
      "comments": [
        {
          "id": "c_a1b2c3",
          "start_line": 5,
          "end_line": 10,
          "body": "Comment text",
          "quote": "the specific words selected",
          "anchor": "The sessions table needs a complete rewrite...",
          "author": "User Name",
          "resolved": false,
          "replies": []
        }
      ]
    }
  }
}
```

#### Step 4 — Address each review comment

For each unresolved comment:

1. Understand what the comment asks for.
2. If it contains a suggestion block, apply that specific change.
3. Revise the referenced file (plan or code file from the diff).
4. Reply with what you did: `crit comment --reply-to <id> --author '<your name>' '<what you did>'` (reply bodies support markdown).
5. **Do not pass `--resolve`.** Resolving is the reviewer's call. Only add `--resolve` if the user explicitly asks.

Editing the plan or code file triggers Crit's live reload — the user sees changes in the browser immediately.

**Replying to multiple comments** — use `--json` for a single bulk call:

```bash
echo '[
  {"reply_to": "c_a1b2c3", "body": "Fixed"},
  {"reply_to": "c_d4e5f6", "body": "Refactored as suggested"}
]' | crit comment --json --author '<your name>'
```

**If there are zero review comments**: inform the user no changes were requested and stop.

#### Step 5 — Signal completion and start the next round

**CRITICAL — you MUST run this step. Do NOT skip it. Do NOT proceed without it.**

When Step 2's `crit` command exits with feedback, it prints `Next round: crit <args>` to stdout. Run that command verbatim — the daemon is keyed by args, so mismatched args spawn a new daemon instead of reconnecting.

On subsequent calls, `crit` automatically signals round-complete first, then blocks until the next "Finish Review" click.

Tell the user: **"Changes applied. Review the diff in your browser and click Finish Review when ready."**

**Do NOT proceed until `crit` completes.** When it does, return to Step 3. If the user finishes with zero comments, the review is approved — stop the loop and proceed.

### Part B: Authoring Comments Programmatically

Beyond replies, you can author original comments — useful when reviewing someone else's work or in multi-agent workflows.

```bash
crit comment --author '<your name>' '<body>'                       # review-level (general feedback)
crit comment --author '<your name>' <path> '<body>'                # file-level (whole file)
crit comment --author '<your name>' <path>:<line> '<body>'         # single line
crit comment --author '<your name>' <path>:<start>-<end> '<body>'  # line range
crit comment --reply-to <id> --author '<your name>' '<body>'       # reply
```

**Hard rules for authoring:**

- **Pass `--author '<your name>'`** so comments are attributed correctly (use the name of the agent or tool you are). If omitted, crit falls back to the configured VCS user name.
- **Always single-quote the body** — double quotes break on backticks and shell metacharacters.
- **Line numbers reference the file on disk** (1-indexed), not diff line numbers.
- **Only pass `--resolve` when the user explicitly asks.** Never resolve proactively.

**Bulk commenting (3+ comments)** — use `--json` for atomicity (single write, no partial state) and speed. JSON comes from stdin or `--file <path>`:

```bash
echo '[
  {"body": "overall feedback", "scope": "review"},
  {"path": "session.go", "body": "restructure", "scope": "file"},
  {"file": "src/auth.go", "line": 42, "body": "Missing null check"},
  {"file": "src/auth.go", "line": "50-55", "body": "Extract to helper"},
  {"reply_to": "c_a1b2c3", "body": "Fixed — added null check"}
]' | crit comment --json --author '<your name>'
```

For multi-paragraph bodies, prefer `--file` — a literal newline inside a `"body"` string breaks JSON parsing. Write the JSON to a temp file, then:

```bash
crit comment --json --file /tmp/crit-bulk.json --author '<your name>'
```

Per-entry fields: `file`/`path` (relative path; `path` alone → file-level), `line` (`42` or `"45-47"`), `body` (always required), `author` (per-entry override), `scope` (`review`/`file` — usually inferred), `reply_to` (comment ID), `resolve` (only when the user asks).

If `crit comment` errors with "comment found in multiple files", disambiguate with `--path <file>` (or set `file` on the JSON entry). Review-level IDs (`r_`) are globally unique and never need this.

### Part C: Sharing Reviews

```bash
crit share <file> [file...]   # Upload and print URL
crit share --qr <file>        # Also print QR code (terminal only)
crit unpublish                # Remove the shared review
```

- **Always relay the full output** — copy the URL (and QR if used) directly into your response. Don't make the user dig through tool output.
- **`--qr` is terminal-only** — skip it in mobile apps or web chat UIs where Unicode block characters won't render.
- If a review file exists, comments for the shared files are included automatically.
- Unpublish uses the persisted delete token in the review file — no extra args needed.

### Part D: GitHub PR Integration

```bash
crit pull [pr-number]                                    # Fetch PR review comments into the review file
crit push [--dry-run] [--event <type>] [-m <msg>] [pr]   # Post review comments as a GitHub PR review
```

Requires the `gh` CLI installed and authenticated. PR number is auto-detected from the current branch. `--event` values: `comment` (default), `approve`, `request-changes`. `-m` adds a review-level body message.

### Part E: UI/UX Design Review (2026)

When the review involves UI/UX design (not just code correctness), apply the following workflow alongside the crit review loop.

**Inputs to collect:** target users, primary task, platform, viewport range, existing design system, accessibility requirements, brand constraints, data density, interaction states, and success metric. Ask for screenshots or reference URLs when visual fidelity matters.

**Workflow:**

1. Start from the user task and information architecture, not decoration.
2. Map key states: empty, loading, success, error, disabled, permission-limited, offline, and responsive variants.
3. Apply accessibility requirements early: keyboard flow, focus visibility, labels, contrast, reduced motion, touch targets, text resizing, and semantic structure.
4. Use design-system primitives where available; otherwise define tokens for spacing, color, type, elevation, radius, and motion.
5. Design responsive layouts with stable dimensions and no text overlap across desktop and mobile.
6. Validate with realistic content, long labels, error text, and touch/keyboard interaction.
7. Deliver concrete implementation guidance, not vague aesthetic notes.

**Output format:** Return a design or implementation plan with: user goal, layout structure, component list, states, accessibility checks, responsive behavior, copy notes, and verification steps. For code tasks, include exact files/components and testing guidance.

## Pitfalls

- **Skipping the blocking step**: You MUST block on the `crit` foreground command until it exits. Reading the review file early or proceeding without the command finishing means the human hasn't finished reviewing yet.
- **Mismatched args on next round**: The daemon is keyed by args. If you run `crit` with different arguments than the original invocation, it spawns a new daemon instead of reconnecting. Always run the `Next round: crit <args>` command verbatim.
- **Resolving comments proactively**: Never pass `--resolve` unless the user explicitly asks. Resolving is the reviewer's call.
- **Missing `--author`**: If omitted, crit falls back to the configured VCS user name, which may not be the agent's identity. Always pass `--author '<your name>'`.
- **Double-quoted bodies**: Double quotes break on backticks and shell metacharacters. Always single-quote the body.
- **Newlines in JSON bodies**: A literal newline inside a `"body"` string breaks JSON parsing. Use `--file <path>` for multi-paragraph bodies.
- **Stale line numbers**: After edits, line numbers in comments may be stale. Use the `quote` and `anchor` fields to locate the correct position. If `drifted: true`, line numbers are approximate at best.
- **`resolved` field missing**: A missing `resolved` field means unresolved — treat it the same as `false`. Only `true` means resolved.
- **Ambiguous file paths**: If `crit comment` errors with "comment found in multiple files", disambiguate with `--path <file>`.
- **`--qr` in non-terminal contexts**: Skip `--qr` in mobile apps or web chat UIs where Unicode block characters won't render.
- **UI/UX conflicts**: If requirements conflict, prioritize usability, accessibility, and product fit over novelty. If a requested visual pattern harms readability or accessibility, explain the tradeoff and offer a better variant.

## Verification

1. **Crit binary available:**
   ```bash
   crit --version
   ```
   Expected: prints version string. If not found, direct user to install instructions.

2. **Review file exists after `crit` exits:**
   ```bash
   ls -la /path/to/review.json
   ```
   Expected: file exists with valid JSON content.

3. **Validate JSON structure:**
   ```bash
   cat /path/to/review.json | python -m json.tool
   ```
   Expected: pretty-printed JSON with `review_comments` array and `files` object.

4. **Count unresolved comments:**
   ```bash
   cat /path/to/review.json | python -c "import json,sys; d=json.load(sys.stdin); rc=[c for c in d.get('review_comments',[]) if c.get('resolved')!=True]; fc=[c for f in d.get('files',{}).values() for c in f.get('comments',[]) if c.get('resolved')!=True]; print(f'{len(rc)} review-level, {len(fc)} file-level unresolved')"
   ```
   Expected: integer counts of unresolved comments.

5. **Verify replies were sent:**
   ```bash
   cat /path/to/review.json | python -c "import json,sys; d=json.load(sys.stdin); [print(c['id'], len(c.get('replies',[]))) for c in d.get('review_comments',[])]"
   ```
   Expected: each comment ID with reply count > 0 for those you addressed.

6. **UI/UX quality checklist:**
   - User can complete the core task quickly and repeatedly.
   - UI supports keyboard, screen readers, visible focus, and sufficient contrast.
   - Mobile and desktop layouts do not overlap or rely on fragile viewport-scaled text.
   - Controls use familiar affordances and expose state clearly.
   - Motion is purposeful and respects reduced-motion preferences.
   - Visual direction is intentional and consistent with the product domain.

## Related Skills

- **code-review** — general code review without the `crit` browser surface.
- **accessibility-audit** — deeper WCAG compliance auditing.
- **design-system** — design token and component library maintenance.

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C Understanding WCAG 2.2: https://www.w3.org/WAI/WCAG22/Understanding/intro
- Apple Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines
- Material accessibility guidance: https://m2.material.io/design/usability/accessibility.html
- Material Design 3: https://m3.material.io/
- crit README: https://github.com/tomasz-tomczyk/crit
