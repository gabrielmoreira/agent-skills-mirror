# OpenMotion repository guidelines

OpenMotion is a standalone npm application at the repository root. Run commands here with the Node version pinned in `.github/workflows/ci.yml`. Preserve `package-lock.json` and `scripts/runtime-lock.json`; do not introduce workspace-only dependencies. Follow the [migration guide](docs/repository-migration.md), keep user data and credentials outside the checkout, and preserve third-party licenses.

## Local validation

Before publishing a branch, select local checks for the changed boundary. Run `npm ci` when dependencies or lockfiles change, or installed dependencies are missing or stale; otherwise reuse the existing installation.

- Runtime or Studio changes: run `npm run check`, `npm run typecheck:studio`, `npm run build:studio` and affected deterministic tests.
- Skill, contract, installer or distribution changes: run the affected deterministic and packaging/installation checks.
- Prose-only changes that do not alter those boundaries: check links and run `git diff --check`; no dependency reinstall or Studio build is required.

PR CI keeps repository policy, source scanning and release controls for every change. Only the explicit presentation-document allowlist skips Studio, rendering and package checks when installation sections and code blocks are unchanged; Skills, installation guides, examples and unknown paths retain the full gate. Maintainability analysis runs for code and configuration changes. Distinguish CI, target-machine installation, model creation and human content acceptance. This feature migration must not merge or publish packages unless separately authorized.

## Repository collaboration instructions

Keep persistent user instructions for repository work in this file, and keep `CLAUDE.md` aligned with this shared source so every Agent follows the same rules.

1. All commit messages must be in English, including both the subject and body, as well as merge and revert messages.
2. All repository collaboration content you create or update must be in English: issue and pull request titles and descriptions, comments, review summaries, discussions, and release notes. This applies even when the user's request is in another language.
3. Before committing or submitting repository content, verify that it follows these English-language requirements.
4. Branch new work from the latest `main` and target all pull requests at `main`. Merge reviewed changes directly into `main` when authorized; do not use `feature/motion` as an intermediate integration branch.

## Repository PR review follow-up

