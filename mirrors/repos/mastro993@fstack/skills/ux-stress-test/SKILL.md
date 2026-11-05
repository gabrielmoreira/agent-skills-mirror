---
name: ux-stress-test
description: Use when the user wants to stress-test UX flows, simulate first-time users, run usability or persona testing, or do pre-launch QA of a web app.
compatibility: Needs subagents, Chrome, browser-use (uv tool install browser-use) or playwright-cli as a fallback, and the app's source code to fix.
---

# UX stress test

You are the launch QA lead. Five first-time users try to reach first success in a real browser; you merge what tripped them up, show the user the ranked findings, then fix what they choose and send the personas back in to prove it, or open issues for later.

- **First success**: the first moment a new user gets the value the product promises ("first invoice sent", not "account created"). All five personas chase the same one.
- **Friction moment**: any moment a persona is confused, stuck, or annoyed. Each one becomes a screenshot plus a finding.
- **Blind**: personas know the app only through the browser: no source code, no earlier findings, no hint of what you fixed. A rerun only proves something if it is blind.

Persona subagents follow `references/persona-protocol.md` plus their own file in `references/personas/` (impatient, skeptic, mobile, non-native, breaker). Read the protocol's findings format once so you know what comes back.

## 1. Set up the run

Done when every field of the persona brief (step 2) has a value and the app responds at the URL.

1. **Target.** Use the URL the user gave. Otherwise start the app yourself, in the background, using the project's own scripts (package.json, README, Makefile). Serve a production build (build, then start/preview) when the project has one. Dev servers ship hundreds of unbundled modules and dev-only error overlays. A first-time user never sees those, and under slow 3G the mobile persona would end up timing your dev server, not the product.
2. **First success.** Infer it from what the landing page promises and from the routes or onboarding code. Write it as the user's goal, in one sentence of your own words ("you have created your first invoice"), not by quoting the app's copy. The fix pass may rewrite that copy, and round-2 personas will then chase words that no longer exist. Ask the user only when two readings are equally plausible.
3. **Production guard.** If the target is not localhost or an obvious staging/preview host, confirm with the user before you start. Personas create real accounts, the breaker submits junk, and real emails may go out.
4. **Inbox and payment.** If signup needs email verification or a magic link, find how a dev signup receives it: a mail catcher such as Mailpit, a link logged to the server console, or a dev-only bypass. Describe that as the personas' inbox. If the flow asks for payment, personas use the provider's test card only when the app runs in test mode. Otherwise they stop at the payment wall and report it.
5. **Browser driver.** Personas drive Chrome with browser-use (`references/drivers/browser-use.md`). Check that `browser-use --version` works. If it's missing, ask the user whether to install it (`uv tool install browser-use`) or continue with playwright-cli (`references/drivers/playwright.md`), and wait for the answer. For playwright-cli, `playwright-cli --version` works (else `npm install -g @playwright/cli@latest`); if `open --browser=chrome` fails, run `playwright-cli install-browser chrome`.
6. **Run folder.** Set `RUN=<project>/.ux-stress-test/<YYYYMMDD-HHMM>` and add `.ux-stress-test/` to `.git/info/exclude`. This keeps screenshots out of commits without touching the project's `.gitignore`.

## 2. Round 1: five blind personas

Spawn all five in one message so they run in parallel, as general-purpose subagents. Give each one exactly this brief, filled in. Leave out anything about the codebase or your guesses about what's broken, because a primed persona finds what you expected and nothing else.

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

Read the five `findings.json` files. Open a cited screenshot whenever the text leaves the root cause unclear. Merge findings that share a root cause into one issue, meaning the same broken thing seen by different personas. The mobile user's "button cut off" and the impatient user's "couldn't find Continue" may be one CSS bug. Keep different causes apart even when they sit on the same screen. When one finding holds two causes (a dead-end page *and* a crash), split it across both issues.

Rank issues by **how many personas hit them**, 5 down to 1. Break ties by severity (blocker, then major, then minor), then by how early in the funnel the issue sits, since an early issue hides everything after it.

Write `RUN/round-1/issues.md` as one ranked table:

| # | Issue | Hit by | Severity | Where | Root cause | Findings |
|---|-------|--------|----------|-------|------------|----------|
| UX-01 | Password rule only revealed by a generic error | 4/5: impatient, mobile, non-native, breaker | blocker | /signup | Rule enforced server-side only; error says "Invalid input" | [impatient-r1-02](impatient/02-signup-error.png), [mobile-r1-03](mobile/03-invalid-input.png), … |

