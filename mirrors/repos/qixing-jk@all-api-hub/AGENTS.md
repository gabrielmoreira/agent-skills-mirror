# Repository Guidelines

## Agent skills

### Issue tracker

Issues and specs for this repo live as local Markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default canonical triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: read root `CONTEXT.md` and root `docs/adr/` when present. See `docs/agents/domain.md`.

## Project Structure & Module Organization

### Source Modules

- `src/entrypoints/`: WXT extension entrypoints for `background`, `content`, `popup`, `options`, and `sidepanel`.
- `src/features/`: feature-oriented UI modules; keep entrypoints thin and push reusable logic into features, services, hooks, or utils.
- `src/components/` and `src/components/ui/`: shared React components and UI primitives.
- `src/services/`: business logic, persistence, site adapters, and browser integration.
- `src/hooks/`, `src/contexts/`, `src/utils/`, `src/types/`, `src/constants/`, `src/lib/`, `src/styles/`: shared app building blocks.
- `src/locales/`: app i18n resources; manifest strings live in `src/public/_locales/`.

### Tests and Artifacts

- `tests/`: Vitest setup, MSW handlers, and shared test utilities.
- `e2e/`: Playwright end-to-end coverage.
- Build artifacts are written to `.output/`; browser test artifacts may appear in `coverage/`, `playwright-report/`, and `test-results/`.

## Domain Knowledge: Site Types & Upstream Backends

This repo models site support on three independent axes: account scope, managed-site scope, and adapter family/capabilities. Do not infer one axis from another.

`src/services/accountSiteDefinitions/definitions.ts` is the source of truth for registered site types, scopes, adapter families, onboarding metadata, and product profiles. `src/services/apiAdapters/registry.ts` owns capability dispatch. `src/services/apiService/` contains provider-specific protocol transports used by those adapters.

When working on a site type:

1. Confirm registration and scope in `src/services/accountSiteDefinitions/identifiers.ts`, `definitions.ts`, and `registry.ts`.
2. Confirm capability dispatch in `src/services/apiAdapters/registry.ts` and the provider-specific adapter. Use `src/services/siteDetection/detectSiteType.ts` only for onboarding and detection behavior.
3. Verify upstream behavior before making definitive claims when backend differences matter.
4. If upstream behavior cannot be verified, state assumptions clearly and ask for the target deployment URL, fork, version, or a redacted network trace.

### Relationships

- **One API (`one-api`)** is the original upstream family. One API/New API-family account types share capability construction under `src/services/apiAdapters/newApi/` and protocol transports under `src/services/apiService/newApiFamily/`.
- **New API (`new-api`)** is a One API downstream family with both account-site and managed-site support.
- **Veloera (`Veloera`)** is downstream of New API and uses the New API family plus Veloera-specific account and managed-site overrides.
- **OneHub (`one-hub`)** is downstream of One API with a substantially different surface.
- **DoneHub (`done-hub`)** is downstream of OneHub and uses New API-family account capabilities plus a dedicated managed-site adapter.
- **AnyRouter (`anyrouter`)** and **WONG公益站 (`wong-gongyi`)** use New API-family capabilities with provider-specific variants and check-in handling; verify the target deployment before describing their exact compatibility.
- **`v-api`** documents its backend as based on One API with some New API functionality; treat it as a One-API derivative/New API-compatible bucket rather than a pure New API fork.
- **`Super-API`, `Rix-Api`, and Neo-API (`neo-Api` in code)** are treated as New API-family variants or compatibility buckets, but their degree of downstream modification varies by deployment and should not be guessed without upstream docs or observed API behavior.
- **Legacy VoAPI (`VoAPI`)** remains a New API-family account compatibility bucket for older deployments. **Current VoAPI (`voapi-v2`)** is account-only and has dedicated adapters under `src/services/apiAdapters/voapiV2/` plus transports under `src/services/apiService/voapiV2/`; do not apply one generation's API assumptions to the other.
- **Octopus (`octopus`)** is managed-only and has dedicated managed-site capabilities plus protocol transports under `src/services/apiService/octopus/`.
- **AxonHub (`axonhub`)** is managed-only and not One-API/New-API compatible; it uses dedicated GraphQL admin integration and native managed-resource adapters.
- **Claude Code Hub (`claude-code-hub`)** is managed-only and not One-API/New-API compatible; it uses dedicated admin/provider and managed-site adapters.
- **Sub2API (`sub2api`)** is both an account site and a managed site. It has dedicated authentication-session, account, model-catalog, key-resource, and managed-resource integrations; it is not a New API-family alias.
- **AIHubMix (`AIHubMix`)** is account-only and uses dedicated capabilities under `src/services/apiAdapters/aihubmix/`. Always use `https://aihubmix.com` as the API origin, including accounts imported from `console.aihubmix.com`. Auto-detect may use logged-in web endpoints (`/call/usr/self`, `/call/usr/tkn`) to obtain the account access token, but saved accounts operate as access-token accounts. Token-authenticated requests send raw `Authorization: <access_token>` without a `Bearer` prefix. Full API keys are one-time secrets; saved key responses may be masked and must not fall back to New API-family secret-resolution behavior.
- **SharedChat (`sharedchat`)** is an account-only integration for the canonical `new.sharedchat.cc` deployment. It uses dedicated cookie-authenticated account, service-credential, invite, and model-catalog capabilities. Treat its observed deployment API as provider-specific; no verified public upstream source repository is currently recorded.
- **OpenRouter (`openrouter`)** is an account-only platform integration, not a managed/self-hosted backend. It uses Management Keys for account access and provides native API-key resources plus provider-owned model catalogs.

