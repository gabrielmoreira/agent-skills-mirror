---
mode: agent
description: Discover and inspect optional plugins under .ai/plugins/. Lists manifests, status, capabilities, and offers to run any read-only discovery scripts each plugin ships.
---

# /ai-plugin-discover

Inspect the `.ai/plugins/` directory: enumerate every plugin, summarise its manifest, and (with user permission) run any discovery probes the plugin ships under `scripts/detect-*`.

This command is **read-only**. It never enables, disables, or configures a plugin.

The plugin contract is defined in [.ai/plugins/README.md](../../.ai/plugins/README.md). Read it before acting if the structure looks unfamiliar.

---

## Steps

### 1. Enumerate

List every subdirectory of `.ai/plugins/` that contains a `plugin.yaml`. For each, print:

- Plugin name (from manifest, must match directory name)
- `version`
- `status` (`disabled` / `experimental` / `stable`)
- One-line `description`
- Capabilities (`provides.capabilities`, joined)
- Frontmatter fields contributed (`provides.frontmatter_fields`)
- Slash commands contributed (`provides.slash_commands`)
- Validator checks contributed (`provides.validator_checks`)

Group output by `status:` — surface `stable` first, then `experimental`, then `disabled`.

### 2. Manifest sanity

For each plugin, warn (do not fail) when:

- `name:` does not equal the directory name.
- `status:` is not one of the three allowed values.
- A declared slash command does not exist under [`.github/prompts/`](../prompts/).
- A declared governed tool does not exist under the plugin's `tools/`.
- A required field is missing.

### 3. Probe (optional, prompted)

For each plugin, list any executable discovery scripts found at `scripts/detect-*.ps1` (Windows) or `scripts/detect-*.sh` (POSIX). Ask the user whether to run them.

If the user agrees, run each via the project's shell ([.github/dev-specs.md](../dev-specs.md)) and stream the output. These scripts MUST be read-only per the plugin contract; if a script attempts to install or modify state, halt and report.

### 4. Summary

Print:

- Count of plugins: total / stable / experimental / disabled.
- Count of warnings raised.
- A reminder pointing to [.ai/plugins/README.md → Adopter Workflow](../../.ai/plugins/README.md#adopter-workflow) for how to enable a disabled plugin.

---

## Constraints

- Never modify `plugin.yaml`, tier files, or any other plugin content.
- Never run a script outside a plugin's `scripts/` directory.
- If `.ai/plugins/` does not exist or is empty, say so and exit cleanly — the framework is fully functional without plugins.
