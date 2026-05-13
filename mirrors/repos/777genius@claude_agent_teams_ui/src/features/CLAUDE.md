# Feature-Local Guidance

This file is a navigation layer for feature slices under `src/features/`.

Before changing a feature slice, read:

- [Project instructions](../../CLAUDE.md)
- [Feature Architecture Standard](../../docs/FEATURE_ARCHITECTURE_STANDARD.md)
- [Feature root guide](./README.md)

Use local references:

- `src/features/recent-projects` - full cross-process reference
- `src/features/member-work-sync` - full feature with a root public barrel
- `src/features/member-log-stream` - full feature with `main/application/`
- `src/features/agent-graph` - thin `core/domain` plus `renderer` reference

Default location for new feature work:

- `src/features/<feature-name>/`

Before adding or moving code:

- decide whether the feature is full, thin, or process-limited
- add only the layers the feature actually owns
- expose production callers through public entrypoints only
- keep tests close to the layer they verify under `test/features/<feature>/` or
  feature-local `__tests__` when that is the established local pattern

Do not duplicate architecture rules here. Keep architecture rules centralized in
[../../docs/FEATURE_ARCHITECTURE_STANDARD.md](../../docs/FEATURE_ARCHITECTURE_STANDARD.md).
