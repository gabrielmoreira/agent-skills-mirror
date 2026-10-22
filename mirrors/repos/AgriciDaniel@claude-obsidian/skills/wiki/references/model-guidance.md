# Model and host compatibility

The canonical skills describe outcomes, evidence and mutation boundaries. Let
the host select its model; do not bake a model name or host-only frontmatter
into portable workflows. Keep private reasoning private and report the answer,
supporting evidence, actions and unresolved limits.

For Opus 5.5, start a controlled evaluation at its default `medium` effort and
measure quality, latency and usage before changing it. Its thinking is always
adaptive. API adapters must read content blocks by type, handle refusal and
incomplete output, and avoid forced tool choice. Existing clear prompts do not
need a wholesale rewrite merely because the model changed.

When building a prompt from source text, use a fresh application-generated
delimiter, encode source fields safely and state that the enclosed text is
untrusted data. A delimiter is defense in depth, not proof of injection
resistance. Validate generated artifacts independently before using them.

Primary guidance, reviewed 2026-10-17:

- [Opus 5.5 prompting](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)
- [Opus 5.5 migration](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)

For an acceptance run, record exact model and host versions, skill hashes,
fixture hashes, effective options, tool permissions and usage. Use synthetic
sources in a disposable vault and compare paired conditions on the same cases.
Keep offline, model, host-loading and native Obsidian evidence separate. Never
infer permission to send a private vault to a provider from a local test.