### Managed Sites

`ManagedSiteType` is defined in `src/constants/siteType.ts` and currently includes:

- `new-api`
- `Veloera`
- `done-hub`
- `octopus`
- `axonhub`
- `claude-code-hub`
- `sub2api`

Do not assume `one-hub`, `anyrouter`, `wong-gongyi`, either VoAPI generation, `v-api`, AIHubMix, SharedChat, OpenRouter, or other account-site compatibility buckets are managed sites without checking the current definition registry.

### Backend Notes

- Account-site membership, onboarding metadata, adapter family, product profiles, and managed-resource policy are centralized in `src/services/accountSiteDefinitions/`.
- Site capability dispatch is centralized in `src/services/apiAdapters/registry.ts`; shared New API-family behavior lives under `src/services/apiAdapters/newApi/` and `src/services/apiService/newApiFamily/`.
- Managed-site capabilities live under `src/services/apiAdapters/managedSites/`; provider-native managed resources live under `src/services/apiAdapters/managedResources/`.
- Provider directories under `src/services/apiService/` are protocol transports, not necessarily `siteType` values or capability declarations.
- `src/constants/siteType.ts` is a compatibility facade over the definition registry. Use the registry, not directory names or detection rules, to decide whether a type is account-scoped or managed-scoped.

### Default Upstream References

When the user names a backend without a deployment URL or fork, treat these as the default upstream references:

- One API: `https://github.com/songquanpeng/one-api`
- New API: `https://github.com/QuantumNous/new-api`
- Veloera: `https://github.com/Veloera/Veloera`
- V-API: `https://github.com/popjane/v-api`
- Current VoAPI / `voapi-v2`: `https://github.com/VoAPI/VoAPI`; verify legacy `VoAPI` compatibility against the target deployment
- Super-API: `https://github.com/SuperAI-Api/Super-API`
- AnyRouter docs: `https://docs.anyrouter.top/`
- OneHub: `https://github.com/MartialBE/one-hub`
- DoneHub: `https://github.com/deanxv/done-hub`
- Octopus: `https://github.com/bestruirui/octopus`
- AxonHub: `https://github.com/looplj/axonhub`
- Claude Code Hub: `https://github.com/ding113/claude-code-hub`
- Sub2API: `https://github.com/Wei-Shaw/sub2api`
- AIHubMix API docs: `https://docs.aihubmix.com/en/api/Cli` and `https://docs.aihubmix.com/en/api/Models-API`
- SharedChat canonical deployment: `https://new.sharedchat.cc`; no verified public upstream source repository is currently recorded
- OpenRouter: `https://openrouter.ai/`; docs: `https://openrouter.ai/docs`; OpenAPI source: `https://github.com/OpenRouterTeam/docs/blob/main/openapi/openapi.yaml`

