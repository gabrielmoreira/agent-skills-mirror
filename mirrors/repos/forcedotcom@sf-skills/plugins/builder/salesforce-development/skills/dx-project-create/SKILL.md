---
name: dx-project-create
description: "Scaffold a new Salesforce DX project of any template — standard, empty, analytics, agent, or a React/Angular UI-bundle app — and set it up end-to-end: relocate the session, connect an org, set the default, enable source tracking. Use when the user asks to create or scaffold a new Salesforce/SFDX project, start a new React/Angular Salesforce app, or run 'sf template generate project'. DO NOT TRIGGER for: building/editing/styling an EXISTING UI-bundle app (experience-ui-bundle-frontend-generate); scaffolding only a UI bundle as a step of building one out (experience-ui-bundle-project-generate, experience-ui-bundle-app-coordinate); tool validation (platform-environment-validate); org auth (login); project stats; scratch orgs (dx-org-manage)."
metadata:
  domains: ["Developer Experience"]
  relatedSkills:
    - "experience-ui-bundle-project-generate"
    - "experience-ui-bundle-frontend-generate"
    - "experience-ui-bundle-deploy"
    - "platform-environment-validate"
    - "dx-org-manage"
  cliTools:
    - tool: ["npm"]
      semver: ">=8.0.0"
    - tool: ["sf"]
      semver: ">=2.0.0"
allowed-tools:
  - Bash
  - Read
---

# Creating a New Salesforce Project

Walk the user through a wizard that scaffolds a new Salesforce DX project, relocates this session into the new project, connects it to an org, and configures it for development. Run each step in order, confirming with the user before any environment-changing action.

The `salesforce-development` plugin's MCP servers (`salesforce-api-context`, `salesforce-metadata-experts`, `salesforce-lsp`) are provided by the **installed plugin**, not by the project — so they stay available in the new project automatically once the session relocates. There is no per-project `.mcp.json` to copy.

## Step 1: Choose a Project Template

This skill scaffolds **every** template the CLI offers, including React/Angular UI-bundle apps — creating a project is a core capability and shouldn't require installing a separate plugin just to pick a template. (Once the project exists, the `experience-ui-bundle-*` skills own *building it out* — pages, components, styling, deploy — but the initial scaffold happens right here, whether or not that plugin is installed.)

Read the template set **live from the CLI** — never hardcode it, because Salesforce adds templates over time and a baked-in list goes stale:

```bash
sf template generate project --help
```

Parse the `-t, --template=<option>` line's `<options: a|b|c|…>` list — those pipe-separated names are the authoritative template set. As of writing the CLI offers eight, all scaffolded here: `standard`, `empty`, `analytics`, `agent`, plus the UI-bundle set `reactinternalapp`, `reactexternalapp`, `angularinternalapp`, `angularexternalapp` (React/Angular × internal/external audience). Treat the live parse as the source of truth; the list here is only a fallback if the parse fails.

**Intent shortcut first.** Take the shortcut **only when the request fully resolves to exactly one template.** Anything with a missing choice goes to the picker so it can ask — never guess. Resolve `{template}` directly when:

- The request **names a non-UI template**: "empty/minimal project" → `empty`; "analytics project" → `analytics`; "agent project" → `agent`; "standard project" → `standard`.
- The request is a **UI-bundle app with BOTH framework AND audience clear** → the matching UI template (e.g. "internal React app" → `reactinternalapp`, "customer-facing Angular portal" → `angularexternalapp`). Internal = employee-facing/already-authenticated; external = customer/partner-facing with a login flow.

**A description of the app is NOT a template name.** "Build me a personal todo app", "an inventory tracker", "a CRM for my team" describe *what* to build, not *which* template — they do NOT resolve to a template, so they do **not** qualify for the shortcut. Do not infer `standard` (or any template) from the app's purpose, however obvious it seems: `standard` being the picker's default does not license skipping the picker. When the user hasn't named a template or a framework, **you must show the picker and let them choose** — silently assuming a template is the exact miss this step exists to prevent.

