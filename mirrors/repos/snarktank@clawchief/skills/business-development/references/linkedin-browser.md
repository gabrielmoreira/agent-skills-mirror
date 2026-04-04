# LinkedIn browser workflow

Use this reference when the task involves LinkedIn profile investigation, connection requests, acceptance checks, or any LinkedIn UI flow that requires judgment rather than a single obvious button.

## Recommended browser architecture

Prefer this order:

1. **Dedicated agent-controlled browser profile** (`openclaw` or a dedicated profile like `linkedin`)
   - Best default for unattended work
   - Persistent agent-owned browser state
   - No attach prompt to {{OWNER_NAME}}'s personal Chrome session
2. **Remote CDP browser** (Browserbase / Browserless / remote node-hosted browser)
   - Use when the browser should live outside {{OWNER_NAME}}'s Mac or when always-on remote control matters
3. **`user` profile / Chrome attach**
   - Fallback only when {{OWNER_NAME}}'s existing signed-in Chrome state is required *and* {{OWNER_NAME}} is at the computer to approve the attach prompt

Why:
- OpenClaw docs explicitly position `user` / existing-session attach as the path for reusing a real signed-in browser session when the human is present to approve attachment.
- For unattended workflows, a dedicated agent-controlled browser is the correct substrate.

## Profile guidance

### Preferred local path

Use a dedicated browser profile for LinkedIn work:
- `openclaw` if no dedicated LinkedIn profile exists yet
- otherwise a dedicated profile like `linkedin`

Log LinkedIn into that dedicated browser once, then keep using that same profile for future work.

### Preferred remote path

If the founder wants browser control decoupled from the Mac, use a remote CDP profile:
- Browserbase
- Browserless
- a node-hosted browser proxy on another machine

Keep the workflow skill profile-agnostic so the same logic works whether the browser is local-managed or remote CDP.

## Investigation logic for LinkedIn profiles

Do **not** rely on one signal alone unless it is decisive.

### Decisive signals

Treat as **not accepted / still pending** when:
- `Pending` is visible anywhere in the top action area or profile controls
- the visible connection degree is `2nd` or `3rd` and there is no stronger contrary evidence

Treat as **accepted** when:
- the visible connection degree is `1st`

### Important caution

Do **not** mark a connection as accepted from `Message` alone.
Some LinkedIn surfaces can show message-related actions without proving a first-degree connection.

## Investigation sequence

For each profile:

1. Open the LinkedIn profile in the chosen agent-controlled browser profile.
2. Inspect the top card first.
3. Check for `Pending`.
4. Check the visible degree badge (`1st`, `2nd`, `3rd`).
5. If status is still unclear, inspect `More` / the 3-dots menu.
6. If still unclear, leave the tracker unchanged and note it as ambiguous rather than guessing.

## Batch acceptance-check workflow

When checking many profiles in the outreach sheet:

1. Read the current sheet rows first.
2. Filter to leads where:
   - LinkedIn connection request sent = `Yes`
   - LinkedIn accepted != `Yes`
3. Reuse one browser tab/profile through the batch when possible.
4. Only update the sheet on **clear evidence**.
5. Prefer fewer larger writes when practical, but do not risk incorrect bulk updates.
6. Record ambiguous cases separately instead of forcing a classification.

## Tracker update rules

- `LI connect accpeted` -> set to `Yes` only on clear evidence, preferably `1st`
- Leave it unchanged for `Pending`, `2nd`, `3rd`, or ambiguous states
- Put operational notes in `{{ASSISTANT_NAME}}'s Notes`, not `{{OWNER_NAME}}'s Notes`

## Human-like operating behavior

LinkedIn often hides the decisive state in different places. Act like an investigator, not a script:
- check the obvious action row first
- then the degree badge
- then the `More` menu if needed
- prefer verification over speed
- never guess from a partially loaded page

## If browser control is flaky

1. Prefer switching away from `user` / attach mode before adding more retries.
2. Use the managed agent-controlled browser profile if possible.
3. If {{OWNER_NAME}} needs off-machine reliability, move the same workflow to a remote CDP profile.
4. Only use the Chrome attach path when {{OWNER_NAME}} is present and explicitly wants reuse of his live personal browser session.
