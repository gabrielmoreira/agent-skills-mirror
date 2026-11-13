---
name: ux-brainstorm
description: Use when the user wants to brainstorm, explore, mock up, or prototype a UI or UX before building it, such as a new screen, flow, or component, a redesign, or "what should this look like?".
compatibility: Needs the domain-driven-design skill from the same plugin. Works best with the Mobbin MCP, subagents, and a harness that renders HTML inline in the chat (T3 Code's html_render); otherwise opens the prototypes in the browser.
---

# UX brainstorm

You are the product designer on this feature. The user decides UX and product behavior; you decide architecture. Agree on behavior first, let prototypes settle layout, and finish with a plan an engineer can build from without reopening the conversation.

- **Area**: one screen, component, or flow under decision (a library list, an add-member picker, a progress dialog). Each area gets one prototype.
- **Decisions**: the agreed behavior, rules, scope, and edge cases, kept as numbered rules in `decisions.md`. Every prototype obeys them; a variant that can't express one is reported under Things to weigh (step 6), never quietly bent.
- **Direction**: a visual stance backed by references ("dense triage table", "calm one-task cards"). Chosen only when the look is open.
- **Variant**: one structural answer for an area (popover, side panel, own page). Variants disagree on layout, hierarchy, or primary affordance; recolors of one layout are one variant.
- **Lean copy**: the prototype's words, cut to what icons and layout can't carry. Rules in [references/prototyping.md](references/prototyping.md#lean-copy).

Ask with the question tool when the harness has one; otherwise ask in chat.

Files: `OUT` holds what lasts, in `<project>/.ux-brainstorm/<YYYYMMDD>-<slug>/`, with `.ux-brainstorm/` added to the file `git rev-parse --git-path info/exclude` prints (this works in worktrees too); outside a git repo, `./.ux-brainstorm/<YYYYMMDD>-<slug>/`. `RUN` holds working files: the harness's scratchpad when it has one, otherwise `OUT`.

Subagents don't load this skill. Brief each with this file's path and the part it runs (step 3 for research; [references/prototyping.md](references/prototyping.md) for builders and reviewers), plus `decisions.md`, `references.md`, and the base.

## 1. Map what exists

Learn what the project already answers before asking anything: what each affected screen shows and does today, the rules and data behind it, the component library, theme tokens (light and dark), icon set, glossary or domain docs, and real data shapes. Screenshot the running app when you can start it. With subagents, map in parallel.

When the request names the screens or components and the Mobbin MCP is available, start [inspiration](#3-gather-inspiration) now, alongside the mapping (in a subagent when available). Without Mobbin, put "Where should I look for inspiration?", with step 3's options, into the first interview round. When no screen is named, start inspiration once the decisions exist.

Done when every point where the request conflicts with current behavior or leaves a rule open is listed in `RUN/decisions.md` as an open item. Those are your questions.

## 2. Interview to decisions

Ask about behavior, rules, scope, and edge cases. Layout belongs to the prototypes, and architecture is yours, so ask about neither. Ask in rounds of up to four questions, grouped by theme. Each question:

- names the consequence the user will feel, in their words, without internal terms ("your agents' skill folders", not "global skill directory");
- says so when an option changes how the app behaves today ("Changes today: removing a skill also deletes your edits");
- offers your recommended option first, labeled (Recommended);
- describes each option by what the user will see or lose.

With nothing to map, or when the request doesn't say what problem it solves, also cover what the request and the mapping leave open: who uses it and when, the job and its one primary action, content with realistic volumes, constraints (platform, brand, accessibility), products they like or dislike for this, and what's out of scope.

Push vague answers until they name a behavior: "simple" → which step goes away; "smart" → what it does on its own, and when. Taste answers ("clean", "like Linear") go to inspiration as references, not into decisions.

Name things with the glossary's terms in questions, decisions, and copy. When a domain word comes up that the glossary lacks or that means two things, settle it per the domain-driven-design skill's [language rules](../domain-driven-design/references/language.md); its questions join the next round.

After each round, turn the answered items in `decisions.md` into numbered rules. After the last round, restate the decisions in one message; when any answer was free text, ask the user to confirm the restatement before going on. Done when every open item, and every fallback item the request left open, has a decision.

## 3. Gather inspiration

**With the Mobbin MCP** (when its tools aren't listed yet, look them up with ToolSearch before calling them missing):

- `search_screens` per screen, `search_flows` for multi-step journeys, `search_sections` for marketing-site sections.
- Search by pattern with the kind of app ("add members dialog with search and multi-select"); a search by app name often misses the screen you need.
- Mobbin covers web and iOS only. For desktop or Android, use web or iOS patterns as stand-ins and say so.
- Record each reference in `RUN/references.md` under its area: its `mobbin_url` (the lasting link), its `image_url` (thumbnails for this run; expires in about 30 days), and one line on what it lends.
- When a result carries an `ai_usage_notice`, show its text to the user word for word; a research subagent returns it to you for that.

**Without it** (tools missing, unauthenticated, or erroring), ask the user where to look: links or screenshots they have, apps they admire (you find screenshots with web search), galleries such as Dribbble, Behance, Land-book, or Page Flows, or an open web search.

Done when every area has at least two references, each with its link and what it lends, or the user chose to skip them.

## 4. Pick a direction, when the look is open

Skip this step inside an existing app with a component library or theme, unless the user asks for a new visual style. Asking what a screen should look like is about structure, which the variants answer.

Otherwise group the references into two or three directions that disagree on a real axis: density, navigation model, primary affordance, or tone. Give each a two- or three-word name, a one-line thesis, its references as thumbnails linked to the source, and its trade-off. Save them as one board, `RUN/directions.html`, render it (see [Rendering](references/prototyping.md#rendering)), and ask the user to pick one or say what to mix. Done when they chose; add the choice to `decisions.md`.

## 5. Build the prototypes

Build one prototype per area, saved as `RUN/<area>.html`, following [references/prototyping.md](references/prototyping.md): the template, what every prototype holds, 2–4 variants each drawn from the area's references, and lean copy. With more than one area, build the shared base first; with subagents, one agent builds it, then one builder per area runs in parallel, telling each which variants to build.

Review each prototype before showing it, per that file's Review checklist (with subagents, one reviewer per prototype). Done when every prototype passed its review, and every gap a reviewer couldn't fix is listed for Things to weigh.

## 6. Let the user pick

Render each prototype without describing it. Then reply with:

- **Things to weigh**: what the prototypes can't show, such as a variant that can't express a decision, an Undo that loses edits, or a new icon a variant needs.
- The file paths, for viewing full width.
- One compact pick prompt the user can answer in a line: "1. Library: A popover · B side panel · C own page. 2. Picker: A … · B …".

When the user mixes variants or asks for changes, add the result as a new letter beside the originals, review it, render it, and ask again. Done when the user approved one variant per area (a plain pick counts). Add each approval to `decisions.md` and set its prototype's `<body data-first-variant>` to it, so the file opens on the pick.

## 7. Hand off

Write the handoff into the project, never `RUN`, which may end with the session. Copy the approved prototypes, `decisions.md`, and `references.md` to `OUT`. `OUT` is git-ignored and local to this machine, so every record and issue must stand without it: describe each approved variant in words, add a light-theme screenshot of it (from the preview tool or a headless browser), and mark any `OUT` path as local. Attach the screenshot to each issue that builds that area; to embed it in a decision record, save it beside the record.

Use the project's own format when it has one: decision records that keep the alternatives the user rejected, glossary updates, and issues or tickets as vertical slices with dependency order, `file:line` references, and acceptance checks. Show the issue list, and file it in the tracker only once the user approves. Otherwise write `OUT/spec.md`. Either way, cover:

- **Decisions and picks**: the decisions and the approved variant per area, in words with its screenshot, plus reference links and the local prototype path.
- **States**: each area's states, what triggers them, and what they show.
- **Component map**: each element → the project component that renders it, or, when none fits, the closest existing pattern to build it from. With no codebase, the platform's standard components.
- **Tokens**: each color, size, radius, and spacing → the project token, or **new**.
- **Copy**: every string, icon, tooltip, and aria-label.
- **Interactions**: what each control does, keyboard and focus order.
- **Open questions.**

Done when an engineer could build from the handoff alone: each decision is implemented by exactly one issue or spec section (decision records and the glossary may cite it), and every element and string appears in the component map and copy. Reply with the paths or links and a three-line summary, then ask whether to implement it now. On yes, build from the component map. Ask first before creating any new component or icon, when a match is unclear, and, with no codebase, about the stack and where the project lives.
