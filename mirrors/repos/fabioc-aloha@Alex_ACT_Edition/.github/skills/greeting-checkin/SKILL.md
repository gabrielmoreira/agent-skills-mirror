---
type: skill
lifecycle: stable
inheritance: inheritable
name: greeting-checkin
description: "Greeting-triggered self-check — recognise greetings, check Edition version against the upstream tag, scan AI-Memory announcements, and report inside the greeting reply"
tier: standard
applyTo: "**/*checkin*,**/*greeting*,**/*welcome*,**/*hello*,**/*hey*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Greeting Check-in

The heir's pull-based health check. Replaces the deleted weekly auto-update workflow. Fires from [greeting-checkin.instructions.md](../../instructions/greeting-checkin.instructions.md) on the first greeting of a session, or on demand via `/checkin`.

## Greeting Recogniser

Match case-insensitively against the trimmed first message. Treat as a greeting if it is **substantially** one of:

| Bucket | Examples |
|---|---|
| Salutation | `hi`, `hello`, `hey`, `yo`, `howdy` |
| Time-of-day | `good morning`, `good afternoon`, `good evening`, `morning`, `evening` |
| Check-in question | `how are you`, `how's it going`, `how have you been`, `what's up`, `you there` |
| Compound | any of the above plus the heir's name or a comma-suffix (`hi alex,`, `hey there`) |

**Do not** trigger on:

- Substantive requests that happen to start with "hi" (e.g. `hi, can you fix this build error?`) — process the request normally
- Acknowledgements (`thanks`, `ok`, `cool`, `got it`)
- Anything longer than ~80 characters — long messages aren't pure greetings

## Check Protocol

Run these in order. Each step is best-effort: if it fails, note the failure and continue.

### 1. Confirm this is a heir

Read `.github/.act-heir.json`. If absent, this isn't an ACT heir — abort the check silently and respond as a normal greeting.

Capture: `heir_id`, `edition_version` (current), `last_sync_at`.

### 2. Check Edition version

Run the upgrade script in dry-run mode and capture stdout:

```bash
node .github/scripts/upgrade-self.cjs
```

Parse the output for the `Edition version available:` line. Compare to `edition_version` from the marker.

Outcomes:

- **Same version** → "you're on the latest Edition (`vX.Y.Z`)"
- **New patch/minor available** → "Edition `vX.Y.Z` is out — patch/minor bump from `vA.B.C`. Run `/upgrade` when you're ready."
- **New major available** → "Edition `vX.0.0` is out — **major** bump from `vA.B.C`. `/upgrade` requires `--allow-major` and you'll want to read the release notes first."
- **Network error / git failure** → "couldn't reach Edition; will retry next session" — don't block

### 3. Check AI-Memory announcements

Resolve the AI-Memory root using the resolution algorithm from [ai-memory-setup](../ai-memory-setup/SKILL.md):

1. Check `cognitive-config.json` for `ai_memory_root` override
2. Auto-discover cloud drives (OneDrive, iCloud, Dropbox, Google Drive, Box, MEGA, pCloud, Nextcloud)
3. Skip folders listed in `ai_memory_exclude`
4. Pick the first drive with an existing `AI-Memory/` subfolder
5. Fall back to `~/AI-Memory`

Or use the CLI: `node .github/scripts/_registry.cjs --resolve .`

Once the root is resolved, check `<root>/announcements/alex-act/` for `*.md` files (skip `README.md`).

If the root resolves, check for announcements. Parse frontmatter for `date` (or fall back to file mtime). Filter to files newer than `last_sync_at` from the heir marker.

Outcomes:

- **AI-Memory not found** → "AI-Memory isn't set up yet. Run `node .github/scripts/_registry.cjs --discover` to see available cloud drives, then `--init <name>` to create it."
- **No new announcements** → "no new announcements"
- **1-3 new announcements** → list them by title, with one-line summaries
- **4+ new announcements** → say how many, list the most recent 3, point at the folder

### 3b. Execute auto_actions from announcements

If any announcement has `auto_actions` in its frontmatter, **execute them immediately** — do not ask the user. These are Supervisor-issued maintenance commands, not suggestions.

For each auto_action:

1. Read the `check_file` path relative to the repo root
2. If the file exists, execute the `if_exists` instruction
3. If the file is absent, execute the `if_absent` instruction
4. After all actions, stage changes and commit silently (unless nothing changed)
5. Report what was done in the greeting reply — one line per action with its result

### 4. Write the session marker

Create `/memories/session/greeting-checkin.md` with:

```markdown
# Greeting check-in fired

- date: <ISO date>
- edition_current: <version from marker>
- edition_available: <version reported by upgrade-self>
- announcements_new: <count>
```

This gates the instruction so it doesn't re-fire mid-session.

## Reply Format

Wrap the findings inside a normal greeting response. Keep it short — one paragraph if everything is clean, a tight bullet list if there's anything to act on. Examples:

**All clean:**

> Hey! Edition `v0.8.0` is current and AI-Memory has no new announcements. What are we working on?

**Update available:**

> Hi! Quick check-in: Edition `v0.9.0` shipped (minor bump from `v0.8.0`). One new announcement in AI-Memory: *"Brain-qa workflow update"*. Run `/upgrade` when you've got a moment. What's on the agenda?

**Major bump:**

> Morning. Heads up — Edition `v1.0.0` is out, which is a **major** bump from `v0.8.0`. Read the release notes before running `/upgrade --allow-major`. AI-Memory has 2 new announcements I'll list if you want. Where do you want to start?

## Failure Modes

| Failure | Behaviour |
|---|---|
| `upgrade-self.cjs` not found | Note "upgrade script missing — bootstrap may be incomplete", point at heir-doctor |
| Network unreachable | Skip the version check silently, still do AI-Memory + greeting |
| AI-Memory folder missing | Mention it once ("AI-Memory not configured"), don't repeat next session |
| Heir marker malformed | Run `node .github/muscles/heir-doctor.cjs` and report what it says |

## Falsifiability

This skill is decorative if, after 30 days of typical use, the user reports that:

- Greeting check-ins fire on non-greetings (false positives), or
- The reply text adds friction the user works around by skipping greetings, or
- Real Edition releases ship without the heir surfacing them within the first session after release

Re-evaluate at the 30-day mark; tune the recogniser or the reply format accordingly.

## Related

- [`greeting-checkin.instructions.md`](../../instructions/greeting-checkin.instructions.md) — the activation trigger (fires on session greeting)
- [`checkin.prompt.md`](../../prompts/checkin.prompt.md) — manual invocation
- [`upgrade.prompt.md`](../../prompts/upgrade.prompt.md) — the action to take when an update is available
- [`welcome.prompt.md`](../../prompts/welcome.prompt.md) — first-session orientation (different audience)
