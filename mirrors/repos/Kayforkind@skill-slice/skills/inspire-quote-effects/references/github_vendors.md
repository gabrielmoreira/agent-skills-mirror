# GitHub vendors (patterns to adapt — do not blindly npm-install everything)

Prefer **copying small MIT snippets** into pack `components/` with a source URL header. Heavy deps only when the pack already uses them.

## Tier 1 — use first

| Repo | Stars / notes | Steal |
|------|---------------|--------|
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Official | `@remotion/transitions` (`fade`, `slide`, `wipe`, `clockWipe`), `OffthreadVideo`, `noise` |
| [av/remotion-bits](https://github.com/av/remotion-bits) | ~436 · registry of bits | `AnimatedText`, word/char stagger, glitch-in, typewriter, particle system, gradient transition — **best open catalog** |
| Local sibling `quotes/spider-man/remotion` | In-repo | `CaptionWordReveal`, `SceneEffects` (Glitch/FilmBurn/PunchZoom) |

## Tier 2 — inspect for ideas

| Repo | Steal |
|------|--------|
| [DojoCodingLabs/remotion-superpowers](https://github.com/DojoCodingLabs/remotion-superpowers) | Captions, transitions, production plugins (Claude) |
| [lifeprompt-team/remotion-scenes](https://github.com/lifeprompt-team/remotion-scenes) | Scene templates |
| [reactvideoeditor/clippkit](https://github.com/reactvideoeditor/clippkit) | Editor primitives |
| [Remocn/remocn](https://github.com/Remocn/remocn) | Remotion component ecosystem |

## GLM-listed names (verify before vendor)

Some planner suggestions may be stale/missing on GitHub. Always `gh api repos/<owner>/<name>` before cloning. If 404, implement the effect yourself from this skill’s catalog + remotion-bits.

## License discipline

- Prefer MIT / Apache-2.0
- Put `// source: https://github.com/...` at top of vendored files
- Do not vendor full three.js stacks unless the composition needs 3D
