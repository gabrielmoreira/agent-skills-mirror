# AGENTS.md

Vendored ACE core classes.

- Treat generator, reflector, and curator behavior as upstream-owned unless a compatibility patch is required.
- Prefer benchmark-specific behavior in `src/systems/ace/system.py`.
- Keep changes minimal and compatible with the ACE adapter imports.