If the user's reported behavior differs from upstream, ask for the exact deployment, fork, or version before concluding the repo is wrong.

### External Backend References in Code

- When implementation behavior depends on external upstream documentation or verified backend behavior, add a concise code comment near the adapter logic that records the source and the specific contract being relied on.
- This is required when the source determines protocol fields, authentication format, unsupported capabilities, compatibility boundaries, one-time secrets, endpoint selection, or deliberate non-fallback behavior.
- Prefer a short URL or upstream repository reference plus the relevant contract summary. Do not add broad comments for ordinary implementation details that are already obvious from local types or tests.

## Build, Test, and Development Commands

### Prerequisites

Node.js version from `.nvmrc` and pnpm 10+.

### Local Development

- Install: `pnpm install` (runs `wxt prepare` via `postinstall`).
- Dev, Chromium: `pnpm dev`, then load `.output/chrome-mv3-dev` as an unpacked extension.
- Dev, Firefox: `pnpm dev:firefox`, then load `.output/firefox-mv2-dev` as a temporary add-on.
- Dev, mobile Firefox helper: `pnpm dev:mobile:firefox`.

### Build and Package

- Build: `pnpm build`, `pnpm build:firefox`, `pnpm build:all`.
- Package: `pnpm zip`, `pnpm zip:firefox`, `pnpm zip:all`.

### Validation and Tests

- Type-check: `pnpm compile`.
- Repo-wide dead-code/dependency analysis: `pnpm knip`.
- Lint/format checks: `pnpm lint`, `pnpm format:check`.
- Hook-equivalent validation: `pnpm run validate:staged`, `pnpm run validate:push`.
- Unit tests: `pnpm test`, `pnpm test:watch`, `pnpm test:ci`.
- E2E tests: `pnpm e2e:install`, `pnpm e2e`, `pnpm e2e:ui`.

## Coding Style & Naming Conventions

### Style

- TypeScript + React with Prettier formatting and ESLint enforcement.
- Follow the existing repo style: 2 spaces, no semicolons, double quotes.

### Imports and File Placement

- Prefer `~/` for `src/` imports and `~~/` for repo-root imports such as tests and tooling.
- Tests typically use `*.test.ts` or `*.test.tsx` and are organized under `tests/`; do not add colocated `__tests__/` directories under `src/`.
- Keep options-page entrypoints thin; shared logic should not depend on `src/entrypoints/options/pages/**`.
- Keep `src/services/` free of React UI state wiring. Put React context/provider modules in `src/contexts/`, and place UI-facing hooks outside `services/` unless they are genuinely service-layer logic with no React state ownership.

## Implementation Expectations

### Branch Freshness

- Before starting non-trivial work on a feature branch, fetch the remote and check whether its base branch has advanced.
- If the branch is stale, refresh only the current branch. Use `refresh-stale-branch` when available; otherwise perform the refresh directly. Do not update every worktree.

### Implementation Strategy

- Inspect nearby existing abstractions before planning or implementing new helpers, modules, or UI patterns; prefer reuse or small extensions over parallel implementations.
- For dependencies bundled with the extension, treat package size as a secondary selection factor because it adds no per-use network request. Make size decisive only when measured extension output, startup, memory, or store-distribution impact is material.
- If a string participates in runtime branching, shared protocol values, reusable state mapping, or canonical external URLs, do not duplicate it as a bare literal across modules. Prefer a single runtime constant source, and derive types from that source when both runtime and type-level usage are needed.
- Normalize data at the highest reliable boundary, then pass the normalized shape downward. Once a contract is established, prefer required types in downstream helpers and components instead of reintroducing optional fallbacks at each leaf.
- Keep fallback behavior close to the layer that defines the rule or owns the data contract. Do not duplicate the same fallback across multiple consumers merely to compensate for weak typing or incomplete normalization upstream.

### UI Component Dependencies

