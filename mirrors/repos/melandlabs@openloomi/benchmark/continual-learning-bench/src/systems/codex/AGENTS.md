# AGENTS.md

Codex CLI system adapter.

- Preserve Docker workspace isolation, `single_conversation` resume behavior between instances, hard reset behavior, and JSONL event parsing.
- Skill invocation and prepended skill text are conversation bootstrap only. In `skill` mode, prompts contain only `$<skill-name>`, never the skill body. In `prepend` mode, prompts contain the skill body. Resumed/repair Codex turns must not include either.
- Native Codex memories are enabled by default with the CLI memory flag. `disable_native_memories` only omits that CLI flag; it must not change memory snapshotting.
- File memory is the union of existing `.codex/memories` files and the configured `other_memory_files` workspace watch list. Trace metadata records only `memory_files` snapshots (relpath → contents); the artifact exporter writes captured files under `<artifact_dir>/memory/`.
- Keep schema prompting, JSON extraction, validation, and token usage extraction consistent with the benchmark trace model.
- Keep container paths and CLI flags localized to this adapter.
