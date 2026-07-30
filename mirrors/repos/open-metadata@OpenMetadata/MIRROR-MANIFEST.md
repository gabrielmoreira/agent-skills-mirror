---
repo: open-metadata/OpenMetadata
repoUrl: https://github.com/open-metadata/OpenMetadata.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `open-metadata/OpenMetadata` — 26 default patterns, 5 followed patterns, 90 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `open-metadata/OpenMetadata` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 5 |
| Files         | 90 |

## Default Sparse Patterns  *(included from config)*

- `**/AGENTS.md`
- `**/CLAUDE.md`
- `**/claude.md`
- `**/gemini.md`
- `**/GEMINI.md`
- `**/SKILL.md`
- `**/skills.md`
- `**/LLMs.txt`
- `**/llms.txt`
- `**/copilot-instructions.md`
- `**/.cursorrules`
- `**/.cursor/rules/**`
- `**/.windsurfrules`
- `**/.continue/**`
- `.github/instructions/**`
- `.github/prompts/**`
- `.agents/**`
- `agents/**`
- `skills/**`
- `skill/**`
- `prompts/**`
- `prompt/**`
- `.cursor/**`
- `.continue/**`
- `.mcp/**`
- `mcp/**`

## Followed Sparse Patterns  *(discovered via markdown refs)*

- `ARCHITECTURE.md`
- `DEVELOPER.md`
- `docs/index.md`
- `.claude/rules/schema-first.md`
- `.claude/rules/migrations.md`

## File Index

Legend: **✓** = default pattern · **→** = followed via markdown