- This repo has shadcn configured via `components.json`. When adding a new shadcn-supported primitive, prefer `pnpm shadcn add <component> --yes` or `pnpm shadcn add <component> --overwrite --yes` when replacing an existing local baseline.
- Treat the shadcn CLI output as the baseline. Adapt it only as needed for repo conventions: `~/` aliases, `src/components/ui` barrel exports, `cn`, design tokens, floating-layer/z-index behavior, i18n, lint/JSDoc requirements, and component-specific UX.
- Do not hand-copy shadcn component templates when the CLI can generate them. If the CLI fails, classify whether the failure is tooling, network, auth, package-manager, or registry related; clean unintended partial outputs before retrying or falling back.
- Do not remove or rewrite shadcn-added dependencies merely to reduce lockfile noise unless dependency cleanup is explicitly in scope. If a generated dependency looks excessive, call it out and keep the task moving unless it creates a concrete build, bundle, license, or runtime problem.

### Feature Observability and Discoverability

Treat telemetry and settings discoverability as related release-readiness checks for new or materially changed product behavior. They answer different questions and should be evaluated separately.

#### Telemetry

- For new or materially changed product behavior, make an explicit telemetry decision before handoff: `none`, `reuse existing`, `add action`, `add settings snapshot`, or `add result/summary event`. Do not default to silent feature work.
- Add or update product analytics for new user-visible actions, settings, async/background flows, automatic detection branches, confirmation/cancel paths, shortcuts, and recovery actions when the data is needed to understand adoption, success, failure, skipped states, or funnel drop-off.
- For high-volume, low-meaning telemetry such as passive impressions, prefer persisted daily summary events over per-event capture with short TTL dedupe.
- Keep analytics privacy-safe: record controlled booleans, enums, counts, durations, and status categories only. Do not record URLs, hosts, paths, raw IDs, names, API keys, tokens, cookies, prompts, responses, user-entered text, backend messages, or stack traces.
- When adding analytics fields, update the typed event payload, privacy allow-list/sanitizer, snapshot builders, and focused tests together. If telemetry is intentionally not added, state the reason in the final handoff.

#### Settings Search and Deep Links

- When adding, renaming, moving, or deleting settings UI, update settings search definitions and deep-link targets in the same change. Check the relevant `*.search.ts`, `searchTargets.ts`, target `id` attributes, URL `anchor` parameters, and `ANCHOR_TO_TAB` mappings when heading anchors or cross-entrypoint navigation are involved.
- Prefer a single exported target-id constant for settings controls that are used by both rendered DOM ids and search/navigation definitions. Do not duplicate anchor strings across UI, search index, tests, or runtime navigation.
- Cover settings search and anchor behavior with focused unit/component tests by default. Add Playwright E2E only when the risk depends on real extension browser behavior rather than search registry data or route parameter handling.

### Progressive Refactoring

- Prefer progressive refactors over big-bang rewrites when replacing legacy flows or reshaping feature boundaries.
- When a new implementation path is chosen for a feature, route subsequent feature work to that path by default.
- Legacy paths may receive only compatibility shims, required regression fixes, or migration glue that forwards toward the new path.
- Do not implement the same new capability in both the preferred path and a legacy path unless the task explicitly requires a temporary compatibility bridge.
- When keeping a legacy branch temporarily, add a short comment that states why it still exists, what new path replaces it, and what condition allows safe removal.
- Before deleting an old path, verify inbound references, impacted site types or adapters, and the relevant validation coverage.
- For scout-style cleanup in this repo, anchor the scope to the current task or current branch diff. Prefer small behavior-preserving improvements in touched files, such as extracting a tiny repeated helper, clarifying local naming, or replacing duplicated runtime literals with an existing or task-scoped constant. Validate the affected path with the same gate as the main change.

### Maintainability Gate

- Before handoff for non-trivial code changes, inspect the task-scoped diff for repeated logic, duplicated runtime literals, weak fallback propagation, oversized components or functions, and missed reuse of existing helpers or components. Fix low-risk issues inside the touched scope; if cleanup would broaden scope or change behavior, report it as follow-up instead of silently leaving it.
- For non-trivial implementation work, include a maintainability decision in the final handoff: what was reused, what was extracted or centralized, and what was intentionally left because it would exceed task scope.

### User-Facing Errors and Disclosure

