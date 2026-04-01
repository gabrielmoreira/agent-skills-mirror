# Container skills (runtime)

Skills here are **copied recursively** into each group’s session at `data/sessions/<group>/.claude/skills/` and mounted in the agent container as `/home/node/.claude/skills/`.

Anything the WhatsApp / WeCom / Discord / local-web agent should use belongs **here**, not only under `.claude/skills/`.

## Layout

| Directory | Role |
|-----------|------|
| `bio-tools/` | Bio CLI + Python recipes; `templates/` holds runnable plot/PyMOL scripts |
| `agent-browser/` | Browser automation skill |
| `sds-gel-review/` | SDS gel image review |
| `query-*` | Database / API usage (Ensembl, UniProt, KEGG, …) |
| `blast-search/`, `pubmed-search/`, `sequence-analysis/` | Literature & sequence workflows |

## Developer-only skills

Meta skills that teach **how to change the repo** (setup, add-telegram, convert-to-docker, `add-figure`, etc.) stay in **`.claude/skills/`** at the project root.
