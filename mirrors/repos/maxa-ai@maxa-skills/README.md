# maxa-skills

Public Claude Code plugin marketplace for the Maxa organization.

## Available Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `maxa-spec` | `build-data-model`, `check-data-model`, `write-business-doc` | Activate a Maxa AI Specification for data modeling, transform implementation, and business analysis |

## Installation

```bash
# Add the marketplace (once)
/plugin marketplace add maxa-ai/maxa-skills

# Install a plugin
/plugin install maxa-spec@maxa-skills
```

## Usage

Once installed, invoke skills with the plugin namespace:

```
/maxa-spec:build-data-model     # Build data models and transforms from the Maxa spec
/maxa-spec:check-data-model     # Audit an existing model against the Maxa spec
/maxa-spec:write-business-doc   # Write business documents (risk register, gap analysis, etc.)
```

## Testing Locally

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

## Evaluations

Each skill includes `evals/evals.json` with test cases and assertions, compatible with Anthropic's [skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) plugin. Test fixtures (Maxa specs, schemas) are in `tests/fixtures/`. `sap-finance-ai-specification` is a copy of the Maxa spec the toolbox produces for the sap-finance dataset (`datasets/sap-finance/processing-artifacts/project/ai-specification/` in `maxa-ai-data-studio-toolbox`), plus `NOTICE.md`; refresh it from there when the toolbox output changes.

To run evaluations:

```bash
# Install skill-creator (once)
/plugin install skill-creator@claude-plugins-official

# Evaluate a specific skill
/skill-creator:skill-creator evaluate my build-data-model skill
```

The eval runner spawns with-skill and without-skill agents for each test case, grades assertions, and produces an HTML viewer for side-by-side comparison. Eval workspaces (`*-workspace/`) are gitignored.

## Validation

Run the CI checks locally before pushing:

```bash
.github/scripts/validate-plugins.sh
```

## Contributing

1. Create or modify a plugin under `plugins/<plugin-name>/`
2. Each plugin needs `.claude-plugin/plugin.json` (with `name` and `version`) and at least one `skills/<skill-name>/SKILL.md`
3. Register new plugins in `.claude-plugin/marketplace.json`
4. **Bump the version in `plugin.json` on every change** — updates won't propagate without it
