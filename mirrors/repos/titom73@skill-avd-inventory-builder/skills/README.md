# Skills

## What is a Skill?

A **skill** is a reusable expert methodology that defines:

- A role and area of expertise
- Principles and best practices
- An expected response structure
- Templates and examples

**Use a skill when you want to:**

- Generate or review configurations according to a standard
- Validate design patterns
- Enforce a consistent response structure
- Inject business conventions

---

## Modular Structure (Option B)

Each skill uses a **3-tier architecture** to support different AI platforms:

```text
<skill>/
├── core.md       # Essential instructions (source of truth)
├── claude.md     # Full version (core + templates + examples)
└── copilot.md    # Condensed version (based on core)
```

### Why This Structure?

| Aspect        | Claude Code                   | GitHub Copilot             |
| ------------- | ----------------------------- | -------------------------- |
| **Context**   | ~200k tokens                  | ~8k tokens recommended     |
| **Usage**     | Long, detailed sessions       | Fast inline suggestions    |
| **Format**    | Long documents with examples  | Concise instructions       |
| **Templates** | Full templates included       | Short snippets preferred   |

### Benefits

1. **Single source of truth**: `core.md` contains shared expert logic
2. **No duplication**: Principles are maintained in one place
3. **Platform optimization**: Each version is adapted to constraints
4. **Easy maintenance**: Modifying `core.md` propagates changes

### Content by File

| File         | Content                                                           |
| ------------ | ----------------------------------------------------------------- |
| `core.md`    | Role, principles, best practices, response structure              |
| `claude.md`  | Core + templates, decision trees, examples, matrices              |
| `copilot.md` | Condensed version aligned with core, optimized formatting         |

---

## Available Skills

| Skill                                     | Description                                          | Claude | Copilot |
| ----------------------------------------- | ---------------------------------------------------- | ------ | ------- |
| [eos-fabric-design](./eos-fabric-design/) | Arista EOS fabric design (EVPN/VXLAN, MLAG, BGP)     | ✅     | ✅      |
| [avd](./avd/)                             | PyAVD for EOS config generation                      | ✅     | ✅      |

---

## Installation

### Claude Code

1. Add the `<skill>/claude.md` file to the `.claude/` folder of your project
2. Or use the command: `claude project add-instructions <skill>/claude.md`

### GitHub Copilot

1. Create a `.github/copilot-instructions.md` file at the root of the repo
2. Copy the content of `<skill>/copilot.md`
3. Or use the script: `../scripts/install.sh copilot skill <skill-name> /path/to/repo`

---

## Create a New Skill

1. Copy the `_templates/` folder to a new folder
2. Rename according to the skill domain
3. Create `core.md` with essential instructions
4. Create `claude.md` that extends core with templates and examples
5. Create `copilot.md` condensed version based on core
6. Update this README

See [_templates/](./_templates/) for templates.
