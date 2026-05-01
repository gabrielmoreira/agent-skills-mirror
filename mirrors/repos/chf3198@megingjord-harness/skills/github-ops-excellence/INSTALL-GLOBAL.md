# Install Globally (All Projects)

Install this as a personal skill so it is available in every repository.

## 1) Create personal skill folder

Create:

- `~/.copilot/skills/github-ops-excellence/`

## 2) Copy the skill file

Copy:

- `docs/workflow/skills/github-ops-excellence/SKILL.md`

To:

- `~/.copilot/skills/github-ops-excellence/SKILL.md`

## 3) Confirm discovery

In chat, run:

- `/skills list`

Ensure `github-ops-excellence` appears.

## 4) Invoke by mode

- `/github-ops-excellence mode=triage scope=repo`
- `/github-ops-excellence mode=pre-pr scope=repo`
- `/github-ops-excellence mode=pre-merge scope=repo`
- `/github-ops-excellence mode=release-readiness scope=repo`
- `/github-ops-excellence mode=admin-audit scope=org`

## 5) Optional additional locations

If you use shared skill directories, enable them in Copilot skill locations.

## Safety reminder

This skill should propose bounded process and governance improvements only. It must not silently loosen branch, review, or security protections.
