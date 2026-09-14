# `scripts/`

Repo-maintenance, CI, dev-loop, and release tooling. This is a map, not a
manual — each entry point below has its own header comment or README with the
details.

## Sub-directories

The first seven have their own README; the rest are documented by the header
comments of the scripts inside them.

| Directory | Purpose |
| --- | --- |
| `ci/` | Merge-gate scripts (layout, feature forwarding, module pins, coverage, toolchain drift) — see [ci/README.md](ci/README.md). |
| `bench/` | Agent-scale benchmarks against a real `openhuman-core` server process — see [bench/README.md](bench/README.md). |
| `debug/` | Agent-friendly wrappers around the test runners, run via `pnpm debug ...` — see [debug/README.md](debug/README.md). |
| `profile/` | Embedded-library benchmarking (RSS, CPU, heap, fleet sweeps) for the Rust core — see [profile/README.md](profile/README.md). |
| `rabbit/` | Auto-retriggers CodeRabbit reviews once a PR's rate-limit window elapses — see [rabbit/README.md](rabbit/README.md). |
| `shortcuts/` | High-level pnpm workflow commands (`pnpm review`, `pnpm work`, `pnpm reset`, ...) — see [shortcuts/README.md](shortcuts/README.md). |
| `test-planning/` | Mines GitHub issues/PRs into a test-planning backlog via an LLM CLI — see [test-planning/README.md](test-planning/README.md). |
| `release/` | Release build, signing, packaging, and publishing scripts (macOS notarization, APT/Homebrew, npm, updater manifests). |
| `mock-api/` | The shared mock backend modules (routes, socket, admin, state) behind `mock-api-server.mjs` / `mock-api-core.mjs`; exercised by `pnpm mock:api` and Rust/E2E test runs. |
| `lib/` | Small parsers shared by the CI gates (checklist, coverage matrix, feature forwarding, module pins). |
| `__tests__/`, `tests/` | Unit tests for the scripts themselves (`node --test`, plus a PowerShell installer test). |
| `fixtures/` | `latest.json` / `release.json` release-metadata fixtures consumed by `test_install.sh` (the `install.sh` test). |
| `theme-codemod/` | Codemod collapsing audited `light dark:` Tailwind pairings into the semantic theme utilities (`node scripts/theme-codemod/migrate.mjs [--write]`; see `gitbooks/developing/theming.md`). |
| `agent-batch/` | Validates a batch spec of parallel agent branches, checks file overlap, prints per-agent launch prompts, and reports status (`pnpm agent-batch <validate\|overlap\|launch\|status> <spec.json>`). |
| `deep-work/` | Issue-to-PR workflow automation over worktrees and AI agents: `pnpm deep-work start\|pick\|continue\|status\|list\|cleanup`. |

## pnpm-wired entry points

| Command | Script |
| --- | --- |
| `pnpm docs:generate` / `docs:check` | `generate-architecture-docs.mjs` |
| `pnpm test:rust` | `test-rust-with-mock.sh` (via `openhuman-app`'s `test:rust`) |
| `pnpm test:rust:e2e` | `test-rust-e2e.sh` |
| `pnpm mock:api` | `mock-api-server.mjs` |
| `pnpm debug ...` | `debug/cli.sh` |
| `pnpm rust:layout` | `ci/check-openhuman-rust-layout.mjs` |
| `pnpm test:inventory` | `generate-test-inventory.mjs` |
| `pnpm pr:checklist` | `check-pr-checklist.mjs` |

See `package.json` for the full list, including `i18n:*`, `tauri:ios:*`,
`tauri:android:*`, and the `shortcuts/`/`deep-work`/`agent-batch` commands
above.

## Families by prefix

- **`run-dev-*`** — dev-loop launchers. `run-dev-macos.sh` backs `dev:app` in
  `app/package.json`; `run-dev-win.cmd` backs `dev:app:win`; `run-dev-web.sh`
  backs the root `dev:app:web`.
- **`test-*`** — Rust and flow test runners (`test-rust-with-mock.sh`,
  `test-rust-e2e.sh`, `test-rust-inference-e2e.sh`, channel/webhook/onboarding
  flow smoke tests).
- **`debug-*`** — one-off live debugging helpers (Composio, Notion, agent
  prompts, skills) distinct from the `debug/` runner directory.
- **`check-*`** (outside `ci/`) — repo-level gates: `check-coverage-matrix.mjs`,
  `check-domain-e2e-coverage.mjs`, `check-pr-checklist.mjs`,
  `check-kernel-floor.sh` (dependency-floor ratchet), `check-prompt-budget.sh`
  (fixed-prefix token ratchet), `check-linux-tls-dependencies.sh`.
- **`i18n-*`** — translation coverage and audit tools (`i18n-coverage.ts`,
  `i18n-find-english.ts`, `i18n-react-audit.ts`, behind `pnpm i18n:*`);
  `i18n-doc-scan.sh` scans the Chinese GitBook docs instead of the app.
- **`ios-init.sh` / `android-init.sh`** — `tauri ios init` /
  `tauri android init` wrappers (`pnpm tauri:ios:init`, `pnpm tauri:android:init`)
  for the experimental mobile clients; **`ios-appstore-*`** build, export, and
  upload the iOS IPA and its App Store Connect assets/metadata.
- **`install.sh` / `install.ps1`** — the public `curl | bash` / `irm | iex`
  installers documented in `gitbooks/developing/getting-set-up.md`; tested by
  `test_install.sh` / `tests/OpenHumanWindowsInstall.Tests.ps1` and smoke-checked
  by `docs/RELEASE-MANUAL-SMOKE.md`.
- **`ci-cancel-aware.sh`** — wraps a long-running CI command, polling the
  workflow run's status (via `GH_TOKEN`) and killing the command's process tree
  when the run is cancelled — needed because `docker exec` swallows the
  runner's signals in container jobs. Required by `AGENTS.md` for long CI
  build/test commands.
- **`assert-shed.sh`** / **`dep-sim.py`** — prove or simulate a dependency
  reduction before claiming one in a PR; cited by `AGENTS.md`.
