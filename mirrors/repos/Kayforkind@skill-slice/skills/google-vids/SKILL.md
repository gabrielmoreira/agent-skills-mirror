---
name: google-vids
version: 1.0.1
description: "Creates structured Google Vids (vids.new) work videos via Help me create: prompt plus attached Docs/Sheets/Slides become outline, scenes, stock media, script, AI voiceover, 8s Veo clips, and avatars. Use when the user wants an explainer, launch, or training video from a prompt or document. Not for cinematic Veo/Flow footage, Slides-only decks, or live-action NLE editing."
---

# Google Vids (vids.new)

Google Vids is the Workspace AI video app. The signature flow is **Help me create**: a prompt plus attached files becomes a fully editable, scene-based video with stock media, script, and AI voiceover.

**Desktop only.** Maximum video length is 30 minutes. Consumer access requires Google AI Pro/Ultra; Workspace accounts may also have access depending on plan.

## When to Use

Route here (vs Flow/Veo) when the goal is a **structured, narrated work video** — explainer, training, launch, internal comms, product walkthrough — not cinematic footage.

Trigger keywords: *google vids*, *vids.new*, *help me create*, *ai video*, *explainer video*, *training video*, *voiceover*, *veo clip*, *ai avatar*.

Do **not** route here for:
- Cinematic / photoreal footage generation → use Veo directly.
- Slides-only presentations → use Google Slides.
- Live-action video editing → use a dedicated editor.

## Prerequisites

1. **Desktop browser** — Vids is desktop-only. Disable any mobile emulation in your browser automation context.
2. **Plan** — Google AI Pro or Ultra (consumer), or a Workspace plan with Vids access.
3. **Reference file** — Read `google-ai-ultra/reference.md` **first** before driving Vids. It contains the canonical browser-automation loop (navigate → snapshot → type → click → wait → snapshot) and MCP tool-call conventions used throughout this skill.
4. **Attached files** — Any Doc/Sheet/Slide you attach via `@` must be shared with the same Google account you are using, or it will not appear in the attach menu.

## Feature Map

| Feature | Use |
|---|---|
| **Help me create** | Prompt + `@`-attached Docs/Sheets/Slides → outline + suggested scenes + stock media (video/image/music) + script + AI voiceover |
| **Veo tool** | Generate 8s clips from text or an image, with native audio |
| **AI avatars** | 12 presets, up to ~30s each, ~20 generations/week; write a script, avatar presents it lip-synced |
| **AI voiceover** | Per-scene or all-scenes; many languages; "Voiceover outdated" badge when script changes |
| **Recording studio** | Record yourself / screen / camera and insert |

## Procedure

### Step 0 — Load the reference

Before any Vids automation, read `google-ai-ultra/reference.md`. It defines the MCP browser tool sequence, snapshot interpretation, and wait strategies. All steps below assume those conventions.

### Step 1 — Navigate to Vids

```
browser_navigate → https://vids.new
```

- If redirected away or the editor does not load, see Pitfalls (desktop-only / plan check).

### Step 2 — Start "Help me create"

```
browser_snapshot
```

Find the **Help me create** prompt input or button. Click it:

```
browser_click → <Help me create input/button selector>
```

### Step 3 — Enter the prompt

```
browser_type → "Create a 2-minute product launch video for our new app"
submit=false
```

### Step 4 — Attach a source document

Type ` @` (space + at-sign) inside the prompt field to open the attach menu:

```
browser_type → " @"   (submit=false)
browser_snapshot
```

Click the target Doc/Sheet/Slide in the results list:

```
browser_click → <target document in attach menu>
```

If the `@` menu does not open, see Pitfalls.

### Step 5 — Submit

```
browser_click → <Create / Submit button>
```

### Step 6 — Wait for outline generation

```
browser_wait_for(time=45)
browser_snapshot
```

The editor should now show a scene outline with stock media thumbnails, script text, and scene titles. If the spinner is still running, wait to 60s and re-snapshot. If still stuck after 90s, reload and resubmit (see Pitfalls).

### Step 7 — Generate AI voiceover

```
browser_snapshot
```

Find **Generate voiceover** (all scenes) and click:

```
browser_click → <Generate voiceover button>
browser_wait_for(time=30)
browser_snapshot
```

Confirm audio/waveform indicators appear on scenes.

If "Generate voiceover for all scenes" is not found, open each scene's **Voiceover/Audio** menu and generate per-scene.

### Step 8 — (Optional) Generate a Veo clip

From within the editor, use the Veo tool to generate an 8s clip from text or an image with native audio. Insert the clip into a scene.

### Step 9 — (Optional) Add an AI avatar

Select one of 12 avatar presets (up to ~30s each, ~20 generations/week). Write or paste a script; the avatar will present it lip-synced. Insert into a scene.

### Step 10 — (Optional) Recording studio

Use the recording studio to record yourself, your screen, or your camera and insert the recording into the video.

## Pitfalls

- **"Help me create" missing or page redirects** — Vids is desktop-only and needs an AI Pro/Ultra (or Workspace) plan. Disable mobile emulation, verify the plan, and retry.
- **`@` menu doesn't open** — The cursor may not be in the field. Use `browser_evaluate` to focus the `[contenteditable]` element and dispatch an input event, or click the field first, then retype ` @`.
- **Outline spinner exceeds 90s** — Wait to 60s, re-snapshot. If still stuck, reload the page, re-enter the prompt, and resubmit.
- **"Generate voiceover for all scenes" not found** — Some editor states expose voiceover only per-scene. Open the scene's **Voiceover/Audio** menu and generate individually.
- **Attached Doc not applied** — The document must be shared with the same Google account. Re-trigger `@` and reselect the document.
- **Voiceover produces no audio** — Each scene needs script text. Confirm a supported language is selected, then regenerate.
- **"Voiceover outdated" badge** — Script has changed since the voiceover was generated. Regenerate the voiceover for the affected scenes.
- **AI avatar limit hit** — ~20 generations/week cap. Wait for the weekly reset or use fewer/shorter avatar segments.
- **Veo clip longer than 8s** — Veo clips are capped at 8s. Split content across multiple clips if needed.

## Verification

After completing the flow, verify success with these checks:

1. **Outline present** — `browser_snapshot` shows an editable outline: multiple scenes, each with script text, a stock-media thumbnail, and a title.
2. **Voiceover generated** — Snapshot shows audio indicators (waveform / duration / "Voiceover ready") on all scenes.
3. **Scene 1 plays** — Preview scene 1; confirm a play state and audio duration (voiceover actually generated, not just queued).
4. **Attached content reflected** — Script text or scenes reference content from the attached Doc/Sheet/Slide.

## Related Skills

- `google-ai-ultra` — Parent skill; read `google-ai-ultra/reference.md` for the canonical MCP browser-automation loop.
- `google-veo` — For standalone cinematic / photoreal video generation (not structured work videos).
- `google-flow` — For Flow-based video generation workflows.
