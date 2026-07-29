# Repository Instructions

## Repository purpose

This repository contains AI agent skills in the Degardis source format.
Degardis validates those sources and compiles them into installable AI agent
skill bundles. Treat each skill as an independently valid, buildable unit.

The authored source is `skill.yaml` plus its selected entries, workflows,
profiles, scripts, and assets. Do not edit generated `SKILL.md`,
`references/`, or `agents/openai.yaml` files as source.

## Source organization

- Store every skill directly at `skills/<skill-name>/`.
- Use lowercase, hyphenated skill directory names and make the `skill.yaml`
  `name` match its directory.
- Keep skill names unique across the repository.
- Keep skills self-contained. Do not require another skill to be installed for
  a skill to complete its outcome.
- Preserve unrelated and staged user changes.

Degardis discovers descendant `skill.yaml` files recursively and stops
descending after it finds a skill. Do not add collection manifests or nest one
skill inside another.

## Skill documentation

Leaf README files are generated repository documentation, not Degardis source
content. The root README is handwritten around generated catalog and
installation sections. Each skill's documentation source is `readme.yaml`;
keep it outside the manifest content globs so neither it nor the generated
README is copied into skill bundles.

Use the documentation hierarchy consistently:

- The root `README.md` is the user-facing catalog and installation guide.
- Each skill README explains only that skill.

Do not add collection or category READMEs under `skills/`; the root catalog is
the sole cross-skill index.

Every generated skill README must use this order:

1. Skill title.
2. A compact metadata line with version and linked license.
3. `Purpose`.
4. `When it applies`.
5. `Capabilities`.
6. `Sample prompts`.
7. `Install for your agent`.

Write `When it applies` as a neutral routing boundary:

- Prefer `This skill applies to...` or `This skill applies when...`.
- State an out-of-scope boundary when it resolves a real ambiguity.
- Do not tell the reader or agent to choose another skill.
- Do not add cross-skill recommendations or links in leaf READMEs.

Keep cross-skill navigation in the root catalog. The documentation generator
reads authoritative identity and release metadata from `skill.yaml`:

- `name`;
- `title`;
- `version`; and
- `license`.

Do not duplicate those fields in `readme.yaml`. Store only documentation fields
that are not represented in `skill.yaml`:

- `purpose`;
- `when_it_applies`;
- `capabilities`;
- `sample_prompts`; and
- `catalog.order`, `catalog.category`, and `catalog.summary`.

Set `format_version: 1`. Write `purpose` and `when_it_applies` as Markdown
block scalars, write capabilities and sample prompts as non-empty string
lists, and give every skill a unique integer `catalog.order`.

Treat `skill.yaml` and `readme.yaml` as the authoritative inputs. Keep all
reader-visible wording and Markdown structure in these templates:

- `.github/templates/skill-readme.md` owns complete leaf READMEs;
- `.github/templates/root-catalog.md` owns the root catalog section;
- `.github/templates/catalog-row.md` owns catalog row structure;
- `.github/templates/capability.md` and
  `.github/templates/sample-prompt.md` own repeated leaf list items;
- `.github/templates/root-installation.md` owns the root installation section;
  and
- `.github/templates/changelog-link.md` owns the optional changelog link.

The generator may validate inputs, calculate dynamic values, render repeated
items, and replace generated sections. It must not construct user-facing prose,
headings, table labels, or installation instructions. Do not edit a leaf README
directly.

## Versions and changelogs

Use semantic versioning for skills:

- Patch: corrections within the existing outcome and routing boundary.
- Minor: backward-compatible capabilities, profiles, or workflow additions.
- Major: incompatible routing, behavior, interface, or outcome changes.

When a skill has release history, maintain `CHANGELOG.md` in that skill's
directory. The documentation generator adds its link to the skill README
metadata line automatically. Changelog files are repository documentation and
must remain outside generated bundles.

Use this changelog structure:

```markdown
# Changelog

Significant user-visible changes to this skill are recorded here.

## Unreleased

- Describe pending user-visible changes.

## 1.1.0 — 2026-09-14

- Describe the released behavior and its impact.
```

Changelog conventions:

- Keep releases newest first and use ISO dates.
- Record changes to routing, workflows, capabilities, profiles, scripts,
  assets, interface metadata, or generated behavior.
- Omit internal reorganization and trivial documentation corrections unless
  they materially affect users.
- Do not report abandoned, experimental, or never-released behavior as release
  history.
- Do not invent release dates or backfill releases without evidence.
- When preparing a release, move applicable `Unreleased` entries under the
  released version and date.
- For a released skill, make the latest released changelog version match the
  version in `skill.yaml`.

## Validation

After changing a skill source, validate both the selected skill and the full
collection:

```console
degardis validate skills/<skill-name>
degardis validate skills
```

Build changed sources into an explicit generated directory outside authored
sources:

```console
degardis build skills/<skill-name> --output .artifacts/verification
```

Inspect the generated `SKILL.md`, `agents/openai.yaml`, references, selected
profiles, scripts, and assets. Confirm repository `README.md` and
`CHANGELOG.md` files are absent from the bundle. Remove temporary verification
artifacts after inspection.

For documentation changes:

- Run `python .github/scripts/generate-readmes.py`, then run it again with
  `--check`.
- Verify every relative link.
- Verify displayed version and license values against `skill.yaml`.
- Verify the generated root catalog contains every skill.
- Run `git diff --check`.

Never build into an authored skill directory or maintain generated artifacts
in the repository.

## Distribution

Every leaf skill README is generated end-user documentation. The root catalog
and packaged-skill guide are also generated sections. Run
`.github/scripts/generate-readmes.py` after adding or renaming a skill,
changing `skill.yaml` or `readme.yaml`, editing a README template, or changing
shared installation guidance. Do not hand-edit leaf README files or content
between generated markers in the root README.

The README templates own installation wording and agent-directory tables. The
generator must:

- supply authoritative `title`, `name`, `version`, and `license` values from
  `skill.yaml`;
- supply documentation and catalog values from `readme.yaml`;
- calculate each release asset link from the skill name and README location;
- render capabilities, prompts, catalog rows, and optional changelog links; and
- reject missing, duplicate, nested, or malformed source data.

Change installation prose, warnings, headings, table labels, agent-directory
choices, platform explanations, and ChatGPT instructions only in the
templates. Filesystem installation guidance must tell users to back up local
modifications and empty an existing skill directory before extracting an
upgrade into it.

Keep maintainer release mechanics out of leaf READMEs.

Publish downloadable bundles as complete repository snapshots. Run the
`Release skill bundles` workflow with a tag named `skills-YYYY-MM-DD`; append
`.N` when publishing more than one snapshot on the same date. The workflow
must install the published `degardis` package from PyPI, validate the full
collection, build every skill with every profile, attach every
`<skill-name>.zip`, generate release notes from the authoritative skill titles
and versions, and explicitly mark the snapshot as GitHub's latest release. A
complete asset set is required because every leaf README uses GitHub's
repository-wide `releases/latest/download/` redirect.

Snapshot tags are dated distribution identifiers, not semantic versions.
Continue to version each skill independently in its `skill.yaml`, README, and
catalog entries. Do not introduce a shared semantic version for the
collection.
