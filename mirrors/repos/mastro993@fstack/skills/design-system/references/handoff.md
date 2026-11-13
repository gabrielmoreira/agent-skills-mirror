# Handoff

Follow this once the user has confirmed the system and picked a delivery. For **Both**, do Plan, then Issues. Every pick ends with [Building in a new session](#building-in-a-new-session). Where the project already keeps plans or specs, its location and format win over the ones here.

## First, for every pick: commit the spec

Commit `DESIGN.md` and every approved spec change, on a branch unless the user says otherwise. Everything after this reads from the repository, not from this conversation.

## Plan

1. Write the plan to `docs/design-system/plan.md`, or to the project's own plans or specs folder, in the plan format of [formats.md](formats.md#plan-docsdesign-systemplanmd).
2. Update every page under `docs/` whose description the plan makes wrong, and link the plan from the project's docs index when it has one.
3. Commit the plan with the spec.

Done when the plan holds the catalog with a tier for every component, every opportunity with its call sites, and the slices in order with their checks and dependencies.

## Issues

1. **Find the tracker** from the project: the git remote with `gh`, or a tracker MCP. With none reachable, say so, keep the slices in the plan (write it when the user picked Issues alone), and stop here.
2. **Push the branch** that holds the spec and plan, so the links in the issues open for people without this checkout. When the push fails, tell the user the links won't open until it is pushed.
3. **Create one issue per slice**, in build order (tokens, then atoms, molecules, organisms), so each issue names its blockers by number. Use the issue format of [formats.md](formats.md#issue), the tracker's own dependency or sub-issue links when it has them, and the project's labels.
4. **Reply** with the issue links and the build order: what comes first, what can run in parallel, and why.

Done when every slice has an issue, every blocker is named by number, and the user has the order.

## Building in a new session

Ask whether to start building now. On yes, start a new session with the harness's own means (a new thread, session, or background agent); without one, give the user a prompt to paste. A new session sees only what is on disk in its checkout, so start it in this checkout or in one that has the commit.

The prompt names the plan or the issues, `DESIGN.md`, and the first slice, and says:

- build the slices in order, one at a time, each with its tests, and keep the app working after each;
- write the module README from the plan's outline in the first slice, and add each component to its catalog as it lands;
- ask before adding any dependency, or before changing a spec file beyond what the plan approved.

Done when the new session is running, or the user holds the prompt, or they said not now.
