# Skills

Agent skills for AI coding assistants (Claude Code, Cursor, GitHub Copilot, OpenCode…), installable with the [skills CLI](https://skills.sh).

| Skill | What it does |
|---|---|
| [agentstage](skills/agentstage/README.md) | Switch the assistant's persona, tone and technical focus between "stages", included or your own. |

## 🚀 Installation

```bash
npx skills add juliocebrito/skills                      # pick from the list
npx skills add juliocebrito/skills --skill agentstage   # install one directly
```

Each skill lives in `skills/<name>/`, with its own `SKILL.md` and `README.md`.

## License

[MIT](LICENSE)
