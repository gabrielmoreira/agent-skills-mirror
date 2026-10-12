# Repository Instructions

This repository holds AI-agent skills in Degardis source format; Degardis validates and compiles them into installable bundles.

## Routing

For any work that writes, reviews, assesses, improves, evaluates, or versions a skill, validates or builds one, creates a bundle, or uses the Degardis CLI: invoke and read `degardis-authoring` before planning or inspecting skill sources, or read `skills/degardis-authoring/` if it isn't installed. That skill governs authoring skills in any domain; this file governs the repository around it.

## Repository rules are not skill instructions

A skill source tells an agent how to do the skill's job wherever the bundle lands, and that agent has never seen this repository. So a skill source never mentions this repository, its trials, documentation conventions, scripts, or release process, and these `AGENTS.md` files never restate or host a skill's own rules. Delete text found on the wrong side, and add it where it belongs only if still needed.

## Layout

- Each skill lives directly in `skills/<skill-name>/`, with a unique name and no manifest in `skills/` or above.
- Tests maintained under a skill's scripts directory are part of its source, even when excluded from manifest content globs and bundles.
- `README.md` and `CHANGELOG.md` stay out of manifest content globs and bundles.

## Documentation names

A `README.md` says what a directory holds and states no rule; GitHub opens it for anyone. An `AGENTS.md` holds the rules for a session working in that directory: one per directory that owns rules, and no rule outside one. Trial fixtures are content, governed by `trials/AGENTS.md`.

## The source is authoritative

READMEs and the guides in `docs/` describe the last released bundle and lag the source by design. While working on a skill, don't read or write them: they give a stale picture of what you're editing. The release reconciles them.

## One commit, one skill

A commit changes source for at most one skill, including its tests, and never alongside a README.

Its body is the change's permanent record and the only input to the skill's next release section: state what changed and, where a reader wouldn't otherwise see it, why. Record changes to the skill's source, including its tests, whether or not the affected files ship in the bundle. Repository documentation, blind trials, and release automation belong to no skill's history. Don't add a `Co-Authored-By` trailer.

Don't touch `CHANGELOG.md`: each section is one published version, dated and linked to its release asset, and `changelog.py` accepts nothing else. A never-released skill has none; the release that first publishes it creates one.

## Elsewhere

- Reader-facing pages — the root `README.md`, a guide in `docs/`, or a skill's `README.md`: read `docs/AGENTS.md` first.
- Retiring, withdrawing, or removing a skill, released or not: read `.github/RETIRING.md` first.
- Releases, or their workflows, scripts, or templates: read `.github/AGENTS.md` first. Otherwise don't inspect `.github/`.
- Blind trials or their fixtures: read `trials/AGENTS.md` first. Otherwise don't inspect `trials/`.