For repository PR work, follow the [contributor review checklist](CONTRIBUTING.md#follow-through-on-review). Creating a PR or pushing a fix does not finish an active review task.

1. Read the live PR head, unresolved threads, latest reviews, CI and mergeability before acting. Do not rely on a previous commit's status.
2. Verify each review claim. Fix real issues, run boundary-appropriate validation and push follow-up commits while preserving shared history. For incorrect feedback, reply with concrete code or reproduction evidence.
3. Reply to each addressed thread with the commit and checks, then resolve it when permitted. Keep unanswered or disputed feedback visible and report what remains; do not dismiss change requests or close discussions merely to unblock merging.
4. Address failing required CI and conflicts. Use an isolated worktree when the active checkout contains unrelated work. After a fix push, re-request prior reviewers who have not reviewed the new head when permitted; otherwise report pending re-review. Do not add or ping unrelated people to solicit a merge.
5. Re-read the live state before reporting. Summarize what was fixed, unresolved threads, CI and conflicts, including pending re-review or an external blocker. When waiting, state what is pending rather than claiming completion.

Merge and publication authorization remain separate from review cleanup. These steps do not grant permission to merge, bypass required checks or publish a package.

### Automatic waiting during PR follow-up

During an ongoing PR follow-up task, use the current client's available monitoring or waiting tools to continue when CI or reviews change:

- **Claude Code:** when this session exposes `Monitor`, prefer it to watch the PR and resume the review loop on relevant changes. Use persistent monitoring only as supported by the actual tool; inspect its schema rather than assuming every client/version has it.
- **Codex, OpenCode and other clients:** prefer a native monitor/wait capability when exposed. Otherwise keep a lightweight shell wait active in the current agent session, sampling PR metadata about every 30 seconds and returning when the state changes or its wait deadline is reached. Re-arm the wait while follow-up remains active.
- Compare the head/base commits, review threads (including replies/edits and resolution), latest reviews and mergeability. Fold checks into one CI phase (`pending`, `passed`, `failed` or `missing`) so each individual green job does not restart the review pass. Wake the Agent for a changed state, then verify the actual feedback/check before acting.
- Stop when the requested follow-up is complete, the PR closes/merges, the user stops it or an external blocker needs the user. Report the exact remaining state. An approved PR with required checks green still needs existing merge authorization.
- A session wait does not survive closing the client. Only promise unattended follow-up after session closure when a durable runner has actually been configured for that scope; otherwise leave the PR URL, head, pending items and resume instructions for the next session.

## Repository contribution Skills

Source-checkout contributor Skills live under `.agents/skills/`. When adding or maintaining a built-in BYOK media provider, read `.agents/skills/add-byok-provider/SKILL.md` in this checkout. It covers provider research, implementation, references and verification. These repository-local Skills are excluded from application/plugin distribution and host installation; root `skills/` continues to hold product workflows. Installed product copies may not contain `.agents/skills/`. Other Agents following `CLAUDE.md` use this same source-checkout guidance.

When applying or migrating an existing shared control in Studio, follow the [ODUI apply Skill](.agents/skills/odui-apply/SKILL.md).
For Open Design UI work, choose the repository-local Skill by intent. Use [odui-dev](.agents/skills/odui-dev/SKILL.md) for the local catalogue and live preview, [odui-build](.agents/skills/odui-build/SKILL.md) to create or evolve a component, [odui-apply](.agents/skills/odui-apply/SKILL.md) to adopt an existing component in Studio, and [odui-check](.agents/skills/odui-check/SKILL.md) before review. The component registry and component guide remain the shared source of truth.

## Shared design system — required for every Agent

All Agents must use [packages/design-system](packages/design-system/README.md) for interface styling. Read that package's integration and change rules before creating or changing CSS, component appearance, themes, icons, fonts, loading states or brand assets. [docs/design-system.md](docs/design-system.md) describes the product integration; [brand guidance](packages/design-system/brand/BRANDKIT.md) governs public brand material.

1. **One maintained source.** Define shared visual decisions in `packages/design-system`: `tokens.json` owns theme values and Studio aliases; package styles own reusable controls, materials and states; package assets own icons, fonts and brand artwork. Never create a second palette, font stack or copied component recipe inside a feature module.
2. **Reference, do not duplicate.** Application modules consume the package's CSS entry points, semantic variables, generated utilities and asset exports. Use existing roles for colors, typography, spacing, radii, shadows and motion. If a needed reusable role or recipe is missing, extend the design system first and then reference it from consumers. Do not introduce literal interface colors, fallback palettes or arbitrary visual values to bypass it.
3. **Keep the boundary useful.** Features retain their layout, content, interactions and measured geometry. Domain values such as timeline coordinates, user-selected artwork colors, image pixels and authored video styles are not application-theme tokens. Do not theme project iframes, templates or third-party artwork as a side effect of changing the editor.
4. **Change the source, then generate.** Run `npm run design:tokens` after changing token values or mirrored brand assets. Do not hand-edit generated CSS or compatibility mirrors. Old entry paths may forward to the package but must not become independent implementations. Preserve upstream attribution and font licenses.
5. **Verify propagation.** For shared visual changes, check the affected surfaces together, including both themes, startup/loading, controls and dialogs, template browsing and narrow layouts where applicable. Run `npm run design:check` and the boundary-appropriate validation above. Keep automated checks, browser inspection and human visual acceptance distinct.
6. **Keep the visual workbench independent.** `npm run design:dev` launches only the package-owned workbench. Its UI and Node service may depend on design-system sources and Node built-ins, never Studio, application services, project data or business modules. UI saves and Agent edits share `tokens.json`; downstream modules consume the generated system through their normal build/refresh. Run `npm run design:test` for workbench changes.
7. **Keep every Agent aligned.** `AGENTS.md` is authoritative; `CLAUDE.md` points to this section. Include this requirement in delegated task context and code reviews. A feature-local style exception must have a concrete domain reason; an older hard-coded value elsewhere is not permission to add another one.

The package is a local source module within the standalone root npm application. Do not add workspace-only dependencies or publish it without separate authorization.

## README writing and acknowledgements

When creating or updating any README, including alternative drafts and translations, describe OpenMotion's own capabilities, workflows and the meaning of each example. Do not introduce other products as comparisons, inspiration or source labels in the main narrative, headings, feature descriptions or showcase copy. Avoid wording such as "From MotionGit", "inspired by Hypit" or "the alternative to ...".

Consolidate references to other products, upstream origins, comparisons and source acknowledgements in the final **Acknowledgements** section. Preserve required licenses, copyright notices and detailed provenance in their source files, and link them from that section. Describe external examples accurately without presenting them as OpenMotion-generated results.

Keep technical identifiers needed for setup, supported agent/model names and explicitly requested example brand names accurate; these factual labels are not invitations to add product comparisons or inspiration commentary. Before finishing a README edit, check that product-reference commentary appears only in the final acknowledgements.

## UI design system and interaction feedback

Check the [component library registry and contribution guide](packages/design-system/components/README.md) before adding a shared Studio control. Use the listed source import and update the live example when its recommended usage or behavior changes.

Record an exercised Studio consumer and an explicit adoption decision for each registered control. Follow the [contribution steps](packages/design-system/components/README.md#contribute-a-control) when deciding whether to enforce reuse.

Use the shared Button, IconButton or Slider for new Studio actions and range controls. The design check blocks native `<button>` and `<input type="range">` above the per-file legacy baseline. Lower the baseline when migrating a legacy control.

Follow [the shared design system](docs/design-system.md#interaction-and-feedback-contract) for all new or changed product UI. Reuse its components and semantic tokens in both light and dark themes; do not introduce page-specific palettes or native-looking replacement controls.

- Transient action feedback, including copy, download, save and failure notices, must use floating Toasts through the shared feedback layer. Never insert these messages below buttons or into normal document flow: showing or dismissing feedback must not move content or consume layout space.
- Reuse `useToast` and `StudioToastViewport`; native dialogs must not cover or make the feedback inert. Notices must not steal focus, block the page or create another modal. Coalesce repeated feedback and respect reduced motion.
- Use anchored, non-modal dropdowns for filtering and sorting, with immediate quick filters, or grouped draft selections using category tabs, a live match count and an in-panel Apply action. Preserve individually removable selections and clear-current/clear-all actions. Do not add a confirmation dialog for routine filtering or copying an Agent instruction.
- Keep hover surfaces rounded and inset with consistent padding, align icons and chevrons, and use one focus treatment per composite control while preserving visible keyboard focus.
- Use opaque, solid theme surfaces for product UI, including menus, Popovers, tooltips, dialogs and floating controls. Match the existing shared controls; do not add frosted glass, translucent content backgrounds or background blur (`backdrop-filter`). Fix shared material recipes in `packages/design-system` rather than adding feature-local overrides. A modal scrim may dim the page with a uniform tint without blur; authored video and imported artwork remain independent content.
- Reserve geometry for slow content with shared Skeletons and poster fallbacks. Resource errors replace their reserved content and provide recovery; do not leave indefinite loading after a known failure. Stop offscreen/background video work.
- Verify actual opened menus, Toasts, loading/error states and narrow layouts in both themes. A component rendered in source is not evidence that it layers or behaves correctly in the browser.

## Core capabilities and shared APIs

Every new or extended core product capability must be callable by external Agents through the public MCP contract. This includes asset creation and management, model execution, references and versions, project import and editing, preview and export. Keep operations usable independently so external Agents can compose them into their own workflows.

1. **One capability implementation.** Define atomic operations in shared domain services with maintained inputs, outputs and error semantics. MCP adapters and application API routes call that same implementation and use the same persisted data, jobs and provider integrations.
2. **Product interfaces compose the same operations.** Build controls, workflows and in-app Agent experiences around developer and user needs. They invoke the same API or MCP capabilities exposed to external callers. HTTP and MCP may use different transport adapters, including browser file upload, while converging on the same validation and business execution. Keep presentation state in the UI and business rules in the shared service.
3. **Preserve operation semantics across entry points.** Carry explicit workspace/project/asset identities, pinned references and versions, request deduplication, conflict protection, job status and cancellation through each applicable entry point. Reuse the existing credential boundary and native editing/save authority; do not create parallel state or execution paths for interface actions.
4. **Maintain both access paths together.** When adding or changing a capability, update its public schema/discovery, applicable UI consumer, MCP onboarding and documentation in the same change. Verify equivalent results and relevant failure/conflict behavior through the affected adapters. Distinguish implemented coverage from planned capabilities and document any remaining gap explicitly.

`AGENTS.md` owns this requirement; `CLAUDE.md` links here. Apply it when designing, implementing and reviewing product capabilities.

## Product architecture review

For every change, review the entire [product architecture](docs/product/architecture.md) and decide whether it still accurately describes the product. Consider positioning, core user flows, module responsibilities, dependencies, data and API boundaries, implemented capabilities, and current limitations together.

Update the architecture only when the change makes it incomplete, inaccurate, or internally inconsistent. Keep the document coherent as a whole, and adjust related usage or technical documentation only where needed for consistency. If the architecture remains accurate, leave it unchanged; documentation edits and per-change records are not required for every commit or PR.

Use the [documentation index](docs/README.md) for related topics. Distinguish implemented behavior, confirmed direction, hypotheses, and candidate designs. Preserve useful rationale and verification boundaries without inventing evidence. Check links and source references when editing documentation.

`AGENTS.md` is the shared source for all Agents; keep the `CLAUDE.md` entry aligned when these guidelines change. Distributable plugins include both entries and the approved documentation.

## Video production entry points

Choose the entry for the current intent directly. Each Skill's description states its scope, and [Skill routing](docs/skills.md#职责与入口) summarises the five entries. [openmotion-production](skills/openmotion-production/SKILL.md) handles scoped engineering under established creative decisions, preview, technical checks, troubleshooting and export; its start resource keeps short navigation and is not a mandatory router.

A directly selected specialist reads shared context and continues; do not bounce back to the production start. Small edits, audio-only changes, review-only and export-only requests resume their affected scope. Keep existing decisions and locked content. Repository development and documentation do not trigger video production.

Phase one retains eighteen registered domain openmotion_ names (including the openmotion_assets compatibility alias) for non-App clients; negotiated MCP Apps connections additionally discover the read-only final-video presentation Tool (template recommendations remain an independent optional extension), defined in [the contract](docs/mcp-phase1-tools.md). MCP-only clients read the same guidance through resources/list and resources/read, beginning at openmotion://workflow/production/start or the already-selected specialist. The pinned engine guide is openmotion://engine/SKILL.md. The workflow-reading Tool is internal compatibility only. The supporting [openmotion-media](skills/openmotion-media/SKILL.md) Skill (`openmotion://workflow/media/start`) and its provider references describe BYOK media generation; the five creative routes remain unchanged. Follow conditional references and reuse complete document bodies. Native authoring belongs to the shared production/native guide. Technical export verification, visual quality and actual playback remain separate. See [Skill routing](docs/skills.md).


## MCP onboarding and capability maintenance

The Studio **MCP · Connect Agent** page is the maintained product entry for connecting local Agents and discovering OpenMotion capabilities. Its plug icon is distinct from the model-provider brain icon. Keep `studio/src/motion/McpConnectionPage.tsx`, `mcpCapabilities.ts`, their interface translations and `shared/integration.ts` aligned with the actual public contract and installation.

When changing local MCP tools, media-generation capabilities, production Skills, host adapters, template handoff or optional MCP Apps presentation, review and update this page in the same change. Cover the affected setup steps, example prompts, template actions, capability descriptions, client compatibility, limits and FAQ. Use the installation's actual transport/configuration and the shared template catalogue; do not invent a remote endpoint, universal model access, free quota or verified Agent connection. Explain image/video/music/speech discovery, provider configuration, job tracking and the separation between generated assets and composition edits where relevant. Distinguish eighteen registered domain names (one compatibility alias) from negotiated presentation extensions.

The MCP main page is the product-wide capability and usage handbook. Every new or changed MCP capability, and every user-facing scenario composed from existing MCP operations, must appear there in the same change—even when no tool is added. Maintain the entry point, purpose, copyable example, prerequisites, recovery guidance and actual limitations alongside the implementation. Reuse shared instruction builders between feature entry points and the handbook so project identity, revision protection and delivery requirements cannot drift. Keep atomic tool discovery distinct from scenario examples; add coverage for both. For platform export, maintain the Export panel and handbook together, including independent-copy editing, host-dependent content analysis, verified export and manual platform upload.

Run `tests/mcp-onboarding.test.ts` to verify public-tool coverage and the affected Studio connection/model tests. Check opened client tabs, copy Toasts, manual configuration, loading/recovery, template handoff and narrow layouts in both themes. Workspace reachability, native host connection, paid media generation and human visual acceptance remain separate evidence. `CLAUDE.md` points to these shared requirements.

## Template production and reuse

For changes under `library/templates/catalog/`, follow [the contributor workflow](docs/template-repository.md#contributor-loop). Commit editable project source under the template's `source/` directory, refresh `source/manifest.json`, and keep `template.json.entry.files` paths, byte lengths and SHA-256 hashes aligned. Repository and hosted project files do not require `r.open-design.ai` URLs, a ZIP upload or a new `sourceArchive`; do not make those a contribution or test prerequisite. Existing CMS URLs remain migration inputs, and CMS-mode tests retain their separate download contract.

Local Studio/MCP read registered source files from the checkout; fetch optional LFS bytes for local validation. After final review, maintainers use **Prepare and merge PR** for media transfer and merge. After merging, the main catalog workflow publishes source objects and metadata to R2 automatically. Website CMS publication is a separate internal operation, only performed when explicitly requested. Do not ask contributors to upload revised project files or ZIPs to the old CMS service to complete a repository PR.

`openmotion-template-to-video` implements the default template route and reuses shared context/edit and managed-project revision protection. Unchanged requests are delivered by opening the template in the editor; edited content is checked by playing it in the editor preview, with native snapshots only for layout; completed video creation/content edits follow the shared final-video delivery flow; unchanged template opening and explicit draft, editor-only or review-only work do not render unless requested. `openmotion-video-to-template` separately produces a portable reusable template from a video; it does not replace ordinary video recreation. Visual acceptance belongs to the user. Repository work does not invoke production Skills.

## Candidate and publication controls

New repository installations use the source bootstrap in docs/install.md by default. Published npm application installation is optional and requires an explicit user choice; follow docs/install.md for channel and host selection. Never silently substitute npm for source or mix installations. Preserve existing installations, projects, credentials and unrelated host settings. npm remains the source dependency/build tool.

Follow [the release workflow manual](docs/release-workflows.md): one manually dispatched Motion package and release entry with prepublish and publish modes, plus snapshot-only recovery. Select `main` for all entries; other execution refs are rejected for new release work. Select `test` (default, DEV templates) or `stable` (prod templates). Blank test versions use short workflow-counter `test.N` numbering; stable requires an explicit new `MAJOR.MINOR.PATCH`. Keep full run/source identities in the records. Use candidate-install.md for local testing and keep results private. Publishing requires the explicit publish mode. Reuse an existing candidate with its exact version and run ID, or build and validate within the publishing run. Public candidates must use an exact reviewed source SHA integrated into `main`. Scan tracked source plus the outer npm tgz and inner application; preserve the positive distribution list and licenses. Keep candidate, native registry installation, real Agent creation and human acceptance evidence separate.

Publication ordering reserves the historical 0.6.x namespace and starts the active series at 0.0.1. Use the shared publication comparator for npm channel protection, guide promotion, automatic test baselines and Notes history; retain standard SemVer comparison separately. Historical versions/snapshots remain immutable, and stale historical candidates must not replace active versions. Source 0.0.1 automatically builds 0.0.2-test.N when test version is empty. Existing range dependencies/lockfiles require explicit migration; no live tags or guides change until separately authorized publication. Start new publication/recovery dispatches from the latest main after cutover; do not rerun historical control snapshots that predate this ordering policy.

Stable release descriptions follow the [changelog authoring guide](https://github.com/nexu-io/openmotion/blob/main/docs/CHANGELOG/README.md). Maintain English and Chinese Unreleased drafts, then archive the selected exact stable version before building. Candidate preparation reads only that frozen source SHA; missing copy warns and retains an automatic draft, while malformed supplied copy fails. Publication reuses sealed Notes and preserves published maintainer edits. Changelog sources stay outside application/npm/plugin distribution; never rewrite a retained candidate to add copy or infer publication from a draft.

Each publication uses its exact sealed candidate bytes. Require both macOS and Windows candidate installs and a prepared immutable template snapshot before publishing npm. Test uploads under `candidate` and stable under `stage`; both tags are public. Verify the public tarball hash before advancing `test` or `latest`, then finalize the guide, catalog and Release. The existing `motion-publish-test.yml` filename remains the npm Trusted Publisher identity for both channels. npm publication and release snapshot recovery require separate manual authorization. Main-branch template synchronization is explicitly authorized to run automatically using the existing R2 release-bucket credentials, scoped in the workflow to the final upload step; it does not publish npm, move tags or update installation guides. These are shared bucket credentials, not template-only credentials. Consumer jobs receive neither npm OIDC nor R2 credentials. Archive-only work must not publish npm, move tags or access default entries. The read-only Motion installation check can recheck an exact public test or stable version independently. Never overwrite published versions, put private template payloads/internal acceptance material into public artifacts, or infer merge/publication authorization from green CI. Real prod template, Agent and audiovisual acceptance remain release responsibilities; hosted installation checks do not establish them. Skills marketplace publication, main registration, npm trust, main cutover and repository rename remain separate operations.
