# Handoff

Follow this once the user has picked how to continue. For **Both**, do Issues, then New session.

## First, for every pick: commit the docs

Both handoffs read the docs from outside this conversation. Commit the spec, ADRs, glossary, and updated docs, on a branch unless the user says otherwise.

## Issues

1. **Find the tracker** from the project: the git remote with `gh`, or a tracker MCP. With none reachable, say so, leave the slices in the spec, and stop here.
2. **Push the branch** that holds the docs. Issues are read by people without this checkout, so link the spec and ADRs at that branch, where every link opens. When the push fails, tell the user the links won't open until it is pushed.
3. **Create one issue per slice** of the spec, in dependency order, so each issue can name its blockers by number. Each issue has an outcome as its title, what to build, acceptance checks, links to the spec and its ADRs, and what it is blocked by, in the issue format of [formats.md](formats.md). Use the tracker's own dependency or sub-issue links when it has them, and label the issues the way the project labels its own.
4. **Reply** with the issue links and the implementation order: what comes first, what can run in parallel, and why.

Done when every slice has an issue, every blocker is named by number, and the user has the order.

## New session

Start a new session with the harness's own means (a new thread, session, or background agent). Without one, give the user a prompt to paste. The prompt names the spec, the ADRs, and the first slice or issue, and says to implement from them as decided, test-first with the test-driven-development skill, turning each acceptance check into a test.

A new session sees only what is on disk in its checkout: start it in this checkout, or in one that has the commit.

Done when the new session is running, or the user holds the prompt.
