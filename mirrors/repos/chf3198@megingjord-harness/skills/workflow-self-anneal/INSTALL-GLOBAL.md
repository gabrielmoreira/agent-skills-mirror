# Install Globally (All Projects)

Use this skill as a **personal skill** so it is available in every repository.

## 1) Create personal skill folder

Create:

- `~/.copilot/skills/workflow-self-anneal/`

## 2) Copy the skill file

Copy this file:

- `docs/workflow/skills/workflow-self-anneal/SKILL.md`

Into:

- `~/.copilot/skills/workflow-self-anneal/SKILL.md`

## 3) Confirm skill discovery in chat

In chat, run:

- `/skills list`

You should see `workflow-self-anneal`.

## 4) Optional: invoke directly

- `/workflow-self-anneal context=post-failure scope=stability`

## 5) Optional: additional shared locations

If you maintain a central skills directory, enable it via skill locations in your Copilot settings.

## Recommended usage cadence

- Session start (quick drift check)
- Immediately after any crash/failure
- Pre-merge for high-risk changes
- Post-release for incident-derived guardrails

## Safety reminder

This skill should propose bounded process improvements only. It should never perform recursive self-modification or bypass approval/security controls.
