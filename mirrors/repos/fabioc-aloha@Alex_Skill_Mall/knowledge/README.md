# Knowledge Packages

Reference material for heirs to consult on demand, not load into the brain.

## What's Different from Plugins?

| Aspect | Plugin (`.github/skills/local/`) | Knowledge (`AI-Memory/knowledge/`) |
| --- | --- | --- |
| **Loaded** | Every matching conversation | Only when heir consults it |
| **Token cost** | Always-on brain tax | Zero until read |
| **Use case** | Patterns applied repeatedly | Reference consulted occasionally |
| **Install target** | `.github/skills/local/<name>/SKILL.md` | `AI-Memory/knowledge/<name>/` |
| **Upgrade-safe** | Yes (local/ is heir-owned) | Yes (AI-Memory is heir-owned) |

## When to Use Knowledge Instead of a Plugin

| Signal | Install as |
| --- | --- |
| Heir uses it every session or most sessions | **Plugin** |
| Heir uses it once per project (planning, architecture, audit) | **Knowledge** |
| Content is >10K tokens and only relevant periodically | **Knowledge** |
| Content is behavioral rules the AI should always follow | **Plugin** |
| Content is reference data the AI should look up when asked | **Knowledge** |

## Structure

Each knowledge package is a folder under `knowledge/<category>/<name>/`:

```text
knowledge/<category>/<name>/
  knowledge.json      # manifest (required)
  README.md           # human description (required)
  *.md                # reference content files (1 or more)
```

### knowledge.json Schema

```json
{
  "name": "architecture-diagramming",
  "version": "1.0.0",
  "type": "knowledge",
  "description": "Reference for C4 diagrams, threat model visualization, and architecture documentation",
  "author": { "name": "ACT Plugin Mall" },
  "keywords": ["architecture", "c4", "diagrams", "threat-model"],
  "category": "architecture",
  "use_phase": "planning",
  "token_cost": 15000,
  "source_store": "agency-microsoft/playground",
  "install_path": "AI-Memory/knowledge/architecture-diagramming/"
}
```

Fields unique to knowledge packages:

| Field | Purpose |
| --- | --- |
| `type` | Always `"knowledge"` (distinguishes from plugin) |
| `use_phase` | When in the project lifecycle this is most useful: `planning`, `implementation`, `review`, `audit`, `periodic` |
| `install_path` | Target is `AI-Memory/knowledge/<name>/` instead of `.github/skills/local/` |

## Installation

```bash
# Copy the knowledge package to AI-Memory
mkdir -p "AI-Memory/knowledge/<name>"
cp knowledge/<category>/<name>/*.md "AI-Memory/knowledge/<name>/"
```

Or heirs can use:

```text
/mall install <name> --knowledge
```

## How Heirs Use Installed Knowledge

Once installed to `AI-Memory/knowledge/<name>/`, heirs consult it by:

1. The AI notices a topic match and reads the relevant file
2. The heir explicitly asks: "check the architecture-diagramming knowledge"
3. A prompt references it: "per AI-Memory/knowledge/..."

The knowledge is **not** auto-loaded. It's consulted on demand, keeping the brain lean.

## Categories

| Category | Use Phase | Examples |
| --- | --- | --- |
| `architecture` | planning | C4 diagrams, threat modeling, system design |
| `compliance` | audit | Regulatory frameworks, security standards, audit checklists |
| `domain-reference` | periodic | Industry standards, medical protocols, legal frameworks |
| `project-lifecycle` | planning | Quarterly planning, capacity modeling, stakeholder mapping |
| `operations` | periodic | Incident response playbooks, runbook templates |
