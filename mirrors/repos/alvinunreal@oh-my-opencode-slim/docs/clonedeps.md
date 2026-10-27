# Clonedeps

![Clonedeps dependency source workspace](../img/clonedeps.jpg)

`clonedeps` is a bundled Orchestrator skill that clones a small set of
important dependency source repositories into an ignored local workspace, so
agents can inspect library internals when docs are not enough.

---

## Usage

Ask the Orchestrator directly:

```text
Use clonedeps to clone the key dependency source repos for this project.
```

For a specific dependency:

```text
Use clonedeps for the OpenCode SDK so you can inspect its plugin API internals.
```

It reuses `.slim/clonedeps.json` when present, proposes a small clone plan for
approval, clones each repository once, then updates the manifest, ignore files,
and a short `## Cloned Dependency Source` section in the root `AGENTS.md`.
There is no helper script: selection is agent judgment, cloning is plain git.

---

## Files It Creates

### `.slim/clonedeps/repos/`

Ignored, read-only clones, one folder per source repository:

```text
.slim/clonedeps/repos/<owner>__<repo>/
```

The safe name comes from the repository owner/name, not the package name:
`https://github.com/anomalyco/opencode.git` →
`.slim/clonedeps/repos/anomalyco__opencode/`. Do not add version or package
suffixes; every manifest entry from one repository shares that path with a
different `packagePath`. Do not edit these clones.

### `.slim/clonedeps.json`

A small, committable manifest, read first on later runs:

```json
{
  "version": "1.0.0",
  "updatedAt": "2026-08-04T19:15:39.000Z",
  "dependencies": [
    {
      "name": "@opencode-ai/plugin",
      "resolvedVersion": "1.18.13",
      "repoUrl": "https://github.com/anomalyco/opencode.git",
      "ref": "v1.18.13@a105350812f05f914c768e468559dbd6bd508d8e",
      "path": ".slim/clonedeps/repos/anomalyco__opencode",
      "packagePath": "packages/plugin",
      "reason": "Plugin API source used by the project"
    },
    {
      "name": "@opencode-ai/sdk",
      "resolvedVersion": "1.18.13",
      "repoUrl": "https://github.com/anomalyco/opencode.git",
      "ref": "v1.18.13@a105350812f05f914c768e468559dbd6bd508d8e",
      "path": ".slim/clonedeps/repos/anomalyco__opencode",
      "packagePath": "packages/sdk/js",
      "reason": "Core SDK source used to inspect runtime behavior"
    }
  ]
}
```

### `AGENTS.md`

A short `## Cloned Dependency Source` section lists the clone paths and what
each is for, so agents do not need the manifest to know what exists.

---

## Safety Defaults

- Prefer 0-3 strong recommendations; clone at most 3-5 core dependencies.
- Use HTTPS URLs and prefer pinned tags or commit SHAs.
- Never run install, build, test, or lifecycle scripts from a clone.
- Git ignores `.slim/clonedeps/repos/`, not `.slim/clonedeps.json`; ignore-file
  edits stay inside the managed clonedeps marker blocks.

## When To Use It

Use it when source answers better than docs: debugging SDK/framework behavior,
implementing against plugin/runtime APIs, checking version-specific internals,
or reading generated types, adapters, and protocol code. Skip it for ordinary
doc lookup, tiny utilities, transitive dependencies, or well-documented
packages.
