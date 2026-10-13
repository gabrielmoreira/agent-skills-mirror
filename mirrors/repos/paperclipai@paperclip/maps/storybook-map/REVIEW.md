# Initial Storybook review — 2026-10-12

Source baseline: `f0e12c851971a21f7aadf0835b016bfaf2067314`.
Scope: complete source inventory and initial classification, with targeted source
comparison and browser checks. This is not full state parity, full interaction
coverage, or production acceptance for all stories.

## Inventory and organization

There is one Storybook, already centralized under `ui/storybook/`. At the initial
baseline, its 223 story files were split between 176 files at the stories root and
47 nested files, with 51 top-level sidebar groups. The initial pass recorded
product meaning, provenance, and review status before changing that organization.
The follow-up organization pass below moves the files and sidebar together.

The downstream catalog gives each file a primary feature home and related stable
capability IDs. The generated index includes all 171 upstream capabilities across
35 feature areas. The existing Overview story now provides searchable feature
navigation into the actual built story index. The initial pass kept sidebar titles
stable; the follow-up uses explicit IDs to preserve links while changing titles.

| Dimension | Initial classification |
| --- | --- |
| Product alignment | 18 current subjects, 4 proposals, 5 historical suites, 8 mixed suites, 188 requiring deeper parity review |
| Rendered subject | 199 production, 8 prototype, 11 mixed, 5 guides |
| Data boundary | 217 fixture-based, 1 separate fixture server, 5 static guides |

A production subject can have unreviewed state parity. A current subject can still
have untested loading, error, permission, or backend behavior. The catalog's notes
and source references qualify these labels; none are a substitute for live proof.

## Corrections and retained history

- **Question dismissal and send:** the local interaction-above-composer harness
  kept a pending badge for dismissed questions and left the question open after
  a normal send. Production `TaskChatThread` excludes questions from
  `pendingReminderInputs` and dismisses the selected question on send. The harness
  now matches those rules. Added question-dismiss and confirmation-reopen cases;
  corrected the send case's stale editor selector. The story still does not prove
  persisted dismissal or history behavior.
- **Fast response helpers:** `empty`, `configured`, and `result` were exported
  fixtures which Storybook also treated as stories. Their IDs collided with
  `Empty`, `Configured`, and `Result`. Explicit exclusion removes the false exports
  while retaining the real stories and imported fixtures. Browser review also
  exposed a missing explicit `onConnectionChange` spy after the production view
  began calling it on mount; added that fixture callback.
- **Chat provenance:** the main chat wrapper combines production conversation/task
  pages with a local landing view. The separate first-created-agent chat-entry
  design is historical; current primary-agent examples are its replacement.
- **Historical designs retained:** GitHub chat, old agent onboarding, connect-model
  tiles, paused composer, and chat-entry remain available with their purpose and
  replacement references. Local proposals are labeled rather than deleted.
- **Prototype folder is not a verdict:** some files re-export production subjects;
  others implement local compositions. Static import traversal found no obvious
  orphan prototype TS/TSX module. This is not proof that each is still useful.
- **Contributor guidance:** replaced the old Overview's manual coverage claims,
  corrected the interaction-authoring skill's obsolete story path, and updated the
  prototype README's catalog source count to match the shipped five sources.

## Verification

Environment: local macOS, headless Chromium, built Storybook 10.6.0, fixture data.
The following nine `play` cases reached Storybook's `storyFinished: success` event
without a browser page exception. These results establish story interactions only.

| Story ID | Subject / assertion |
| --- | --- |
| `composer-interaction-above-composer--ask-user-questions-and-send` | Production card/composer in local harness; normal send dismisses question without a pending badge |
| `composer-interaction-above-composer--dismiss-question-without-pending-badge` | Production card/composer; dismiss leaves editable composer without pending badge |
| `composer-interaction-above-composer--dismiss-confirmation-keeps-pending-badge` | Production card/composer; dismiss retains confirmation badge and reopening works |
| `composer-new-task--empty` | Production composer wrapper; existing play assertions |
| `design-explorations-agent-chat-sidebar-components--add-and-reopen-chat` | Production sidebar; fixture add/reopen assertions |
| `assistant-connections-consent--choose-organization` | Production consent surface; fixture organization selection assertions |
| `historical-github-chat-prototypes--standard-trust-warning` | Historical prototype; existing trust-warning assertions, not current GitHub acceptance |
| `design-previews-recovery-notice--retry-request-failed` | Production recovery notice; fixture failure-state assertions |
| `composer-mobile-assignee-picker--picker-open` | Production picker; existing open-picker assertions |

Additional manual browser checks passed: search the guide for `steering/queue`,
follow its link to the real queued-message story, dismiss a question, then reload
and verify that the fixture resets to an open question. Screenshots were inspected
locally and are not committed as new regression baselines.