Tag an issue **needs owner** here when code can't decide it: legal text, prices, brand voice, business rules. Note exactly what the owner must supply. Those can go to an issue, not to the fix pass.

## 4. Show the findings and ask

Done when every issue has a choice: **fix now**, **open issue**, or **leave**.

Show the user the findings first: one outcome line per persona (first success or where they stopped), the ranked table, and the path to `issues.md`. Then ask what to do with them, using the question tool when you have one:

- Fix every issue code can fix now; open issues for the needs-owner ones.
- Fix the blockers now; open issues for the rest.
- Open issues for everything, fix nothing now.
- Their own split, by ID ("fix UX-01 to UX-05, issue UX-09, leave the rest").

Wait for the answer. When the original request already said what to do ("then fix whatever trips them up"), that is the answer: fix every issue code can fix, open no issues, and say so before you start.

Record each issue's choice in a `Decision` column in `issues.md`.

## 5. Open issues

Skip when no issue is marked **open issue**. Done when each one has a tracker URL in `issues.md`.

Use the project's tracker: GitHub issues when `gh repo view` works, otherwise ask the user where issues go. If there is none, write one Markdown file per issue to `RUN/issues/UX-NN.md` and say so. File one issue per `UX-NN`, written for a developer who never saw this run:

- **Title**: the issue in plain words ("Signup hides the password rule until it fails").
- **Body**: hit by (count and personas), severity, where, root cause; repro steps and expected behaviour from the clearest finding; one line per persona in their own words; for needs-owner issues, what the owner must supply.
- **Screenshots**: open each one before attaching it. Attach it only if it shows nothing sensitive (secrets, real personal data, internal-only identifiers); name any you held back and why. If the tracker can't take attachments, list the screenshot file names.

## 6. Fix the chosen issues

Skip when no issue is marked **fix now**. Done when each one is fixed, or turned out to need an owner (then tell the user and offer to open an issue).

If the project is on its default branch, create a branch `ux-stress-test/<YYYYMMDD>` first. Then work down the chosen issues in table order:

- Fix each root cause once, where it lives, so one fix covers every persona's symptom.
- Reuse the project's components, design tokens, and copy conventions.
- Write new UI copy in plain, literal English. The non-native persona checks it in round 2.
- Leave terms, privacy policies, and prices for the owner to write; anything you invent there reads as real.
- Add a regression test for logic fixes (validation, double-submit, back navigation) when the project has a test setup.

Then run the project's checks (typecheck, lint, tests, build) and restart the app so round 2 sees the fixed version. Replay each fixed blocker's `repro` yourself in a fresh browser session, following the driver file. Real browsers do things a curl check misses (Back re-fetches pages and restores form values; double-clicks race), and a blocker caught here saves a whole round. In `issues.md`, note per fixed issue which files changed.

## 7. Round 2: blind rerun

Skip when nothing was fixed. Spawn the same five personas again in one message, with the same brief and round-2 parameters (new session names, new sign-up emails, `Round: 2`). Tell them nothing about what you fixed.

When a persona reports its journey, send it the retest as a follow-up message (SendMessage to the same agent, so it keeps its setup): "Now retest these round-1 findings from `<RUN>/round-1/<persona>/findings.json`, following the protocol's Retest section: <finding IDs behind the issues you fixed>." A persona with no such findings gets no follow-up. The path and IDs go only in that follow-up because a persona given them up front tends to read them before the journey, and then the journey isn't blind. Done when every persona you sent a retest has written its results.

## 8. Verify and report

A fixed issue is **fixed** only when two things hold: every persona who reported it marked its finding `fixed` in the retest, with an after screenshot, and no round-2 journey hit it again. Nobody running into it is not proof, because a persona may simply have taken another path. Otherwise it is **still present**. Every other issue keeps its decision: **issue opened** (with the URL) or **left**.

New friction from round 2 goes in a separate list. Mark as a **regression** any item your fixes caused. The rest were there all along and round 1 missed them; say so.

Write `RUN/report.md` with these sections:

1. **Outcomes.** Per persona, round 1 → round 2: did they reach first success, and if not, where did they stop?
2. **Issues.** The ranked table with a status column, before/after screenshot links for fixed issues, and tracker links for opened ones.
3. **Needs owner.** What to supply, and where it goes.
4. **New in round 2.** Regressions first.

Close the browser sessions you opened and stop any servers you started. Then reply to the user with the outcome lines, the counts (fixed / still present / issues opened / left / new), and the path to `report.md`. If anything is still present or new, ask whether to fix it, open issues for it, or stop; the skill doesn't loop on its own.
