---
name: peon-ping-create-pack
description: 'Internal — invoked headlessly by `peon create`; humans should run `peon create` instead. Author and render a brand-new PeonPing draft pack — invoked headlessly as: "Use the peon-ping-create-pack skill to draft a pack: name=<n> flavor=<f> vibe=<v> draft_root=<dir>. Follow the skill exactly." Authors all 7 CESP categories honoring the vibe, writes openpeon.json (draft-stamped) and prompts.json, renders every sound via scripts/pack-render.py, and always ends by telling the human to run `peon eval <name>`.'
---

# peon-ping-create-pack

You are drafting ONE brand-new PeonPing pack from scratch. Work only inside
the draft directory you create. Do not touch any other directory, do not
install anything, do not commit anything, and never finish by declaring the
pack "done" or "installed" — a freshly created pack is never installed
directly (see Hard rules).

## If invoked without name/flavor/vibe/draft_root

This skill is internal: it is only ever invoked headlessly by `peon create`
with `name`, `flavor`, `vibe`, and `draft_root` already filled in. If you were
invoked WITHOUT all four (a human ran this directly with missing arguments),
do nothing except tell them to run `peon create` instead. Do not touch any
files. Exit.

## Procedure

1. Parse the invocation: `name` (already validated by the caller against
   `^[a-z0-9][a-z0-9_-]*$`), `flavor` (`sfx` or `voice`), `vibe` (a one-line
   description), `draft_root`.
2. Compute `draft_dir = <draft_root>/<name>`. If it already exists, STOP —
   tell the human a draft with that name already exists and to run
   `peon eval <name>` on it (never overwrite an existing draft). Otherwise
   create `draft_dir/sounds/`.
3. Author a concept honoring the vibe, covering **all 7 CESP categories**
   with **at least one sound each**: `session.start`, `task.acknowledge`,
   `task.complete`, `task.error`, `input.required`, `resource.limit`,
   `user.spam`. This mirrors the concept-authoring discipline of the
   `brand-to-peon-packs` skill's step 2:
   - Every sound needs a `label` — short, caption-quality text describing
     what's heard (not a filename, not a restatement of the category — e.g.
     "Soft acknowledgement", "Serene completion", not "task_complete_0").
   - Keep the aesthetic consistent across all 7 sounds so the pack reads as
     one coherent idea, not seven unrelated clips. Let the `vibe` string
     drive instrument palette / tone / register (e.g. "calm bells" implies
     soft chimes and bowls throughout, never harsh or percussive).
   - **`flavor: sfx`** — wordless. Each sound needs a `prompt`: a concrete,
     renderable description for ElevenLabs sound-generation (instrument or
     texture, character, brief shape — e.g. "two gentle bells, soft decay,
     warm room tone"). Avoid vague adjectives with nothing to render ("nice
     sound") — describe what would actually produce the sound.
   - **`flavor: voice`** — spoken. Each sound needs `text` (an in-character
     line fitting the category and vibe) plus a `voice_id` (an ElevenLabs
     voice id). Reuse ONE `voice_id` across all 7 sounds — a pack has one
     voice, not seven. If no voice was specified in the invocation, pick a
     stock ElevenLabs voice whose character plausibly fits the vibe; do not
     invent a `voice_id` string — use one you can confirm actually exists
     (list voices via the ElevenLabs API if unsure).
4. Write `draft_dir/openpeon.json` — a CESP manifest with `cesp_version`,
   `name`, `display_name`, `version` (start at `"0.0.1"`), a short
   `description` reflecting the vibe, and `"x_openpeon_draft": true`
   (**always** — a pack authored by this skill is never anything but a
   draft). `categories` maps each of the 7 category names to
   `{"sounds": [{"file": "sounds/<category>_<index>.wav", "label": "..."}]}`.
5. Write `draft_dir/prompts.json` — the contract the `peon-ping-remix` skill
   reads for rerolls: `{"<file>": {"type": "sfx"|"tts", "prompt": "..."}}`
   for sfx sounds, or `{"<file>": {"type": "tts", "text": "...", "voice_id":
   "..."}}` for voice sounds. Keys are the same `file` paths used in
   `openpeon.json` (relative to `draft_dir`, e.g. `sounds/session_start_0.wav`).
6. Render every sound. For each entry, write a small job file **under
   `draft_dir/jobs/`** (e.g. `draft_dir/jobs/render-job-<category>_<index>.json`
   — never at the draft root; `approve` prunes everything under `jobs/`, so a
   render input left at the root would ship as junk in the approved pack)
   shaped as `{"type": "sfx"|"tts", "prompt"|"text"+"voice_id", "out": "<absolute
   path to the WAV>"}`, then run:
   ```
   python3 <peon-ping>/scripts/pack-render.py --job <file>
   ```
   Pass `--mock` when the environment variable `PEON_RENDER_MOCK=1` is set —
   this writes a silent placeholder WAV instead of calling ElevenLabs, so the
   whole draft can be authored and rendered with no network, no API key, and
   no ffmpeg. This is how automated tests exercise this skill.
   (Resolve `<peon-ping>` as the scripts directory next to the running peon
   install, in the same order the `peon-ping-remix` skill uses: `$PEON_DIR/scripts`
   when set, else `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/peon-ping/scripts`,
   else the repo checkout you were invoked from.)
7. The renderer exits nonzero on a malformed job, a missing key, or a
   silent-after-retry render. If ANY sound fails to render, STOP — print the
   renderer's stderr and exit nonzero. Do not leave `openpeon.json` claiming
   sounds exist that never rendered; it is fine to leave the partial
   `draft_dir` on disk for the human to inspect or retry — do not delete it.
8. After every sound renders successfully, print a short summary (pack name,
   flavor, category count, sound count) and **always** end by telling the
   human to run:
   ```
   peon eval <name>
   ```
   to listen to and approve the draft. Never claim the pack is finished,
   ready to use, or installed — creation only ever produces a draft that
   still has to clear the eval gate.

## Hard rules

- NEVER write outside `draft_dir`.
- NEVER set `x_openpeon_draft` to anything but `true`.
- NEVER install the pack, copy it into a packs directory, or otherwise make
  it directly usable — that only happens via `peon eval <name>` → approve.
- NEVER print or log an ElevenLabs key.
- Honor `PEON_RENDER_MOCK=1` by passing `--mock` to every `pack-render.py`
  call — this is load-bearing for tests and for previewing the flow without
  spending API credits.
- The flow ALWAYS ends by telling the human to run `peon eval <name>` —
  creation never ends with an installed pack.