- For user-visible success/error feedback, do not rely solely on backend `message` fields; provide a local fallback when responses may be empty, unstable, or not suitable for direct display.
- In errors shown only to the affected user, preserve useful upstream `code` and `message` by default. Do not replace safe diagnostic detail with generic localized copy merely because it exposes backend or deployment information; explicitly map only known opaque or unhelpful errors.
- Treat private user-facing errors, local logs, and telemetry or external reports as separate disclosure boundaries. Private UI and local logs may retain useful diagnostic context after redacting tokens, API keys, cookies, refresh/session secrets, credentials, authentication payloads, and authentication headers. Telemetry and external reports must not include raw backend messages or secrets.

### Comments

- Add brief inline comments or short code-block comments when non-obvious intent, invariants, edge cases, or protocol/browser constraints need clarification; do not narrate obvious code.

### Validation Strategy

Use validation as progressive gates:

- **Focused checks**: Agents own affected-behavior validation. Start with the repo-defined affected-file or `related` flow and broaden only when the change is cross-cutting. For TS/TSX edits, prefer `vitest related --run` style checks over a manually assembled test file list; add focused browser E2E only when the unresolved risk depends on real extension behavior.
- **Commit gate**: When committing, stage only task-scoped files and let the pre-commit hook run `pnpm run validate:staged`. Do not manually run the same gate immediately before that hook on an unchanged index. For a local handoff without a commit, do not stage files solely to run this gate; report that the commit gate was not exercised.
- **Formatting**: Do not treat standalone Prettier checks as correctness validation. Use Prettier directly only when formatting is the task, no commit will be created, a hook failed because of formatting, or pre-formatting is needed to reduce review noise; prefer `prettier --write` in those cases.
- **Push gate**: When pushing applicable TypeScript, export, dependency, generated-wiring, shared-contract, or repo-structure changes, let the pre-push hook run `pnpm run validate:push`. Do not pre-run the same gate on an unchanged file tree, and do not run `validate:push` or `pnpm knip` for a local-only handoff by default.
- **CI gate**: PR CI owns repository-wide unit, coverage, and full E2E suites by default. Run one locally only when the user explicitly requests it, repository policy requires it before the requested handoff, or the task is diagnosing that suite or a failure visible only there.
- **Evidence reuse**: Treat validation evidence as current for the same relevant base and file tree. A history-only commit rewrite does not invalidate it after tree equivalence is verified; rerun proportionately when the base or content changes, the prior result was incomplete or failed, or the affected risk was not covered.
- **Push failures**: If `pnpm run validate:push` or the actual pre-push hook fails, do not report the remote handoff as complete. Classify the failure as code, tooling, environment, auth, network, or permission related; fix code and tooling failures before retrying the push, and report environmental blockers with the exact remaining impact.
- **Sub-agent handoffs**: Sub-agents may hand off partial implementation, investigation findings, or review notes without running hook-owned gates unless their assigned scope explicitly requires one. They should report what they completed, files touched, validation run if any, known gaps, and risks; the coordinator owns the final validation decision and evidence report under the ownership rules above.

## Testing Guidelines

### Test Stack

- Unit and component tests use Vitest with jsdom and Testing Library.
- HTTP mocking uses MSW from `tests/msw/handlers.ts` and `tests/msw/server.ts`.
- Shared test rendering utilities live in `tests/test-utils/render.tsx`.
- Global test setup lives in `tests/setup.ts` and uses `wxt/testing/fake-browser` for WebExtension API mocking.

### Coverage Expectations

- For `src/**` TS/TSX changes that add or modify executable logic, treat tests as part of the same task by default instead of waiting for CI to expose a coverage drop. Pure types, constants, copy, styles, and no-behavior refactors are the main exceptions.
- New executable files, functions, branches, listeners/controllers, or error fallback paths should usually ship with at least one targeted test covering the added behavior.
- Coverage-driven tests must still prove a meaningful behavior, regression, edge case, protocol contract, or integration boundary. Do not add tests that only execute lines, restate implementation shape, or assert mock choreography unrelated to externally observable behavior.
- When coverage tooling reports misses, identify the exact changed lines or branches first. Add the smallest behavior-level coverage for those paths, and treat unrelated whole-file historical misses as diagnostic context rather than automatic scope.
- Do not stop at `happy path` coverage. For added or changed executable logic, identify and cover the most relevant `edge cases`, especially empty or partial inputs, invalid values, boundary conditions, backend error or empty responses, browser API unavailability, permission or environment limits, site-type compatibility branches, cache or persistence failures, and repeated or concurrent triggers.
- If an important `edge case` is not practical to automate in this change, call out the uncovered scenario, why it remains uncovered, and the residual risk before handoff.

