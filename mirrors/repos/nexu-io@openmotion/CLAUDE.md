# Claude Code

Read and follow [AGENTS.md](AGENTS.md) before working in this repository. It is the shared source of instructions for all Agents.

Use `CLAUDE.md` as the Claude Code instruction entry. Record future repository-rule updates here and keep them aligned with `AGENTS.md`.

## Branch workflow

Branch new work from the latest `main` and target all pull requests at `main`. Merge reviewed changes directly into `main` when authorized; do not use `feature/motion` as an intermediate integration branch.

Follow [Repository PR review follow-up](AGENTS.md#repository-pr-review-follow-up) after opening or updating a repository PR: verify feedback, fix and validate, reply and resolve, then report the live review/CI/conflict state. Keep merge and publication authorization separate.

For ongoing follow-up, use `Monitor` when this session exposes it, following [Automatic waiting during PR follow-up](AGENTS.md#automatic-waiting-during-pr-follow-up); otherwise use the documented session wait and report its lifetime.

## Interface styling

Follow the mandatory [shared design system rules](AGENTS.md#shared-design-system--required-for-every-agent) for every style-related change. Read [packages/design-system/README.md](packages/design-system/README.md), reuse its tokens, styles and assets, and extend the package before adding a missing reusable visual role. Feature modules must reference this source rather than maintain independent palettes or copied styles. Apply the same rule when delegating or reviewing work; authored video and domain geometry retain their own styling boundary.
For CI scope and local validation, follow [Local validation](AGENTS.md#local-validation), including the presentation-document allowlist and the full product-content gate.

## Repository template contributions

For repository template edits, follow [Template production and reuse](AGENTS.md#template-production-and-reuse): commit source and refresh manifests/file identities; repository/hosted files need no old CMS URL or uploaded ZIP. Maintainers use **Prepare and merge PR** after review, and main synchronization publishes hosted source automatically. Website CMS publication requires a separate explicit request.

## Candidate and publication controls

New repository installations use the source bootstrap in docs/install.md by default. Published npm application installation is optional and requires an explicit user choice; follow docs/install.md for channel and host selection. Never silently substitute npm for source or mix installations. Preserve existing installations, projects, credentials and unrelated host settings. npm remains the source dependency/build tool.

Follow [the release workflow manual](docs/release-workflows.md): separate manual candidate-build and npm-publication entries, plus snapshot-only recovery. Select `main` for all entries; other execution refs are rejected for new release work. Select `test` (default, DEV templates) or `stable` (prod templates). Blank test versions use short workflow-counter `test.N` numbering; stable requires an explicit new `MAJOR.MINOR.PATCH`. Keep full run/source identities in the records. Use candidate-install.md for local testing and keep results private. The publication operator enters the exact version and starts the manual workflow; no acceptance checkbox or independent approval environment is enabled. Public candidates must use an exact reviewed source SHA integrated into `main`. Scan tracked source plus the outer npm tgz and inner application; preserve the positive distribution list and licenses. Keep candidate, native registry installation, real Agent creation and human acceptance evidence separate.

Publication ordering reserves the historical 0.6.x namespace and starts the active series at 0.0.1. Use the shared publication comparator for npm channel protection, guide promotion, automatic test baselines and Notes history; retain standard SemVer comparison separately. Historical versions/snapshots remain immutable, and stale historical candidates must not replace active versions. Source 0.0.1 automatically builds 0.0.2-test.N when test version is empty. Existing range dependencies/lockfiles require explicit migration; no live tags or guides change until separately authorized publication. Start new publication/recovery dispatches from the latest main after cutover; do not rerun historical control snapshots that predate this ordering policy.

Stable release descriptions follow the [changelog authoring guide](https://github.com/nexu-io/openmotion/blob/main/docs/CHANGELOG/README.md). Maintain English and Chinese Unreleased drafts, then archive the selected exact stable version before building. Candidate preparation reads only that frozen source SHA; missing copy warns and retains an automatic draft, while malformed supplied copy fails. Publication reuses sealed Notes and preserves published maintainer edits. Changelog sources stay outside application/npm/plugin distribution; never rewrite a retained candidate to add copy or infer publication from a draft.

Publication uses the accepted candidate bytes, never a rebuild. Test publishes under `candidate`, promotes `test` after registry propagation, archives and updates the DEV guide, then runs non-blocking Mac/Windows cold installs. Stable publishes publicly under `stage`, requires both exact prod cold installs to pass, then promotes `latest`, archives and updates the stable guide last; it preserves `test`. A stage tag does not make the package private. The existing `motion-publish-test.yml` filename remains the npm Trusted Publisher identity for both channels. npm publication and release snapshot recovery require separate manual authorization. Main-branch template synchronization is explicitly authorized to run automatically using the existing R2 release-bucket credentials, scoped in the workflow to the final upload step; it does not publish npm, move tags or update installation guides. These are shared bucket credentials, not template-only credentials. Consumer jobs receive neither npm OIDC nor R2 credentials. Archive-only work must not publish npm, move tags or access default entries. The read-only Motion installation check can recheck an exact public test or stable version independently. Never overwrite published versions, put private template payloads/internal acceptance material into public artifacts, or infer merge/publication authorization from green CI. Real prod template, Agent and audiovisual acceptance remain release responsibilities; hosted installation checks do not establish them. Skills marketplace publication, main registration, npm trust, main cutover and repository rename remain separate operations.

## UI design system and interaction feedback

Use opaque, solid theme surfaces for product UI, including menus, Popovers, tooltips, dialogs and floating controls. Do not introduce frosted glass, translucent content backgrounds or background blur (`backdrop-filter`). Maintain this treatment in the shared design system, not feature-local overrides. Modal scrims may use a uniform tint without blur; authored video and imported artwork remain independent. The authoritative rule is in [AGENTS.md](AGENTS.md#ui-design-system-and-interaction-feedback).

Follow [the shared UI rules](AGENTS.md#ui-design-system-and-interaction-feedback) and [the design-system interaction contract](docs/design-system.md#interaction-and-feedback-contract). Transient operation results use `useToast` and `StudioToastViewport` on the floating feedback layer, including inside native dialogs; never insert success or failure notices into the content flow. Reuse semantic light/dark tokens, non-modal dropdowns (immediate quick filters; grouped draft selections with live counts and in-panel Apply), padded rounded hover states, one visible focus treatment, and shared loading/fallback geometry. Verify the actual opened states in the browser without shifting or blocking the working area.

## Product documentation

Follow the [README writing and acknowledgements rule](AGENTS.md#readme-writing-and-acknowledgements) for every README, alternative draft and translation. Keep the main narrative, headings and showcase copy focused on OpenMotion and what each example demonstrates. Put other-product comparisons, inspiration, source-product labels and upstream acknowledgements only in the final **Acknowledgements** section; do not use headings such as "From MotionGit". Preserve licenses and provenance, and keep required setup identifiers, supported agent/model names and explicitly requested example brand names accurate. Verify this placement before finishing README edits.

The design-system workbench is an independent package-owned editing surface. Keep it free of Studio and business-module imports; UI edits and Agent edits update the same design-system source. Run `npm run design:dev` to open it and `npm run design:test` for its save/conflict/independence checks.

## MCP onboarding

The MCP main page is the shared capability and usage handbook. Follow [MCP maintenance](AGENTS.md#mcp-onboarding-and-capability-maintenance) for every capability change and every scenario built from existing tools, even without a new tool. Update its entry points, examples, prerequisites, recovery and limitations in the same change; reuse shared instruction builders with feature UI and test both atomic tool coverage and scenario coverage. Platform export must remain aligned between Export and the handbook.

Follow [MCP onboarding and capability maintenance](AGENTS.md#mcp-onboarding-and-capability-maintenance). Changes to local MCP, media generation, Agent adapters, templates or optional presentation must keep the Studio connection page, capability descriptions, setup instructions and compatibility boundaries current in the same change.

## Core capabilities and shared APIs

Follow [Core capabilities and shared APIs](AGENTS.md#core-capabilities-and-shared-apis). Every new or extended core capability must support external MCP calls. Product controls and in-app Agents may compose these capabilities according to developer and user needs, using the same API or MCP operations and shared domain implementation. Preserve the same data, job, version, validation and conflict semantics across entry points; keep public discovery, applicable UI consumers, documentation and adapter verification aligned.
