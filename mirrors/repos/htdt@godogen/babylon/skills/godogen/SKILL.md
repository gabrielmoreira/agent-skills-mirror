---
name: godogen
display_name: Godogen
short_description: Generate or update complete Babylon.js browser games
default_prompt: "Use ${GODOGEN_COMMAND} to build or update this Babylon.js browser game from a natural-language design brief."
description: |
  Generate or update a complete Babylon.js browser game from a natural-language description. Use when the user wants ${AGENT_NAME} to make, rebuild, or substantially extend a Babylon.js project end to end.
---

# Babylon Game Generator

Generate and update Babylon.js browser games from natural language.

## Capabilities

Read each stage file from `${GODOGEN_SKILL_DIR}/` only when you reach that stage.

| File | Purpose | When to read |
|------|---------|--------------|
| `visual-target.md` | Generate reference image | Pipeline start |
| `decomposer.md` | Decompose into task plan | After visual target |
| `scaffold.md` | Vite/Babylon project shell | After decomposition |
| `architecture.md` | Babylon gameplay architecture stance | Before designing game code |
| `asset-planner.md` | Budget and plan assets | If budget provided |
| `asset-gen.md` | Asset generation CLI ref | When generating assets |
| `rembg.md` | Background removal | Only when an asset needs transparency removed |
| `task-execution.md` | Task workflow + commands | Before first task |
| `quirks.md` | Babylon/browser gotchas | Before writing code |
| `scene-generation.md` | Scene/world implementation patterns | When creating or replacing the playable scene |
| `capture.md` | Browser screenshot/video capture | Before screenshots or video |
| *(babylon-help skill)* | Babylon/Vite/browser API lookup | For Babylon-specific questions |

## Pipeline

```text
User request
    |
    +- Check if PLAN.md exists (resume check)
    |   +- If yes: read PLAN.md, STRUCTURE.md, MEMORY.md, ASSETS.md if present -> skip to task execution
    |   +- If no: continue with fresh pipeline below
    |
    +- Generate visual target -> reference.png + ASSETS.md (art direction only)
    +- Analyze risks + define verification criteria -> PLAN.md
    +- Scaffold/refresh Vite project -> package.json + src/ + STRUCTURE.md
    |
    +- If budget provided (and no asset tables in ASSETS.md):
    |   +- Plan and generate assets -> ASSETS.md + updated PLAN.md with asset assignments
    |
    +- Start/keep Vite dev server running at http://127.0.0.1:5173
    +- Execute risk slices first, then main build
    +- Use browser screenshots frequently while iterating
    +- If final presentation media is required:
        +- Record browser video to screenshots/result/{N}/video.mp4
```

## Assets

If a budget is provided, generating proper assets is part of the task. Use `asset-planner.md` / `asset-gen.md` before falling back to procedural stand-ins.

Runtime-loaded assets belong under `src/assets/**` when imported by TypeScript, or `public/**` only when a stable direct URL is needed. Keep reference images, prompts, source sidecars, and debug captures outside runtime asset paths.

## Execution

Read `task-execution.md` before starting. Keep `npm run dev` alive when possible. Vite hot reload should be the normal inner loop:

1. Edit `src/game/**` or `src/assets/**`.
2. Let the scene reload in the already-open browser.
3. Capture or inspect the browser.
4. Run `npm run check` before larger edits and `npm run build` before final media.

Chrome/Chromium and WebGL2 are required. If either is missing, stop and report the missing dependency rather than working around it. Hardware GPU acceleration is preferred — the capture script logs a prominent warning when WebGL2 falls back to a software renderer (SwiftShader, llvmpipe, lavapipe, etc) but still completes the capture. On a host with a GPU, treat that warning as a misconfiguration to fix; on a GPU-less host the warning is informational and the run still proves the task at reduced quality.

## Babylon Help

Use `babylon-help` for Babylon API questions, examples, loader behavior, Vite integration, browser capture issues, or exact import paths. Prefer the installed npm package sources/types for the current project version, then official docs.

## Context Hygiene

Keep important state in files:

- `PLAN.md` — task statuses and verification criteria
- `STRUCTURE.md` — architecture reference
- `MEMORY.md` — discoveries, quirks, workarounds, what worked or failed
- `ASSETS.md` — asset manifest with paths and generation details

After completing each task, update the relevant state files. Commit after verified task slices when the repo policy or user asks for commits.

## Visual Verification

Do not trust code alone. Verify visible work in the browser with screenshots or recorded video. When code and media disagree, trust the media. If a requirement is not visible in browser capture, treat it as unfinished.