### Test Quality Anti-Patterns

- Do not freeze whole arrays, object graphs, menu/layout configs, or rendered structures with exact equality unless the full shape is the product contract. Prefer asserting the specific invariant that matters, such as required membership, relative order, fallback behavior, or a compatibility rule.
- Avoid tests that pass mainly by mocking most collaborators and asserting that mocks were called in a particular internal sequence. Mock-call assertions are appropriate for browser APIs, runtime messages, analytics payloads, storage boundaries, and adapter contracts; otherwise prefer observable state, persisted output, rendered result, or returned value.
- Do not assert Tailwind classes, inline styles, wrapper elements, or third-party library transform details in business component tests unless styling is the explicit contract under test. Class/style assertions are acceptable for UI primitives and style helper modules whose public contract is class composition.
- Avoid locating elements by DOM shape, CSS class scans, `nth(...)`, or unlabeled inputs when a semantic role, accessible name, exported test id, or feature-local selector can express the behavior. Positional selectors are only acceptable when the order itself is the contract being tested.
- Do not use E2E to cover logic that can be tested faster and more precisely in Vitest, such as pure filtering, formatting, mapping, validation, or adapter normalization. Reserve E2E for browser-extension runtime behavior, cross-entrypoint workflows, persistence/navigation integration, and regressions lower-level tests cannot catch.

### E2E and Broad Validation

- Do not add Playwright E2E coverage mechanically for every feature commit. Prefer Vitest or Testing Library for pure functions, protocol adapters, formatting/parsing logic, copy-only changes, style-only changes, and isolated component state.
- Before adding or expanding Playwright coverage, first ask whether the same regression can be covered by a targeted Vitest test. If the behavior is limited to hook state, component rendering, form validation, filtering/search/sorting, formatting, copy, or a mocked service call, use Vitest by default instead of E2E.
- Do not use E2E to exhaustively cover UI state matrices. For pages with many filters, tabs, empty states, sort modes, or control variants, keep those combinations in Vitest and reserve E2E for one representative browser-level path.
- For any new or materially changed user-facing behavior, make an explicit E2E decision before handoff: add/update an E2E test, identify the existing E2E flow that already covers the risk, or state why lower-level tests are the right coverage layer.
- Bias toward adding or updating Playwright E2E coverage only when the main risk appears in a real extension browser context. This includes cross-entrypoint behavior across popup, options, sidepanel, background, content scripts, runtime messages, tabs, windows, or extension storage; navigation, hash routing, lazy-loaded entrypoints, first-load behavior, and deep links; browser APIs or permissions such as notifications, downloads, clipboard, context menus, tab/window handling, optional permissions, service workers, or extension build output; complete critical workflows whose failure would not be visible in component tests; and interaction risks involving dialogs, popovers, floating layers, drag/drop, toasts, or confirm flows.
- For Playwright E2E selectors, prefer stable feature-local or entrypoint-local `testIds.ts` constants for workflow-critical elements. If an E2E flow needs to locate, disambiguate, or observe an element and the existing UI does not expose a suitable stable selector, add a narrowly scoped test id as part of the same change instead of relying on positional selectors, mutable visible copy, CSS selectors, or incidental DOM ids. Keep user-visible text assertions for user-facing outcomes, not for locating critical controls.
- Add or update E2E coverage for regressions that lower-level tests previously missed, especially when the failure involved browser runtime behavior, entrypoint integration, persisted state, or a complete user task.
- For larger PRs that add a user-visible workflow, prefer one stable happy-path E2E scenario over many narrow UI assertions. If an existing E2E already boots the relevant entrypoint and exercises a representative path, extend Vitest coverage for additional states instead of adding another browser scenario.
- Final handoffs for user-facing behavior changes should include the E2E decision and the validation actually run.
- Temporary E2E tests created only for self-verification should be deleted before handoff by default. Keep them only when they are deterministic, reusable, and provide clear long-term regression value; if retention is genuinely ambiguous, explain the tradeoff and ask before keeping them.
### Shared Surface Changes