Built-index comparison: all 2,208 prior story IDs remain; only the two new dismissal
regressions were added (2,210 total). Catalog validation, eight checker tests,
feature-map validation, both skill validators, token gates, workspace typecheck,
and workspace build passed. Fast-response settings `empty`, `configured`, and
`result` subsequently reached `storyFinished: success` with no page exceptions
following the explicit callback fix. These three cases are render checks, not save
or backend-persistence tests. The UI Vitest project passed all 8,176 tests in 728
files. The full `pnpm test:run` reported a 15-second timeout in the unchanged backend
case `connects advertised Workspace gmail.read without mutating definitions in
authenticated`. That exact case passed standalone without changing expectations
or timeouts. The remaining broad run was stopped after this failure; a complete
repository suite pass is not established.

Automated review found missing directly rendered subjects in the initial dependency
list. Expanded the catalog across affected suites, including relative production
imports, all direct non-primitive subjects in local wrappers, and the primitives
that foundation stories demonstrate. Explanatory review guides keep their separate
guide classification. This records change detection, not new parity
acceptance. Added a real CSF parser regression for nested discovery, include/exclude
rules, stable explicit IDs, and play counts.

## Feature organization follow-up — 2026-10-12

Source baseline: `75bd3c977cd828d5222823850339e8204f40eb47` (parent PR #16046).
The 223 story files now live under their primary feature area in
`ui/storybook/stories/`. The sidebar uses the feature map's section and feature
labels in map order. Existing scenario groups remain below those labels.
Overview and shared Foundations have dedicated homes. Areas without stories do
not get empty sidebar groups; their gaps remain visible in the catalog.

Nineteen supporting files moved to `ui/storybook/support/`, including fixtures,
shared wrappers, guide READMEs, an HTML fixture, and a fixture test. Relative imports,
active documentation, catalog sources, and replacement references follow the
moves. Classification and review scope did not change. The upstream feature map
and its skill are unchanged.

Every suite now has an explicit meta ID, recorded as `stableId` in the catalog.
The built index comparison preserved all 2,210 story IDs, the single docs ID, and
all entry names. No story was removed or added. Catalog validation checks primary
feature folders, sidebar prefixes, and stable meta IDs; its nine tests passed.

The Storybook build, UI typecheck, all 8,176 UI tests in 728 files, token gates,
map checks, and the maintenance-skill validator passed. A source comparison found
only changed meta titles/IDs, rebased relative references, and updated fixture
path text in story files. The full repository suite was not repeated for these
file moves; the prior full-suite limitation above still applies.

Local Chromium verified the sidebar's section/feature order, rendered the guide,
searched `steering/queue`, and followed its link to the unchanged
`composer-steering-and-queued-messages--queued-while-running` ID. The nine play
cases listed above and `fast-responses-01-settings--empty` all reached
`storyFinished: success` without page exceptions after relocation. This is a
sample of interactions and rendering, not execution of all 2,210 stories.
The fixture-server story and visual-baseline comparisons remain untested for the
reasons below. The owned static preview was left running for the requested test-drive.

## Remaining review work

1. Review the 188 unreviewed suites by capability and production subject. Compare
   state transitions, payloads, errors, gates, and reset behavior before promoting
   a suite. Start with large route wrappers and shared fixture dependencies.
2. Shared preview mocks can fall through to the original fetch; some route harnesses
   return empty arrays for unmatched APIs. These can hide missing fixtures. Audit
   affected endpoints per feature rather than treating a render as API coverage.
3. The managed-accounts test-drive story needs the separately owned local API/DB
   fixture at port 4310. Its upstream providers are simulated. It was not exercised
   against an unknown existing service.
4. Screenshot comparison is blocked: the existing baseline manifest has zero
   snapshots and no published archive. Keep using the established Linux baseline
   workflow when its baseline is published. Do not bless new baselines as part of
   catalog cleanup.
5. Review fingerprints track declared sources, including feature recipes and local
   support; they do not traverse every production dependency. Add missing subjects
   when a review discovers them. Shared setup changes require reviewing callers.

Use `maintain-storybook` to correct drift and `review-storybook` to record separate
source, render, interaction, visual-comparison, and production evidence. Both skills
consume the feature map; neither changes its upstream contract.

## Task workspace reconciliation — 2026-10-12

Scope: the 26 declared-source entries affected by task-workspace work at
`88b1d3a2`, compared with master `dabb8c5daf`, including subsequent comment-only
cleanup and the fixture corrections below. This is a bounded source review,
not a new review of all Storybook states. Reconciliation onto `b5046ec022`
preserves its new feature folders, sidebar titles and explicit stable IDs, along
with the existing exports, classification and simulation boundaries. Shared GitHub
fixtures now live under `ui/storybook/support/github-bot-management/`.

Twenty-one entries changed only through the expanded chat/workspace recipes.
Their setup, identity, browser, artifact, picker and service examples are retained;
the new recipe requirements do not become covered merely because they reference
the same capability. Five entries also depend on changed production subjects:

| Story file under `ui/storybook/stories/` | Source review and remaining scope |
| --- | --- |
| `chat-channels/chat-management/chat-management.stories.tsx` | Mounted endpoint includes connection/destination defaults. Added the missing selectable-workspace fixture response; existing endpoint PATCH and resource PUT retain defaults. No browser save, error, reload or inheritance proof in this pass. |
| `chat-channels/github-bot-management/management.stories.tsx` | Mounted endpoint/repository editors include defaults. Fixed the endpoint mock to persist PATCH values instead of returning the original endpoint. Resource PUT already distinguishes omitted, null and concrete values. Project/workspace choices are intentionally empty fixtures. |
| `chat-channels/imessage-photon.stories.tsx` | Existing scenarios mount setup/access and simulate task conversations. They do not exercise the newly added settings editor or its workspace-choice request. Kept unreviewed rather than claiming settings coverage. |
| `projects/projects-goals-workspaces.stories.tsx` | Existing project-bound summaries still match the rendered components. New nullable project references and runtime invalidation branches have no projectless story scenario here. |
| `workspaces/workspace-runtime-provisioning.stories.tsx` | The demonstrated status subcomponent is unchanged. Its local context row does not prove the full detail page's new projectless behavior. |

The three endpoint-management entries now declare `ChatExecutionDefaults` and its
API clients as review dependencies. AgentMail settings still demonstrates only
the inbox subsection, not the surrounding endpoint defaults. Historical GitHub
designs remain historical; existing unreviewed entries remain unreviewed. None of
these fixture examples establishes source authorization, retained file privacy,
pending workspace selection, sandbox admission or existing-conversation continuity.

Executed: the GitHub fixture's two Vitest cases passed, including default save,
subsequent GET, omitted-value preservation, explicit null clearing and fresh-mount
reset. After the folder rebase, both fixture tests and all nine catalog checker
tests passed again; token gates passed before the path-only reconciliation. After the final
source freeze, only the 26 reviewed fingerprints were refreshed; catalog validation
passed for all 223 files and all 2,210 source-parsed story IDs were unchanged.
All 223 upstream file paths, explicit stable IDs and sidebar titles were preserved.
Not run in this pass: Storybook build, browser rendering or `play`, screenshot
comparisons, provider calls and live production acceptance. No new visual
baselines were accepted. Fixture tests are boundary simulations, not server
persistence or permission tests.

## Workspace safety recipe follow-up — 2026-10-12

Reviewed the twelve entries that depend on the workspace feature recipe: browser-use activity/footer/page, the three HTML-artifact suites, project execution strategy and project workspace summaries, searchable selection, workspace files, runtime provisioning and service controls. Their production subjects, fixtures, feature folders, sidebar titles and stable IDs are unchanged. The recipe now requires prospective child boundary checks, safe low-trust reopening, and coherent returned checkpoint ancestry. These backend safety contracts are not exercised by those fixtures. Each entry remains unreviewed for full production parity. Only the reviewed recipe fingerprints were refreshed; no browser render, play, screenshot baseline or production acceptance was run for this follow-up.


## Remote provisioning recipe follow-up — 2026-10-13

Reviewed the same twelve workspace-recipe-dependent entries after extending the controller-provisioning boundary to standard-trust sandbox and SSH selections. Their components, fixtures and stable IDs are unchanged. Project strategy stories demonstrate configuration fields with environment selection disabled; runtime provisioning stories demonstrate status values with a no-operation log handler. Browser, artifact, file and service-control fixtures do not execute source scripts or prove admission placement. The new recipe requires controller marker denial independent of source write grants while copying and dispatch remain available, including local copy-only selections, retained deny-only metadata and closed-worktree reopening. Implicit trusted local defaults remain separate positive controls. All twelve entries retain their unreviewed production classification. Refreshed only these recipe fingerprints after this source review; no browser render, play, screenshot, Storybook build or live runtime qualification is claimed.

## Default-source recipe follow-up — 2026-10-13

Reviewed the twelve unchanged workspace recipe subjects and fixtures after correcting implicit default selection. Task creation and controller classification now share configured-policy, primary, creation-time and ID precedence. Explicit choices and retained denial markers still suppress controller hooks. Project strategy fixtures show configuration, while runtime status and file/browser/artifact/service fixtures do not execute source scripts or prove this backend ordering. Refreshed only their reviewed recipe fingerprints and retained all classifications and stable IDs. No browser render, play, screenshot, Storybook build or live runtime acceptance was performed.
