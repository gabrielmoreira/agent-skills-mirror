<img src="assets/banner.svg" alt="Alex ACT Plugin Mall" width="100%"/>

# Alex ACT Plugin Mall

The plugin marketplace for ACT (Artificial Critical Thinking) agents and heirs. Curated plugins that extend the capabilities of Alex ACT Edition and any AI agent that reads `.github/` files.

## What's Here

301 plugins organized into 16 categories, plus knowledge packages for on-demand reference material. Each plugin is a self-contained folder with a human-readable README, machine-readable manifest (`plugin.json`), brain artifact (`SKILL.md`), and optional instructions, prompts, or muscles.

**Knowledge packages** (`knowledge/`) are reference material installed to `AI-Memory/knowledge/` instead of the brain. They cost zero tokens until consulted -- ideal for architecture planning, compliance audits, and other periodic tasks.

Install plugins into any ACT heir project without losing them to Edition upgrades.

| Metric | Value |
| --- | --- |
| Plugins | 301 |
| Categories | 16 |
| Shape types | 7 (see notation below) |
| Install path | `.github/skills/local/` (or matching `local/` dirs) |
| Primary consumer | Alex ACT Edition v1.2.0+ |
| Also works with | GitHub Copilot, Claude, Cursor, Windsurf, any AI reading `.github/` |

## Quick Start

```bash
# Clone the Mall
git clone https://github.com/fabioc-aloha/Alex_Skill_Mall.git

# Install a plugin to your project
cp -r Alex_ACT_Plugin_Mall/plugins/converters/md-to-word/ \
  /your/project/.github/skills/local/md-to-word/
```

Then reload your AI agent. The plugin is now available.

## From ACT Edition

If you're running Alex ACT Edition, use the in-session commands:

```text
/mall search azure cosmos
/mall install md-to-word
```

Plugins install into `local/` paths so Edition upgrades never clobber them.

## Browse the Mall

Three axes for discovery: **category** (what domain), **shape** (how complex), **tier** (how specialized).

### Categories (301 plugins)

| Category | Count | Coverage |
| --- | --- | --- |
| [Security & Privacy](plugins/security-privacy/) | 30 | XSS, injection, secrets, threat modeling, SFI compliance, responsible AI |
| [DevOps & Process](plugins/devops-process/) | 30 | Git workflow, release, deployment, CI/CD, project management, PM planning, SDLC, Atlassian, product |
| [Documentation](plugins/documentation/) | 26 | Mermaid, diagrams, docs decay, VitePress, publishing, version stamps |
| [Cloud & Infrastructure](plugins/cloud-infrastructure/) | 24 | Azure, Fabric, IaC, Bicep, deployment, cost optimization |
| [Code Quality](plugins/code-quality/) | 25 | Code review, testing, audit patterns, refactoring, coverage, adversarial review |
| [AI & Agents](plugins/ai-agents/) | 19 | MCP servers, agent design, RAG, prompt engineering, evals |
| [Media & Graphics](plugins/media-graphics/) | 22 | Banners, SVG, slides, presentations, video, image handling, deck building |
| [Data & Analytics](plugins/data-analytics/) | 25 | Power BI, KQL, Fabric, dashboards, data visualization, semantic models |
| [Reasoning & Metacognition](plugins/reasoning-metacognition/) | 15 | ACT pass, hypothesis debugging, root cause, calibration |
| [Platform & Tooling](plugins/platform-tooling/) | 14 | VS Code, cross-platform, Node.js, frontend patterns |
| [Architecture & Patterns](plugins/architecture-patterns/) | 13 | Microservices, saga, API design, workflow orchestration |
| [Supervisor & Fleet](plugins/supervisor-fleet/) | 14 | Fleet governance, Mall curation, release ritual, AI-Memory setup |
| [Domain Expertise](plugins/domain-expertise/) | 15 | Healthcare, legal, finance, game design, marketing, regulatory, executive leadership |
| [Converters](plugins/converters/) | 13 | Word, HTML, email, PDF, EPUB, LaTeX, PPTX, plain text, Loop |
| [Communication & People](plugins/communication-people/) | 9 | Stakeholder management, coaching, collaboration |
| [Academic & Research](plugins/academic-research/) | 7 | Paper drafting, citations, survey verification, lit review |

### Shape Notation

Shape tells you what a plugin contains before you open the folder:

| Shape | Contents | Complexity |
| --- | --- | --- |
| `.S..` | Skill only | Minimal (1 file) |
| `I...` | Instruction only | Minimal (1 file) |
| `.S.M` | Skill + muscle | Light (2 files) |
| `ISP.` | Instruction + skill + prompt (trifecta) | Medium (3 files) |
| `I.P.` | Instruction + prompt | Medium (2 files) |
| `ISPM` | Full stack | Heavy (4+ files) |
| `I...L` | Lock (boundary guard) | Minimal but critical |

Position key: **I**nstruction, **S**kill, **P**rompt, **M**uscle. A dot means that artifact type is absent.

## Plugin Structure

Each plugin is a self-contained folder:

```text
plugin-name/
  README.md          Human-readable: what, why, when, prerequisites
  plugin.json        Machine manifest: shape, artifacts, dependencies, token cost
  SKILL.md           Brain artifact (the actual rules or knowledge)
  *.instructions.md  Optional instruction artifact
  *.prompt.md        Optional prompt artifact
  *.cjs              Optional muscle (executable code)
```

## Machine-Readable Discovery

[CATALOG.json](CATALOG.json) enables programmatic search:

```bash
# Search by category
jq '.plugins[] | select(.category == "security-privacy")' CATALOG.json

# Filter by shape
jq '.plugins[] | select(.shape == "ISP.")' CATALOG.json

# Find plugins under N tokens
jq '.plugins[] | select(.token_cost < 500)' CATALOG.json
```

## Curation

The [Alex ACT Supervisor](https://github.com/fabioc-aloha/Alex_ACT_Supervisor) maintains this Mall. Plugins are evaluated on maintenance health, adoption signal, license clarity, ACT-Edition fit, and documentation quality. Stale plugins are pruned quarterly.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Plugins must solve a real problem, save meaningful time, and encode knowledge that isn't a quick search away.

## License

MIT. See individual plugin folders for any additional license terms.