- If a change modifies shared component or hook props, validation must cover direct render/use sites and standalone harness tests that instantiate the changed API surface.
- Current coverage baseline is configured in `vitest.config.ts`.

## Documentation Guidelines

### Source of Truth

- Keep repo docs such as `README.md` and `README_EN.md` consistent when their shared content changes.
- In `docs/docs/`, treat Chinese pages as the source of truth.

### Translation Workflow

- `docs/docs/en/**` and `docs/docs/ja/**` are auto-translated by `docs_assistant/translate.py` and `.github/workflows/translate-docs.yml`; avoid manual edits by default. If the user explicitly asks to update translated docs directly, manual edits are allowed, but keep them minimal and aligned with the Chinese source.

### Navigation

- When adding or removing docs pages under `docs/docs/`, update locale navigation in `docs/docs/.vuepress/config.js`.

## i18n Guidelines

### Typing and API Usage

- When a helper explicitly accepts a translation function, type it as `TFunction` from `i18next`. Do not hand-write signatures like `(key: string, options?: any) => string` or `ReturnType<typeof useTranslation>["t"]` unless a narrower type is intentionally required.

### Translation Keys and Fallbacks

- Prefer literal translation keys. Finite, typed key selection is allowed when `i18next-cli` can statically enumerate every possible key; verify changes with `pnpm run i18n:extract:ci`. For runtime-selected keys, constrain values to an owned key family and handle unknown values explicitly; never pass raw user or backend text directly to `t`.
- Keep canonical UI copy in locale resources and synchronized across supported locales. Use i18next `defaultValue` only when a missing key is expected by contract and the fallback is intentional; do not use it to conceal a missing locale resource or avoid synchronizing ordinary application copy.

### Plurals and Count Semantics

- When a visible phrase depends on `count` for grammar or wording, prefer a proper pluralized translation (`t(key, { count })`, ICU/message-format equivalent, or explicit plural key family) so the locale controls the full rendered phrase.
- Only split the numeric value out of the translation when the number is a genuinely separate visual metric, such as a standalone badge/counter or a parenthesized metric that does not need grammatical agreement with the adjacent label.
- Treat unexpected `_one`, `_other`, or similar extract-generated rewrites as a signal to clarify intent in source code: either model the phrase explicitly as pluralized copy, or remove `count` from the translation call because the number is visually independent. Do not patch locale JSON blindly without fixing the source usage pattern.

### Extraction Workflow

- When legitimate runtime keys cannot be enumerated from executable source, preserve the narrowest key family with `extract.preservePatterns` or an extractor plugin. Do not add no-op helpers, unreachable branches, dummy `t(...)` calls, or extraction-only comments solely to retain keys.
- After running `pnpm run i18n:extract` or any hook that can update locale files, inspect both the extractor-produced diff and the task-scoped `src/locales/**` diff against the task base before proceeding. Account for every deleted existing key; do not accept `pnpm run i18n:extract:ci` reporting no updates as proof when locale changes are already present or staged.
- If `i18n:extract` removes keys you expected to keep, fix the source usage or extractor configuration instead of re-adding locale JSON by hand. In this repo, prefer direct extractable calls such as `t("ns:key")` over wrapper names like `translate("ns:key")` unless the wrapper is explicitly configured in `i18next.config.ts`.
- After changing translation keys, locale JSON, or any UI code that adds new `t(...)` usages, run `pnpm run i18n:extract:ci` and ensure it reports no unexpected updates before handoff.

### Locale Shape Consistency

- Keep locale key shapes stable across languages; do not let one language drift into a pluralized or structurally different key family unless that family is intentionally introduced for every locale.
- When changing an existing app locale string under `src/locales/**`, check the same key in every sibling locale before handoff. If the wording describes a renamed action, control, icon, or workflow, update all supported app locales in the same change unless a locale is intentionally generated or out of scope, and call that out explicitly.

## Security & Configuration Tips

### Secrets and Configuration

- Never commit secrets, tokens, or private environment overrides.
- Use `.env.example` as the reference for supported environment variables.

### Local Files

- Treat backup or generated local files as out of scope unless the task explicitly targets them.
