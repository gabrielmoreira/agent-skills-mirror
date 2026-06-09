# Contributing to Megingjord

Welcome! Detailed guides are linked below.

## Guide index

| Topic                                            | Guide                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Skill development — add, modify, test skills     | [`docs/contributing-skills.md`](docs/contributing-skills.md)                       |
| PR process — baton gates, doc coverage, signing  | [`docs/contributing-workflow.md`](docs/contributing-workflow.md)                   |
| Dev environment — setup, commands, code style    | [`docs/contributing-dev-setup.md`](docs/contributing-dev-setup.md)                 |
| 100-line design contract — split, never compress | [`docs/howto/100-line-design-contract.md`](docs/howto/100-line-design-contract.md) |

## 100-line design contract

Every file in this repo must be **≤100 lines**. This is a design rule, not a
content budget. When a file needs more space, split it into linked companion
files — never compress or remove content to make the count fit.

See [`docs/howto/100-line-design-contract.md`](docs/howto/100-line-design-contract.md)
for split patterns by file type (markdown, JS/TS, CSS, HTML, shell).

## Types of contribution

- **Skills** — New capabilities delivered to Copilot / Claude Code / Codex runtimes
- **Instructions** — Governance policy markdown for `instructions/`
- **Scripts** — Node.js utilities in `scripts/global/` that deploy to `~/.copilot/scripts/`
- **Wiki** — Knowledge pages in `wiki/wisdom/`, `wiki/work-log/`, `wiki/code/`
- **Dashboard** — Fleet monitoring UI in `dashboard/`
- **Governance** — Hook policies, CI workflows in `.github/workflows/`

## First-time contributor quickstart

```bash
# 1. Clone and install
git clone https://github.com/chf3198/megingjord-harness.git
cd megingjord-harness && npm install

# 2. Validate baseline before making any changes
npm run lint && npm test && npm run validate:triage

# 3. Create a ticket (governance rule — required before branching)
gh issue create --title "feat: your change" --label "type:feat,priority:P2"

# 4. Branch from main using the required naming pattern
git checkout -b feat/123-short-slug   # or fix/123-short-slug

# 5. Implement, verify, open PR
npm run format:check && npm run lint && npm test
gh pr create --title "feat(scope): description #123"
```

## Reporting a bug

Open an issue with label `type:bug`. Include:

1. Runtime (`copilot` | `claude-code` | `codex`)
2. Reproduction steps
3. Observed vs expected behaviour
4. `npm run lint && npm test` output

## Code of conduct

All contributors follow [Contributor Covenant v2.1](CODE_OF_CONDUCT.md).
Violations: `conduct@megingjord.dev`.
