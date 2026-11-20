# S1 · Meeting-to-actions

**What it does:** turns any meeting (a Teams recap, a Capture recording, typed notes or a long email thread) into the same structure every time: **Decisions → Actions (owner, due, source) → Open questions → Flagged.**

**Why a skill and not a prompt:** the summarise-a-thread prompt ([P1](../../prompts/everyone.md#summarise-a-long-email-thread-into-decisions-open-questions-and-owners)) and the site-walk prompt ([P6](../../prompts/project-delivery.md#turn-a-site-walk-or-in-person-meeting-into-decisions-and-actions)) both work, but people tweak them every time, so every team's minutes end up looking different. A skill fixes the format once. Everyone gets the same table, and "Not stated" shows up consistently wherever an owner is missing.

**Licence:** Microsoft 365 Copilot · **Status:** draft, pending live test · **Last verified:** pending re-test

## When to use it
- After any meeting where more than two actions came out of it.
- When you're handed someone else's notes and need to act on them.
- Before forwarding a long thread to someone who wasn't on it.

## Setup

**Option A: as a Copilot custom skill**
1. Download [`SKILL.md`](SKILL.md).
2. Put it in a folder called `meeting-to-actions` inside the **Skills** folder in your OneDrive. If the Skills folder doesn't exist yet, Copilot creates it the first time you add a skill from the **+** menu in the Copilot pane.
3. In the Copilot pane, open **+ → Skills** and choose `meeting-to-actions`, or just ask for "actions from this meeting" and Copilot should pick it up from the description.

**Option B: as agent instructions (Agent Builder)**
1. In Copilot Chat, go to **Agents → Create agent**.
2. Paste everything below the `---` front matter of `SKILL.md` into **Instructions**.
3. Name it "Meeting to actions" and share it with your team.

## Limits
- Owners and dates are only as good as what was said out loud. The skill deliberately writes **Not stated** instead of guessing. That's a feature: it shows you where the meeting was vague.
- Transcripts with crosstalk or poor audio produce poor names. Check the Owner column.
- Custom skills were first documented in PowerPoint and Excel. Support in other apps varies, so in Outlook and Teams use Option B.

See [`example-output.md`](example-output.md) for what good looks like.
