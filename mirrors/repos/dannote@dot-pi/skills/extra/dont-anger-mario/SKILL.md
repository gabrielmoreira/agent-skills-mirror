---
name: dont-anger-mario
description: Prepare concise, high-signal issues or contribution proposals for the pi repository without annoying maintainers. Use when filing issues/PR proposals for earendil-works/pi or mentioning Mario/pi tracker etiquette.
---

# Don't Anger Mario

Use this skill before opening an issue or contribution proposal in `earendil-works/pi`.

## Rules

- Read `CONTRIBUTING.md` first.
- Use an official issue template; blank issues are disabled.
- Keep it short. If it does not fit on one screen, it is too long.
- Write in the user's own voice, not corporate/AI slop.
- Be concrete: what, why, and optionally how.
- Do not submit automatically.
- Before submitting, ask the user to confirm they carefully read the exact final draft and explicitly approve posting it.
- If proposing a change, use **Contribution Proposal** rather than Bug Report.
- If reporting a bug, include minimal repro and version.
- If opening a PR, only proceed after maintainer approval (`lgtm` for PRs; `lgtmi` is issues only).
- Do not send agent-only PRs. If the user cannot explain the change without the agent, stop.

## Safe workflow

1. Inspect templates and contributing docs:

```bash
gh api repos/earendil-works/pi/contents/.github/ISSUE_TEMPLATE --jq '.[].name'
gh api repos/earendil-works/pi/contents/CONTRIBUTING.md --jq .content | base64 --decode
```

2. Draft the issue body in `/tmp`, never inline long Markdown through shell quoting:

```bash
cat > /tmp/pi-issue.md <<'EOF'
### What do you want to change?

...

### Why?

...

### How? (optional)

...
EOF
```

3. Show the exact final title and body to the user.

4. Ask for explicit approval with this wording:

```text
Please read the draft carefully. Do you explicitly approve me posting this issue/proposal as written?
```

Do not proceed on vague approval like "ok" if the user has not seen the exact final draft.

5. Create only after explicit approval:

```bash
gh issue create \
  --repo earendil-works/pi \
  --template contribution.yml \
  --title "Short concrete title" \
  --body-file /tmp/pi-issue.md
```

## Extra caution from prior tracker behavior

Known maintainer reactions that shape this workflow:

- Auto-close gate is intentional; maintainers review closed issues later.
- GitHub Actions outages can let the issue/PR gate fail and flood the repo.
- Maintainers dislike agent-only PRs because they take time to review and are often broken.
- "Clanker misunderstood the code" is a real failure mode; verify the claim before drafting.
- A label/comment like `possibly-openclaw-clanker` is a warning sign: shorten, verify, and make the human reasoning obvious.

Useful receipts:

- https://github.com/earendil-works/pi/issues/3589 — "very tired of clankers"
- https://github.com/earendil-works/pi/issues/5259 — "your clanker misunderstood"
- https://github.com/earendil-works/pi/pull/2666 — "You and your clanker are banned"
- https://github.com/earendil-works/pi/pull/5296 — "please do not send more agent only PRs"

## Good contribution proposal shape

```md
### What do you want to change?

One concrete change.

### Why?

The user-visible problem and why it matters.

### How? (optional)

Small implementation sketch, if useful. Avoid over-design.
```

## Tone

Good:

> Prompt templates support `$1` and `$ARGUMENTS`, but optional arguments cannot have defaults. I want `/next` and `/next 3` to expand cleanly without asking the model to interpret an empty argument.

Bad:

> Implement advanced Bash-compatible templating with all parameter expansion semantics, conditionals, filters, and expression evaluation.
