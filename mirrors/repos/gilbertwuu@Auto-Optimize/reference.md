# Reference: layout, verification, adoption

Progressive disclosure; day-to-day execution starts from **[SKILL.md](SKILL.md)** and **[program.md](program.md)**.

## Directory layout

```text
repo root/
├── SKILL.md                # Skill entry
├── README.md
├── program.md
├── SKILL-GUIDE.md
├── reference.md
├── examples.md
├── scripts/
│   └── skill-verify.sh     # run from repo root
├── docs/                   # phase docs (verifiability, phase-01–04, execution)
│   ├── verifiability.md
│   ├── phase-01-spec.md … phase-04-output.md
│   └── execution.md
├── tracks/prompt-*/        # inner-loop artifacts (project)
└── index.html, assets/     # delivery examples (optional)
```

## Verify script

| Item | Detail |
|------|--------|
| Path | `scripts/skill-verify.sh` |
| CWD | **Repository root** |
| Role | Ensure each `tracks/prompt-*/` has `r01.*`; optional SHA256/bytes for `DELIVERY_FILE` vs `FINAL_TRACK_FILE` |

**Example (repo root):**

```bash
FINAL_TRACK_FILE=tracks/prompt-d/r09.html DELIVERY_FILE=index.html bash scripts/skill-verify.sh
```

Exit **0** = pass; **non-zero** = do not claim byte match. Class A/B: **`docs/verifiability.md` R4**.

## Adopting this Skill

1. Copy `SKILL.md`, `program.md`, `docs/`, and `scripts/` into the target repo root.
2. If the target already has a root `SKILL.md`, merge YAML frontmatter and `description`.
3. Adjust `tracks/` and delivery filenames; update example commands in `program.md`.
4. Optional: add host-specific rules (e.g. `.cursor/rules/`, OpenClaw config, CLI wrappers) for extra gates or waiver wording.

## Terminology

- **Delivery file**: user-visible output (e.g. `index.html`).
- **Final track file**: chosen final version from inner loop (e.g. `tracks/prompt-a/r09.html`).
- **Gate**: condition in phase docs that blocks the next phase until satisfied.