| # | S | File |
|---|---|------|
| 1 | ✓ | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| 2 | ✓ | [`AGENTS.md`](AGENTS.md) |
| 3 | ✓ | [`CLAUDE.md`](CLAUDE.md) |
| 4 | ✓ | [`openmetadata-ui-core-components/CLAUDE.md`](openmetadata-ui-core-components/CLAUDE.md) |
| 5 | ✓ | [`skills/.claude-plugin/plugin.json`](skills/.claude-plugin/plugin.json) |
| 6 | ✓ | [`skills/.github/workflows/lint-standards.yml`](skills/.github/workflows/lint-standards.yml) |
| 7 | ✓ | [`skills/.markdownlint.yaml`](skills/.markdownlint.yaml) |
| 8 | ✓ | [`skills/agents/comment-resolution-checker.md`](skills/agents/comment-resolution-checker.md) |
| 9 | ✓ | [`skills/agents/connector-researcher.md`](skills/agents/connector-researcher.md) |
| 10 | ✓ | [`skills/agents/connector-validator.md`](skills/agents/connector-validator.md) |
| 11 | ✓ | [`skills/agents/frontend-reviewer.md`](skills/agents/frontend-reviewer.md) |
| 12 | ✓ | [`skills/agents/java-reviewer.md`](skills/agents/java-reviewer.md) |
| 13 | ✓ | [`skills/agents/python-reviewer.md`](skills/agents/python-reviewer.md) |
| 14 | ✓ | [`skills/code-review/SKILL.md`](skills/code-review/SKILL.md) |
| 15 | ✓ | [`skills/commands/connector-review.md`](skills/commands/connector-review.md) |
| 16 | ✓ | [`skills/commands/connector-standards.md`](skills/commands/connector-standards.md) |
| 17 | ✓ | [`skills/commands/pr-checklist.md`](skills/commands/pr-checklist.md) |
| 18 | ✓ | [`skills/commands/scaffold-connector.md`](skills/commands/scaffold-connector.md) |
| 19 | ✓ | [`skills/commands/test-locally.md`](skills/commands/test-locally.md) |
| 20 | ✓ | [`skills/connector-audit/prompts/00-setup.md`](skills/connector-audit/prompts/00-setup.md) |
| 21 | ✓ | [`skills/connector-audit/prompts/01-metadata-ingestion.md`](skills/connector-audit/prompts/01-metadata-ingestion.md) |
| 22 | ✓ | [`skills/connector-audit/prompts/02-error-handling.md`](skills/connector-audit/prompts/02-error-handling.md) |
| 23 | ✓ | [`skills/connector-audit/prompts/03-connection-auth.md`](skills/connector-audit/prompts/03-connection-auth.md) |
| 24 | ✓ | [`skills/connector-audit/prompts/04-lineage.md`](skills/connector-audit/prompts/04-lineage.md) |
| 25 | ✓ | [`skills/connector-audit/prompts/05-scale-performance.md`](skills/connector-audit/prompts/05-scale-performance.md) |
| 26 | ✓ | [`skills/connector-audit/prompts/06-refactor-plan.md`](skills/connector-audit/prompts/06-refactor-plan.md) |
| 27 | ✓ | [`skills/connector-audit/prompts/07-implementation.md`](skills/connector-audit/prompts/07-implementation.md) |
| 28 | ✓ | [`skills/connector-audit/SKILL.md`](skills/connector-audit/SKILL.md) |
| 29 | ✓ | [`skills/connector-audit/templates/audit-report.md`](skills/connector-audit/templates/audit-report.md) |
| 30 | ✓ | [`skills/connector-building/connector-profile.schema.json`](skills/connector-building/connector-profile.schema.json) |
| 31 | ✓ | [`skills/connector-building/examples/dashboard-rest.yaml`](skills/connector-building/examples/dashboard-rest.yaml) |
| 32 | ✓ | [`skills/connector-building/examples/database-sqlalchemy.yaml`](skills/connector-building/examples/database-sqlalchemy.yaml) |
| 33 | ✓ | [`skills/connector-building/examples/pipeline-sdk.yaml`](skills/connector-building/examples/pipeline-sdk.yaml) |
| 34 | ✓ | [`skills/connector-building/GUIDE.md`](skills/connector-building/GUIDE.md) |
| 35 | ✓ | [`skills/connector-building/references/architecture-decision-tree.md`](skills/connector-building/references/architecture-decision-tree.md) |
| 36 | ✓ | [`skills/connector-building/references/capability-mapping.md`](skills/connector-building/references/capability-mapping.md) |
| 37 | ✓ | [`skills/connector-building/references/connection-type-guide.md`](skills/connector-building/references/connection-type-guide.md) |
| 38 | ✓ | [`skills/connector-building/SKILL.md`](skills/connector-building/SKILL.md) |
| 39 | ✓ | [`skills/connector-review/scripts/analyze_connector.py`](skills/connector-review/scripts/analyze_connector.py) |
| 40 | ✓ | [`skills/connector-review/scripts/gather-connector-context.sh`](skills/connector-review/scripts/gather-connector-context.sh) |
| 41 | ✓ | [`skills/connector-review/SKILL.md`](skills/connector-review/SKILL.md) |
| 42 | ✓ | [`skills/connector-review/templates/full-review-report.md`](skills/connector-review/templates/full-review-report.md) |
| 43 | ✓ | [`skills/connector-review/templates/incremental-review-report.md`](skills/connector-review/templates/incremental-review-report.md) |
| 44 | ✓ | [`skills/connector-review/templates/pr-review-comment.md`](skills/connector-review/templates/pr-review-comment.md) |
| 45 | ✓ | [`skills/connector-review/templates/specialized-review-report.md`](skills/connector-review/templates/specialized-review-report.md) |
| 46 | ✓ | [`skills/connector-standards/SKILL.md`](skills/connector-standards/SKILL.md) |
| 47 | ✓ | [`skills/hooks/hooks.json`](skills/hooks/hooks.json) |
| 48 | ✓ | [`skills/java-checkstyle/SKILL.md`](skills/java-checkstyle/SKILL.md) |
| 49 | ✓ | [`skills/openmetadata-workflow/SKILL.md`](skills/openmetadata-workflow/SKILL.md) |
| 50 | ✓ | [`skills/planning/SKILL.md`](skills/planning/SKILL.md) |
| 51 | ✓ | [`skills/playwright-validation/SKILL.md`](skills/playwright-validation/SKILL.md) |
| 52 | ✓ | [`skills/playwright/SKILL.md`](skills/playwright/SKILL.md) |
| 53 | ✓ | [`skills/pr-checklist/SKILL.md`](skills/pr-checklist/SKILL.md) |
| 54 | ✓ | [`skills/README.md`](skills/README.md) |
| 55 | ✓ | [`skills/standards/code_style.md`](skills/standards/code_style.md) |
| 56 | ✓ | [`skills/standards/connection.md`](skills/standards/connection.md) |
| 57 | ✓ | [`skills/standards/lineage.md`](skills/standards/lineage.md) |
| 58 | ✓ | [`skills/standards/main.md`](skills/standards/main.md) |
| 59 | ✓ | [`skills/standards/memory.md`](skills/standards/memory.md) |
| 60 | ✓ | [`skills/standards/patterns.md`](skills/standards/patterns.md) |
| 61 | ✓ | [`skills/standards/performance.md`](skills/standards/performance.md) |
| 62 | ✓ | [`skills/standards/registration.md`](skills/standards/registration.md) |
| 63 | ✓ | [`skills/standards/schema.md`](skills/standards/schema.md) |
| 64 | ✓ | [`skills/standards/service_spec.md`](skills/standards/service_spec.md) |
| 65 | ✓ | [`skills/standards/source_types/api.md`](skills/standards/source_types/api.md) |
| 66 | ✓ | [`skills/standards/source_types/dashboard.md`](skills/standards/source_types/dashboard.md) |
| 67 | ✓ | [`skills/standards/source_types/data_warehouses.md`](skills/standards/source_types/data_warehouses.md) |
| 68 | ✓ | [`skills/standards/source_types/database.md`](skills/standards/source_types/database.md) |
| 69 | ✓ | [`skills/standards/source_types/messaging.md`](skills/standards/source_types/messaging.md) |
| 70 | ✓ | [`skills/standards/source_types/mlmodel.md`](skills/standards/source_types/mlmodel.md) |
| 71 | ✓ | [`skills/standards/source_types/nosql_databases.md`](skills/standards/source_types/nosql_databases.md) |
| 72 | ✓ | [`skills/standards/source_types/pipeline.md`](skills/standards/source_types/pipeline.md) |
| 73 | ✓ | [`skills/standards/source_types/search.md`](skills/standards/source_types/search.md) |
| 74 | ✓ | [`skills/standards/source_types/sql_databases.md`](skills/standards/source_types/sql_databases.md) |
| 75 | ✓ | [`skills/standards/source_types/storage.md`](skills/standards/source_types/storage.md) |
| 76 | ✓ | [`skills/standards/sql.md`](skills/standards/sql.md) |
| 77 | ✓ | [`skills/standards/testing.md`](skills/standards/testing.md) |
| 78 | ✓ | [`skills/systematic-debugging/SKILL.md`](skills/systematic-debugging/SKILL.md) |
| 79 | ✓ | [`skills/tdd/SKILL.md`](skills/tdd/SKILL.md) |
| 80 | ✓ | [`skills/test-enforcement/SKILL.md`](skills/test-enforcement/SKILL.md) |
| 81 | ✓ | [`skills/test-locally/SKILL.md`](skills/test-locally/SKILL.md) |
| 82 | ✓ | [`skills/ui-checkstyle/SKILL.md`](skills/ui-checkstyle/SKILL.md) |
| 83 | ✓ | [`skills/ui-core-components/SKILL.md`](skills/ui-core-components/SKILL.md) |
| 84 | ✓ | [`skills/verification/SKILL.md`](skills/verification/SKILL.md) |
| 85 | ✓ | [`skills/writing-playwright-tests/SKILL.md`](skills/writing-playwright-tests/SKILL.md) |
| 86 | → | [`.claude/rules/migrations.md`](.claude/rules/migrations.md) |
| 87 | → | [`.claude/rules/schema-first.md`](.claude/rules/schema-first.md) |
| 88 | → | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| 89 | → | [`DEVELOPER.md`](DEVELOPER.md) |
| 90 | → | [`docs/index.md`](docs/index.md) |

---

*Generated by mirror — do not edit manually*