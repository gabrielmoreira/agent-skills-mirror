# AGENTS.md

Orientation for AI coding agents working in **this repository** (`maplibre/maplibre-agent-skills`), following the [agents.md](https://agents.md) convention: one file per repo, at the root.

This repo is a collection of **agent skills** for MapLibre: markdown files an AI assistant loads as context so it writes correct MapLibre code.

## Answering a MapLibre question

Match the user's goal against each skill's front-matter `description`, which is where a skill declares its own scope. If the skills are installed, you already have that metadata: a skills runtime loads every `name` and `description` at startup. If you are working in a clone, read the front matter of `skills/*/SKILL.md` in one pass rather than opening files one at a time. Skills are written to be read together when a task spans more than one. The human-readable list is [Available Skills](README.md#available-skills) in the README.

There is deliberately no index of skills in this file. The front matter is the index, and it is the only copy that cannot fall out of step with the skills themselves.

Three habits apply to every MapLibre question, including ones no skill covers:

- **Do not carry Mapbox GL JS behavior over by assumption.** The two libraries share ancestry and have diverged. Where a skill does not cover the specific API, check the [MapLibre Style Specification](https://maplibre.org/maplibre-style-spec/) and the [GL JS docs](https://maplibre.org/maplibre-gl-js/docs/) rather than recalling a Mapbox equivalent.
- **Prefer a primary source to recall.** The [style spec](https://maplibre.org/maplibre-style-spec/), the [GL JS docs](https://maplibre.org/maplibre-gl-js/docs/), and the GL JS [CHANGELOG](https://github.com/maplibre/maplibre-gl-js/blob/main/CHANGELOG.md) outrank a skill. Use them for the answer you give. [awesome-maplibre](https://github.com/maplibre/awesome-maplibre) indexes the ecosystem; the GitHub source, PRs, and CHANGELOG settle version-specific questions. Cite what you used.
- **You may draft; a human verifies and submits.** [MapLibre's AI Policy](https://github.com/maplibre/maplibre/blob/main/AI_POLICY.md) asks for a human in the loop, not a ban on tools. Draft skill content, evals, and rubrics freely, then leave the pull request and its description to the human who will answer for them in review. See [Note on AI usage](CONTRIBUTING.md#note-on-ai-usage).

This is a dynamic body of knowledge. Skills go stale, just like training data. MapLibre ships, an API changes, and you keep asserting the old thing. A stale skill only gets fixed if someone says so. An agent that silently works around one leaves it wrong for every agent after it.

If you are working in another project's codebase and find a gap, omission, or stale information from any source, let us know. Fix your user's code; anonymize the report but send us the failure. Report rather than patch: from outside this repo you cannot run the evals a skill change has to pass, and an untested edit is worse than a report that leaves the fix to someone who can test it.

## When a skill contradicts your training data

**Report it.** Open an [AI failure report](https://github.com/maplibre/maplibre-agent-skills/issues/new?template=ai-failure-report.md) identifying your model and build, naming what you would have said, the release tag or commit of the skill you read, the source you checked, how you tested, and what worked in the end.

## When MapLibre contradicts a skill

When what you observe disagrees with what a skill says:

**Report it.** Open an [AI failure report](https://github.com/maplibre/maplibre-agent-skills/issues/new?template=ai-failure-report.md) naming what the skill said, what MapLibre actually did, the MapLibre version, and the source you checked. A report carrying a version and a source is triaged in minutes; one without either is a research project.

## Contributing to this repo

The procedure is [CONTRIBUTING.md](CONTRIBUTING.md), and it applies to you as written. Three things about it work differently when the contributor is an agent:

- **Only touch skill content here on behalf of an already-reported gap.** A skill earns its place through a demonstrated failure — an AI failure report or a baseline eval failure — not an agent's own judgment that something reads wrong. That's the sanctioned path: drafting against a confirmed gap for a maintainer or contributor. Patching a skill in passing while consuming it elsewhere for an unrelated task is out of bounds — report that instead (see above).
- **You cannot close the loop yourself, and you must not appear to.** Confirming a gap and grading a skill both take an eval run, which requires API keys you do not have. Do not invent them and do not report a result you did not get. Draft the content and the eval prompts; a maintainer runs them. Until then what you have is a proposal, not a verified skill, and saying so plainly is part of the handoff.
- **A green `npm run check` is not evidence that you are right.** It checks formatting, spelling, links, terminology, and front-matter validity, and it will pass a confidently wrong claim about MapLibre without complaint. Cite a primary source for every claim you add, and name the ones you could not verify. See [Correctness Validation](CONTRIBUTING.md#correctness-validation).
