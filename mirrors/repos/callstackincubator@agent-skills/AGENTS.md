# Agent Skills

Markdown-only repo with agent skills for React Native and GitHub workflows. No build step.

## Adding New Skills

Follow [agentskills.io spec](https://agentskills.io/specification) and [Claude Code best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### Quick Checklist

1. Create `skills/<skill-name>/SKILL.md`
2. Directory name must match `name` field exactly
3. Required frontmatter:
   ```yaml
   ---
   name: skill-name          # lowercase, hyphens only, 1-64 chars
   description: Third person description of what it does. Use when [trigger conditions].
   ---
   ```
4. Optional frontmatter: `license`, `metadata` (author, tags), `compatibility`
5. Keep body under 500 lines
6. Use markdown links: `[file.md](references/file.md)` not bare filenames
7. Run `/validate-skills` to verify

### What Makes a Good Skill

- **Concise**: Only add context Claude doesn't already have
- **Third person description**: "Processes X" not "I help with X"
- **What + When**: Description says what it does AND when to use it
- **One-level deep**: Reference files link from SKILL.md, not from other references
- **No redundancy**: Don't repeat description content in body

## Repo Structure

```
skills/
├── react-native-best-practices/
│   ├── SKILL.md                    # Main entry point with quick reference + problem→skill mapping
│   └── references/
│       ├── images/                 # Visual references (profiler screenshots, diagrams)
│       ├── js-*.md                 # JavaScript/React skills
│       ├── native-*.md             # iOS/Android native skills
│       └── bundle-*.md             # Bundling & app size skills
│
├── react-native-tv-best-practices/
│   ├── SKILL.md                    # Main entry point with priority framework + problem→reference routing
│   └── references/
│       ├── focus-*.md              # Focus / D-pad navigation
│       ├── nav-*.md                # Directional navigation & keyboard
│       ├── design-*.md             # 10-foot design (typography, layout, color)
│       ├── perf-*.md               # TV performance (lists, memory, animations)
│       ├── video-*.md              # Video streaming, players, DRM
│       ├── a11y-*.md               # TV accessibility
│       ├── setup-*.md              # Cross-platform setup & architecture
│       ├── test-*.md               # Testing strategy
│       └── release-*.md            # CI/CD
│
└── github/
    ├── SKILL.md                    # Main entry point with workflow patterns
    └── references/
```

All reference files are flat in `references/` — no subfolders. Prefix groups related skills.

## When Editing

- Follow format of existing reference files
- Keep "Quick" sections ≤10 lines
- Update `SKILL.md` tables when adding/removing references
- Maintain bidirectional "Related Skills" links

## Details

- [Skill file conventions](./docs/skill-conventions.md)
- [AI assistant integration guide](./docs/ai-assistant-integration.md)
