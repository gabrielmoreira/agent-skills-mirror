---
name: ux-stress-test
description: Use when the user wants to stress-test UX flows, simulate first-time users, run usability or persona testing, or do pre-launch QA of a web app.
compatibility: Needs subagents, Chrome, browser-use (uv tool install browser-use) or playwright-cli as a fallback, and the app's source code to fix.
---

# UX stress test

You are the launch QA lead. Five blind personas chase first success in a real browser; you rank what tripped them up, the user picks what to fix or file, and a blind rerun proves the fixes.

- **First success**: the first moment a new user gets the value the product promises ("first invoice sent", not "account created"). All five personas chase the same one.
- **Friction moment**: any moment a persona is confused, stuck, or annoyed. Each becomes a screenshot plus a finding.
- **Blind**: personas know the app only through the browser: no source code, no earlier findings, no hint of what you fixed. A primed persona finds only what you expected.

Persona subagents follow `references/persona-protocol.md` plus their own file in `references/personas/` (impatient, skeptic, mobile, non-native, breaker). Read the protocol's findings format once so you know what comes back.

## 1. Set up the run

Done when every field of the persona brief (step 2) has a value and the app responds at the URL.

1. **Target.** Use the URL the user gave, or start the app in the background with the project's own scripts. Serve a production build when there is one: under slow 3G the mobile persona would otherwise time your dev server, not the product.
2. **First success.** Infer it from the landing page's promise and the routes or onboarding code. Write it as the user's goal in one sentence of your own words ("you have created your first invoice"), never the app's copy, which the fix pass may rewrite. Ask the user only when two readings are equally plausible.
3. **Production guard.** If the target is not localhost or an obvious staging/preview host, confirm with the user first: personas create real accounts, the breaker submits junk, and real emails may go out.
4. **Inbox and payment.** If signup needs email verification or a magic link, find how a dev signup receives it (a mail catcher such as Mailpit, a link in the server console, a dev-only bypass): that is the personas' inbox. Personas pay with the provider's test card only in test mode; otherwise they stop at the payment wall and report it.
5. **Browser driver.** Default: browser-use (`references/drivers/browser-use.md`); check `browser-use --version`. If missing, ask whether to install it (`uv tool install browser-use`) or use playwright-cli (`references/drivers/playwright.md`), and wait. For playwright-cli, check `playwright-cli --version` (else `npm install -g @playwright/cli@latest`); if `open --browser=chrome` fails, run `playwright-cli install-browser chrome`.
6. **Run folder.** `RUN=<project>/.ux-stress-test/<YYYYMMDD-HHMM>`; add `.ux-stress-test/` to `.git/info/exclude`.

## 2. Round 1: five blind personas

Spawn all five in one message, as general-purpose subagents. Give each exactly this brief, filled in, and nothing about the codebase or your guesses:

```
You are the <persona> persona in a UX stress test of a web app. Read and follow, in order:
1. <skill-dir>/references/persona-protocol.md
2. <skill-dir>/references/personas/<persona>.md

Run parameters:
- App URL: <url>
- First success: <one sentence>
- Inbox: <how verification emails or magic links arrive, or "not needed">
- Payment: <"stop at any payment wall" | "test mode: use <test card details>">
- Sign-up email: ux-<persona>-r<N>-<unix-time>@example.com
- Browser driver: <skill-dir>/references/drivers/<browser-use | playwright>.md
- Browser session: uxst-<persona>-r<N>
- Output dir: <RUN>/round-<N>/<persona>/
- Skill dir: <skill-dir>
- Round: <N>
```

Done when all five have written `findings.json`. Re-spawn a persona once with the same brief if it crashed or wrote nothing.

## 3. Merge and rank

Read the five `findings.json` files, opening a cited screenshot whenever the root cause is unclear. Merge findings that share a root cause into one issue: the mobile user's "button cut off" and the impatient user's "couldn't find Continue" may be one CSS bug. Keep different causes apart even on the same screen, and split a finding that holds two causes (a dead-end page *and* a crash) across both issues.

Rank issues by **how many personas hit them**, 5 down to 1; break ties by severity (blocker, major, minor), then by how early in the funnel the issue sits, since an early issue hides everything after it.

