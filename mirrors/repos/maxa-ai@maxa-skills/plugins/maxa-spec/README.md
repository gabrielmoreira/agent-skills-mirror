# maxa-spec

Ground the model in a Maxa AI Specification when you build data models, write transforms, or write business documents. A Maxa spec holds the business understanding that Maxa extracts from stakeholder discovery: entities, business rules, KPIs, source-system conventions, and known gaps. The skills in this plugin tell the model which parts of the Maxa spec to read for each task, so that the code and documents follow that business understanding.

## Skills

| Skill | Use it to |
|-------|-----------|
| `build-data-model` | Build data models, SQL or dbt transforms, and KPI calculations from the Maxa spec |
| `check-data-model` | Audit an existing data model or set of transforms against the Maxa spec |
| `write-business-doc` | Write business documents, such as a risk register, a gap analysis, or a stakeholder brief |

## Install

In Claude Code:

```bash
# Add the marketplace (once)
/plugin marketplace add maxa-ai/maxa-skills

# Install the plugin
/plugin install maxa-spec@maxa-skills
```

In Codex:

```bash
# Add the marketplace (once)
codex plugin marketplace add maxa-ai/maxa-skills

# Install the plugin
codex plugin add maxa-spec@maxa-skills
```

For other tools, see the [repository README](https://github.com/maxa-ai/maxa-skills#installation).

## Use it

Open a project that contains a Maxa spec: a folder with `maxa-spec.yaml`, or a `project.yaml` that declares `bundle_format_version`. Then ask for the work, for example "build a star schema for the general ledger" or "check my dbt models against the Maxa spec". The correct skill loads automatically. You can also start a skill directly:

```
/maxa-spec:build-data-model      # Claude Code
$maxa-spec:build-data-model      # Codex
```

The other skills follow the same pattern: `maxa-spec:check-data-model` and `maxa-spec:write-business-doc`.

If the model finds no Maxa spec, or finds more than one, it asks you which folder to use.

## Data

The plugin contains only skill instructions. It has no connectors, servers, or scripts, and it sends no data to Maxa or to any other service. The skills tell the model to read the Maxa spec files and the data model files in your project. That content is handled in the same way as any other file read in your session.

## License

MIT. See [LICENSE](https://github.com/maxa-ai/maxa-skills/blob/main/LICENSE).