Everything else falls through to the picker, including:
- a bare "new project" / "create a Salesforce project" with no template named (the picker defaults to **Standard**),
- a **described app** with no template or framework named ("a todo app", "an inventory tracker") — surface the picker; never assume the app's purpose maps to a template, and
- a **partially-specified UI app** — e.g. "create a React app" with no audience. Never assume an audience. When the framework is already known but the audience isn't, skip the top-level picker and go straight to the framework/audience follow-up below to collect only the missing piece.

**Otherwise ask one `AskUserQuestion` — "What kind of project?"** (single-select, four options). `AskUserQuestion` caps at four choices, so the picker surfaces the four most-requested kinds; **`empty` is deliberately picker-omitted** and reached only via the intent shortcut above ("empty/minimal project"). That is intentional — `empty` is the rarely-picked bare-project template, and spending one of four scarce slots on it would crowd out a common choice. A user who wants it names it and the shortcut resolves it directly.

- **Standard** → `standard` (the default) — general-purpose `force-app` metadata project (Apex, LWC, objects, flows).
- **Agentforce agent** → `agent` — ships a sample Local Info Agent.
- **CRM Analytics** → `analytics` (Tableau CRM) — adds the `waveTemplates` directory.
- **React / Angular UI app** → a UI-bundle starter. This needs a framework + audience, so ask **one follow-up `AskUserQuestion`** ("Which UI framework and audience?", four options) that maps directly to `{template}`:
  - **React — internal** → `reactinternalapp` · **React — external** → `reactexternalapp`
  - **Angular — internal** → `angularinternalapp` · **Angular — external** → `angularexternalapp`
  - Internal = employee-facing/already-authenticated; external = customer/partner-facing with login, registration, and profile.

