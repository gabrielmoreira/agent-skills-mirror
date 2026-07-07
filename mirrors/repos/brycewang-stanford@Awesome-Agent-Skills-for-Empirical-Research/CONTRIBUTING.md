# Contributing

We welcome contributions! Here's how you can help.

## Development prerequisites

Before opening a PR, run:

```bash
pip install pre-commit
pre-commit install
```

The pre-commit hooks run the same `python-compat`, `link-check`, and `frontmatter-format` checks as `make check` does in CI, so a clean local run is what reviewers will see.

## Local quality gate (one command)

```bash
make check-fast    # catalog + validate + python-compat + unit tests (~30s)
make check-full    # adds eval-harness + benchmark lanes (~5 min on warm cache)
make quickstart    # 5-minute tour of what's in this repo and where to start
```

## Skill hygiene vs. correctness

The repo reports **two columns** in [`SKILL_HYGIENE.md`](docs/SKILL_HYGIENE.md): a structural hygiene score and an eval-coverage count. The mean hygiene score is a **structural** signal (frontmatter, description, length), not a claim about whether the skill produces correct econometrics. For correctness see [`benchmark/`](benchmark/) and [`eval-harness/`](eval-harness/). When adding or modifying a skill:

- **Adding a new skill?** Update `catalog/skills.json` (run `make catalog`) and consider adding an eval scenario in `eval-harness/scenarios/`.
- **Fixing a low-hygiene skill?** Split it into `references/` (see [`LONG_SKILL_STATUS.md`](docs/LONG_SKILL_STATUS.md)) and add a one-line top-level summary.

## How to Contribute

### Recommend a New Skill

1. Fork this repository
2. Add the Skill entry in the appropriate category document under `docs/`
3. Run the local quality gate:

```bash
make catalog
make check
```

4. Submit a Pull Request

Each Skill entry should include:

- **Name**: Skill name
- **Source**: GitHub link or install source
- **Function**: One-line description of what it does
- **Workflow** (recommended): Step-by-step execution flow
- **Install** (recommended): Installation command
- **Use case** (recommended): What type of research it suits
- **License**: Upstream license and any restrictions
- **Local path**: Where the vendored skill lives under `skills/`

The generated files [`catalog/skills.json`](catalog/skills.json), [`docs/SKILL_CATALOG.md`](docs/SKILL_CATALOG.md), and [`docs/EVALS.md`](docs/EVALS.md) are rebuilt by `make catalog`; do not edit them manually.

If the contribution adds a new first-party flagship skill or changes a recommended flagship workflow, update [`evals/flagship-evals.json`](evals/flagship-evals.json) so reviewers have a regression prompt for the expected behavior.

### Fix Errors

If you find broken links, inaccurate descriptions, or outdated install instructions, please open an Issue or PR directly.

### Share Your Experience

If you used a Skill to complete empirical research, we'd love to hear about it in Issues. We may feature your case in the docs.

## Scope

This catalog lists **open-source, self-contained skills** that researchers can install and run independently. To keep every listed skill independently runnable and license-clean, we **do not include** skills whose core functionality depends on a commercial product or proprietary/paid API (e.g. tools that require an account or paid service to work).

This is not a quality judgment — such tools may be excellent. If a tool later ships a fully open, no-account, locally-runnable path (e.g. against open corpora), we're glad to revisit.

## Quality Gate

All pull requests should pass `make check`. The full gate verifies required project files, local Markdown links, `SKILL.md` frontmatter, generated catalog/provenance/audit freshness, flagship eval docs, unit tests, eval-harness coverage, and numeric benchmark recovery. See [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md) for details.

## Especially Welcome

- Skills for social science disciplines: economics, political science, sociology, public administration
- New Skill implementations for causal inference methods (DID, IV, RDD, SCM, etc.)
- Chinese-friendly Skills
- Multi-agent collaboration system case studies
- Journal-specific writing Skills (AER, QJE, etc.)

## Code of Conduct

- Be kind and professional
- Only recommend Skills you have tested or verified
- Respect original authors' licenses

## Contact

- GitHub Issues: [Open an issue](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills/issues)
- Maintained by: [CoPaper.AI](https://copaper.ai)
