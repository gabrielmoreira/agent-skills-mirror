---
name: autoreview
description: Structured code review through the shared OpenClaw agent-skills installation.
---

# Auto Review

- Use canonical [autoreview skill](https://github.com/openclaw/agent-skills/tree/main/skills/autoreview).
- Before reviewing: read complete installed `~/.agents/skills/autoreview/SKILL.md`
  + required references. Another operator-selected location: use that installation.
- Repository entrypoint contains no review implementation.

- Skill missing: reuse or clone `https://github.com/openclaw/agent-skills`;
  run `python3 scripts/install-skills autoreview` from checkout.
- Windows: use `python`. Symlinks unavailable: `--mode copy` available.

- Run shared `scripts/autoreview` helper with Python from reviewed repository;
  preserve working directory. Follow repository review requirements + canonical skill.

- Keep shared fixes/instructions upstream in `openclaw/agent-skills`.
- Update shared checkout once for all symlinked consumers; reinstall copy-mode
  skills after source update. Never add repository-local helpers or test copies.
