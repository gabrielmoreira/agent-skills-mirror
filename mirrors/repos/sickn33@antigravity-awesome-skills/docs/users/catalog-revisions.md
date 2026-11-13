# Pin a catalog revision independently of the runtime

Starting with runtime 19.10.1, AAS can load a compatible catalog revision without installing a new CLI or MCP release. Existing installations continue to use their embedded catalog until you explicitly select another one. Nothing updates automatically.

A runtime has a software version, such as `19.10.1`. An independent catalog has its own revision, source commit and content digest. Read `catalog-release.json` attached to the corresponding `catalog-vREVISION` GitHub release. It identifies the exact archive integrity and minimum compatible runtime; do not substitute an integrity value from an untrusted message.

## Import verified catalog data

Use an explicit absolute cache directory and the exact revision and SRI from the published descriptor:

```sh
aas catalog update --cache-root /absolute/aas-cache --revision CATALOG_REVISION --integrity 'EXACT_SHA512_SRI'
```

Replace both uppercase placeholders with published values. This imports catalog data and complete skill support files; it does not change any host configuration or install skills into a project. The downloader verifies integrity, schema, complete asset digests and runtime compatibility before promoting the cache entry. A mismatched revision, altered archive or incompatible runtime fails without replacing an existing catalog.

For an archive already downloaded from the release, add `--archive /absolute/catalog.tgz`; the same integrity and compatibility checks apply. Once cached, the catalog is available offline.

## Pin the local MCP

Preview a configuration patch using the catalog digest returned by the import:

```sh
aas mcp configure --host codex --scope user --config /absolute/codex/config.toml --cache-root /absolute/aas-cache --version 19.10.1 --catalog-digest 'EXACT_CATALOG_DIGEST'
```

Replace the paths and digest with your own values. Use `--host claude` for Claude. Inspect the proposed patch and the exact runtime identity before supplying the approval digest returned by the command. Importing a catalog alone never approves a host change. A configuration update and a running client's session reload are separate actions.

The MCP reads the pinned verified catalog and skill files locally. It does not fetch a newer revision or execute bundled skill scripts while searching or reading.

## Preserve and roll back a selection

Create stacks with an explicit `--catalog-digest` and `--cache-root`. The stack manifest records catalog identity, while a plan for an independent catalog additionally requires `--runtime-version` to select a separately verified compatible runtime. Keep the runtime cache identity and approval workflow described in [AAS Core](aas-core.md).

A different catalog digest requires a new stack manifest and plan; an old approved plan never silently follows a newer catalog. Previous verified catalog revisions remain independently addressable in the cache. To roll back, explicitly select the previous digest, regenerate the plan and review the resulting changes. Do not edit cache files or overwrite an immutable release revision.

## Distribution boundaries

Catalog-only publication does not bump or republish npm. Codex/Claude plugin marketplace snapshots in the repository remain aligned with the last prepared runtime distribution; this catalog update command does not silently update installed marketplace plugins. Source `main` may contain newer skills than those distribution snapshots. The live catalog's `catalog-release.json` identifies the independently deployed revision.