The resolved template is `{template}`, which feeds Step 3. If the live CLI adds a new template, add it here (or, if it's another rarely-picked one, wire it as an intent-shortcut keyword rather than a fifth picker slot).

## Step 2: Choose a Project Name

Prompt the user for a project name. It becomes the new directory name **and is interpolated into the shell commands below**, so it MUST be strictly validated before any command uses it — never pass a raw name through.

**Allowlist, then reject-and-re-prompt.** Accept only names matching `^[A-Za-z0-9][A-Za-z0-9_-]*$` — letters, digits, `_`, and `-`, starting with a letter or digit. Anything else (spaces, path separators like `/`, a leading `.` or `..`, or shell metacharacters such as `; | & $ > < ( ) \` " '`) is invalid: explain why and ask again. A name like `proj;rm -rf ~` must never reach a command. As defense in depth, the commands below also quote `"{name}"` — but validation is the real guard, not the quoting.

## Step 3: Generate the Project

**Verify before generating** — do not run the command until you can check both:

- ☐ The `{name}` about to be interpolated is the **exact value that passed the Step 2 allowlist** (`^[A-Za-z0-9][A-Za-z0-9_-]*$`) — not a raw, re-edited, or user-echoed string. If it never passed validation, go back to Step 2.
- ☐ `{template}` is one of the CLI's advertised options from Step 1.
- ☐ No `{name}/` directory already exists in the current working directory — the generate would fail (or risk clobbering an existing project) if it does. Check with `[ -e "{name}" ]` first; if it exists, don't overwrite: tell the user and go back to Step 2 for a different name.

Run in the current working directory:

```bash
sf template generate project -t {template} -n "{name}"
```

This creates a new `{name}/` directory under the current working directory. (`sf project generate` is the deprecated alias for this command — prefer `template generate project`.) No flatten step is needed — unlike a generate-into-an-existing-dir flow, this creates a fresh `{name}/` whose `sfdx-project.json` is already at the root the session will relocate into.

**UI-bundle templates carry npm dependencies — but do NOT install them for the user.** A React/Angular starter isn't runnable (preview/build/lint fail) until its npm deps are present, and there are **multiple** `package.json` files — the project root and each UI bundle — each needing its own install. First-run install is the heavy step (multi-minute) and obvious through the latency, so it's a decision the developer should make explicitly — not something this skill runs unasked. Do **not** run `npm install` yourself. Instead, when `{template}` is a UI-bundle one (`react*`/`angular*`), tell the user in the closing message that deps aren't installed yet and hand them the commands to run when they're ready (see the UI-bundle pointer in the Closing Message).

## Step 4: Relocate the Session Into the New Project

Modern Claude Code (v2.1.169+) can move the current session into the new directory in place — no new terminal, no relaunch, conversation history preserved. Tell the user to run:

```text
/cd {name}
```

This relocates the session: the new directory's `CLAUDE.md` is loaded, project storage moves there (so `--resume`/`--continue` find it), and the cwd becomes the project root, so all remaining `sf` commands run as plain `sf ...` with no path prefix.

`/cd` is a client-side move: it fires no hook and gives you no turn, so the session goes **quiet** the instant they run it — expected, not a hang. But it also means the message in which you hand them `/cd` is your last word until they speak again, so that message MUST end with an affordance telling them how to resume. Close it with a line like:

> Once you're in, just say **"what's next"** (or "connect an org") and I'll pick up from there.

Saying "what's next" re-engages this session and paints the journey nudge, which points at the next step (authenticating an org). Never imply the session will continue on its own after `/cd` — it won't.

When they re-engage, confirm the move in one short line (e.g. "You're in {name} now.") and continue to Step 5. Do **not** run `sf-context detect` or `check-tools` to "re-surface" the banner: `detect` invoked as a tool prints the raw hook JSON (not a rendered banner), and the plugin already surfaces the banner on its own — it shows the HEADLESS identity once per session (at the user's first Salesforce ask, at session start, or on their first orientation question), and paints the journey nudge whenever they ask "where am I" / "what's next". A dev-environment health check is available on demand via `/salesforce-development:setup`.

**Fallback for older Claude Code (before v2.1.169):** `/cd` reports `Unknown command`. In that case the user must relaunch in the new directory instead:

```bash
cd "{name}" && claude
```

The `salesforce-development` plugin is installed globally (via the marketplace), so a fresh session in the new directory loads it automatically and fires SessionStart — the banner and health check appear on their own, no manual `sf-context` calls needed. The remaining steps below then run from inside the project.

## Step 5: Authenticate to an Org

Authenticate the org this project will deploy to:

```bash
sf org login web --alias {alias}
```

- Prompt the user for an `--alias` so later steps can reference the org by name.
- For a **sandbox**, add `--instance-url https://test.salesforce.com`.
- For **production**, omit `--instance-url` (defaults to login.salesforce.com).

If the user already has the org authenticated, skip the login and just collect the existing alias.

## Step 6: Set as Default Org

Set the freshly authenticated org as the project's default target:

```bash
sf config set target-org {alias}
```

## Step 7: Ensure Source Tracking Is Enabled

Check whether source tracking works against the org using a deploy preview (the lightest read-only source-tracking probe):

```bash
sf project deploy preview --target-org {alias} --json
```

If this fails with an error mentioning source tracking not supported or not enabled, offer to enable it:

```bash
sf org enable tracking --target-org {alias}
```

Confirm with the user before running the enable command.

## Closing Message

Once all steps are complete, tell the user:

```text
Your project is ready! Here's what was set up:

  ✅ Project generated: {name}/
  ✅ Session relocated into {name}/ (via /cd)
  ✅ Default org: {alias}
  ✅ Source tracking: enabled (or status)

You're already working inside the new project — this same session moved
here with /cd, so just keep going. Run /salesforce-development:setup
anytime to re-check your dev environment.
```

If the user took the older-version fallback (relaunched with `cd {name} && claude` instead of `/cd`), they're in a fresh session in the project and the SessionStart banner already walked them through the environment — point them to `/salesforce-development:setup` to re-check tools.

For a **UI-bundle** project, the scaffold is done but its npm dependencies are **not installed** — that's the developer's call, not something this skill runs (first-run install is a heavy, multi-minute step). Tell the user their app needs its deps before it can preview/build/lint, and hand them the commands to run from inside the project when they're ready:

```bash
npm install                                        # project root
for b in force-app/main/default/uiBundles/*/; do   # each UI bundle
  [ -f "$b/package.json" ] && ( cd "$b" && npm install )
done
```

Then add a line pointing at the follow-on development skills. **Make the pointer framework-specific**, because the front-end build skill is React-only:

- **React** (`react*` templates) → `experience-ui-bundle-frontend-generate` builds pages/components (it's React/TypeScript-specific — shadcn/ui, react-router, `appLayout.tsx`/`routes.tsx`), and `experience-ui-bundle-deploy` ships the app.
- **Angular** (`angular*` templates) → there is **no** Angular front-end skill, so do **NOT** point at `experience-ui-bundle-frontend-generate`: its precondition requires a React `appLayout.tsx`/`routes.tsx`/`src/components/ui/` and will reject an Angular bundle. Build it out from the Angular starter's own `README`/toolchain; `experience-ui-bundle-deploy` still ships it (deploy is framework-agnostic).

Either way, those skills live in the `experience-react`/`experience-lwc` plugins; if the user doesn't have them, that's for *building* the app, not scaffolding it — the project they now have is complete and deployable as-is.

## Rules

- Run the steps in order; confirm before any environment-changing action (login, set-default, enable tracking).
- The plugin's MCP servers come from the installed plugin, not the project — do NOT create or copy a `.mcp.json` into the new project (the plugin's config uses `${CLAUDE_PLUGIN_ROOT}`, which does not resolve in a project-level file).
- Prefer `/cd {name}` to relocate the session in place (Claude Code v2.1.169+) — a skill can't relocate the session on the user's behalf, so instruct the user to run it. Only fall back to `cd {name} && claude` (relaunch) when `/cd` reports `Unknown command` on an older build.
- The message that hands the user `/cd {name}` is your last turn until they speak again (`/cd` fires no hook), so it MUST end with a resume affordance — e.g. 'once you're in, just say "what's next".' Never promise the session will connect an org or continue on its own after `/cd`; it stays silent until the user re-engages.
- After `/cd`, do NOT run `sf-context detect` or `check-tools` to "show" the banner — `detect` as a tool prints raw JSON, and the plugin surfaces the banner itself (once per session; the journey nudge on orientation questions). Just confirm the move in one line and continue. Health is available on demand via `/salesforce-development:setup`.
- For sandbox login, `--instance-url https://test.salesforce.com` is REQUIRED (the CLI default points at production).
- NEVER store or display access tokens.
- The project name is user input that flows into shell commands. Validate it against `^[A-Za-z0-9][A-Za-z0-9_-]*$` and reject-and-re-prompt on anything else BEFORE using it, and quote `"{name}"` in every command (including the `cd {name} && claude` fallback). A name like `proj;rm -rf ~` must never be interpolated raw — validation is the guard, quoting is the backstop.
- For an EXISTING project that just needs tooling validated, use `platform-environment-validate` (or `/salesforce-development:setup`); for org auth on an existing project, use `/salesforce-development:login`.
- This skill owns **greenfield project creation** for every template, React/Angular included — a from-scratch "create a new project" ask, set up end-to-end (scaffold, relocate, connect an org, enable tracking). Do NOT hand that initial scaffold off to another plugin. Scaffold here — but never run `npm install` for the user; installing a UI bundle's deps is the developer's explicit call (hand them the commands in the closing message). Then point the user at the `experience-ui-bundle-*` skills to *build and deploy* the UI app. The one boundary: when the UI-bundle scaffold is just one **composed step** of building out a UI-bundle app (driven by `experience-ui-bundle-app-coordinate`, no full project setup wanted), that's `experience-ui-bundle-project-generate`'s job, not ours — the two skills' descriptions carry the reciprocal DO NOT TRIGGER. Building/editing an existing UI-bundle app is always theirs; greenfield project creation is ours.