Write `RUN/round-1/issues.md` as one ranked table:

| # | Issue | Hit by | Severity | Where | Root cause | Findings |
|---|-------|--------|----------|-------|------------|----------|
| UX-01 | Password rule only revealed by a generic error | 4/5: impatient, mobile, non-native, breaker | blocker | /signup | Rule enforced server-side only; error says "Invalid input" | [impatient-r1-02](impatient/02-signup-error.png), [mobile-r1-03](mobile/03-invalid-input.png), … |

Tag an issue **needs owner** when code can't decide it (legal text, prices, brand voice, business rules), noting what the owner must supply. Those can only be filed, not fixed.

## 4. Show the findings and ask

Done when every issue has a choice: **fix now**, **open issue**, or **leave**.

Show the user the findings first: one outcome line per persona (first success or where they stopped), the ranked table, and the path to `issues.md`. Then ask, with the question tool when you have one:

- Fix every issue code can fix now; open issues for the needs-owner ones.
- Fix the blockers now; open issues for the rest.
- Open issues for everything, fix nothing now.
- Their own split, by ID ("fix UX-01 to UX-05, issue UX-09, leave the rest").

Wait for the answer. When the original request already said ("then fix whatever trips them up"), that is the answer: fix every issue code can fix, open no issues, and say so before you start. Record each choice in a `Decision` column in `issues.md`.

## 5. Open issues

Skip when no issue is marked **open issue**. Otherwise follow `references/opening-issues.md`. Done when each has a tracker URL in `issues.md`.

## 6. Fix the chosen issues

Skip when no issue is marked **fix now**. Done when each is fixed, or turned out to need an owner (tell the user and offer to open an issue).

On the project's default branch, create `ux-stress-test/<YYYYMMDD>` first. Then work down the chosen issues in table order:

- Fix each root cause once, where it lives, so one fix covers every persona's symptom.
- Reuse the project's components, design tokens, and copy conventions.
- Write new UI copy in plain, literal English; the non-native persona checks it in round 2.
- Leave terms, privacy policies, and prices for the owner; anything you invent there reads as real.
- Add a regression test for logic fixes (validation, double-submit, back navigation) when the project has a test setup.

Run the project's checks (typecheck, lint, tests, build) and restart the app so round 2 sees the fixed version. Replay each fixed blocker's `repro` yourself in a fresh browser session per the driver file: real browsers do what curl misses (Back restores form values, double-clicks race). In `issues.md`, note per fixed issue which files changed.

## 7. Round 2: blind rerun

Skip when nothing was fixed. Spawn the same five personas in one message, with round-2 parameters (new session names and sign-up emails, `Round: 2`) and nothing about what you fixed.

When a persona reports its journey, send it the retest as a follow-up (SendMessage to the same agent): "Now retest these round-1 findings from `<RUN>/round-1/<persona>/findings.json`, following the protocol's Retest section: <finding IDs behind the issues you fixed>." Skip personas with no such findings. The path and IDs go only in the follow-up, since a persona given them up front reads them before the journey. Done when every persona you sent a retest has written its results.

## 8. Verify and report

A fixed issue is **fixed** only when every persona who reported it marked its finding `fixed` in the retest, with an after screenshot, and no round-2 journey hit it again; nobody hitting it proves nothing, since a persona may have taken another path. Otherwise it is **still present**. Every other issue keeps its decision: **issue opened** (with the URL) or **left**.

List new round-2 friction separately: mark what your fixes caused as a **regression**, and say the rest were there all along and round 1 missed them.

Write `RUN/report.md`:

1. **Outcomes.** Per persona, round 1 → round 2: first success, or where they stopped.
2. **Issues.** The ranked table with a status column, before/after screenshot links for fixed issues, and tracker links for opened ones.
3. **Needs owner.** What to supply, and where it goes.
4. **New in round 2.** Regressions first.

Close the browser sessions you opened and stop any servers you started. Reply with the outcome lines, the counts (fixed / still present / issues opened / left / new), and the path to `report.md`. If anything is still present or new, ask whether to fix it, open issues for it, or stop.
