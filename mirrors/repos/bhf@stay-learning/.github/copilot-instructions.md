# Repository conventions

This repository is a course-authoring pipeline built entirely from Copilot customization
files. The agents, skills, instructions, and hooks under `.github/` are the runtime;
`courses/` is the data they produce. `web/` is the one piece of application code: a static
Astro site that reads `courses/` and renders it.

## Course files

- Never hand-edit anything under `courses/**` outside an agent run. The pipeline is designed
  so a lesson can be regenerated; a manual edit is silently overwritten the next time it is,
  and it will not be reflected in the plan it was generated from.
  Change the artefact upstream of the problem instead, and re-run.
- `course.yaml` is the manifest. Every exclusive-stage write updates it in the same turn.
- Three files are shared: `course.yaml`, `glossary.yaml`, `.state/run-log.md`. A wave stage
  writes none of them — it reports the change and the orchestrator applies it. That is the
  only reason the wave is safe.
- Slugs are lowercase-hyphenated. Ids are `m01`, `m01-l01`, `m01-l01-o1`.
- Read the `course-state` skill before touching any course file. It carries the schema and
  the write procedure.

## The web viewer

- `web/` reads `courses/` and never writes to it. If a course renders wrong, check whether
  the artefact is wrong before changing the viewer.
- It holds no course content of its own. Anything a page displays comes from a file under
  `courses/`.
- The course-authoring rules above do not apply to `web/**`; it is ordinary TypeScript and
  Astro, and hand-editing it is the normal way to change it.
- `assessment.yaml` and `*.plan.yaml` are not rendered on purpose. They are instructor- and
  agent-facing.

## Agents

- Every subagent is `user-invocable: false`. `course-orchestrator` is the entry point.
- Stages are either exclusive or wave. Exclusive stages (audience, curriculum, outcomes,
  assessment, lesson plan) run one at a time. Wave stages (capstone, lesson content,
  exercises, quiz) all run at once, once every plan is `current`.
- No agent has the `execute` tool. Validation reaches the shell through the `PostToolUse`
  hook, which is not an agent tool.
- No agent file declares a `model:`. The pipeline is provider-agnostic, and pinning a vendor
  string in one agent breaks that.

## Validation

`.github/skills/course-state/scripts/validate.py` runs automatically after every edit via
`.github/hooks/`. To run it by hand:

```bash
./scripts/setup.sh    # once, creates .venv with PyYAML
.venv/bin/python .github/skills/course-state/scripts/validate.py
.venv/bin/python .github/skills/course-state/scripts/validate.py --strict
```

`FAIL` blocks. `WARN` marks a state that is valid midway through a write procedure but wrong
once the run stops — finish the write procedure and it clears. `--strict` turns warnings into
failures, which is what you want in CI or after a run you believe is complete.

Fix the cause of a failure, not the symptom. Numbers that disagree usually mean one side is
wrong, not that both need forcing into line.
