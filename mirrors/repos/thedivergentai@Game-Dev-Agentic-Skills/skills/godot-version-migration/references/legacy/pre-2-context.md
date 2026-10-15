# Legacy: Godot 1.x / early 2 (archaeology)

Tier **C** — there is no official `upgrading_to_godot` tutorial for 1→2. Use release notes, the [download archive](https://godotengine.org/download/archive/), and [GitHub releases](https://github.com/godotengine/godot/releases). Oldest common docs host: [Godot 2.1 docs](https://docs.godotengine.org/en/2.1/).

## Honesty gate

- **Prefer rewrite** on latest 3.x or library target (4.7+) for small projects.
- Large art/audio libraries: extract assets, rebuild scenes/scripts on modern Godot.
- **NEVER** claim automatic 1.x→4.x conversion.

## Next hops

1. If somehow on 2.x already → [2-to-3.md](2-to-3.md)
2. Stabilize on latest 3.x → [../bridges/3-to-4.md](../bridges/3-to-4.md)
3. Then 4.x minor hops via [../hop-index.md](../hop-index.md)
