# Static JavaScript route inventory

`analyze_javascript_application` and `analyze_web_bundle` retain a shared
`route_inventory` alongside their existing graph and endpoint observations.
The inventory answers which route patterns the supplied code suggests, where
each pattern came from, and which parts remain unknown. It never requests a
route, executes scripts, expands a sitemap, or establishes reachability.

Select a compact view in either MCP analysis call:

```json
{
  "detail": "summary",
  "view": {
    "kind": "javascript-routes",
    "collection": "routes",
    "where": { "path_prefix": "/reports" },
    "fields": ["path", "classification", "confidence"],
    "limit": 20
  }
}
```

Keep the original analysis inputs in that call. For the CLI, pass the same
selection as `--view '<JSON>' --detail summary --evidence_output routes.json`.
The complete Evidence bundle is written without overwriting existing files.
Unselected delivery retains the existing complete result. A web-bundle summary
requires an explicit route view; application summaries also support the existing
general summary when `view` is omitted.

Use the returned `normalized_result.parent_evidence_id` with
`inspect_analysis_view` on the same connection. The CLI's exported bundle can be
reopened with `inspect-evidence-bundle`; its `records` contain the complete
Evidence. To use `inspect_analysis_view`'s `evidence-file` source, extract the
selected parent record into a separate local Evidence JSON file (that source
accepts one Evidence record, not a bundle). Views do not reopen source files or
reconnect to a browser. Historical Evidence without `route_inventory` is
unmeasured, rather than an empty route set.

Collections are `summary`, `routes`, `occurrences`, `sources`, and `unknowns`.
All row collections support exact batch `where.ids`, field selection, `offset`,
and `limit`. An explicit empty filter array matches nothing. Routes also support
exact `paths`, literal `path_prefix`, `classifications`, `mechanisms`, and
`min_confidence`; occurrences support `route_ids`, `source_ids`, and `mechanisms`;
sources support `keys` and `statuses`; unknowns support `source_ids` and `kinds`.
Follow `coverage.next_offset` until `coverage.exhausted`; a page may stop early
at the 1 MiB serialized view budget. Oversized indivisible facts return a
resource error carrying the retained parent Evidence ID.

Pattern IDs bind the exact path. Source IDs bind the source key, path, original
URL, content digest and container digest. Occurrences identify a detector mechanism at a source location; one location
may support multiple mechanisms. `source_count` counts distinct sources. Lookup IDs use 128 bits of SHA-256;
full content and inventory digests remain SHA-256. Field selection always keeps
row identity and necessary provenance. The page's deduplicated `sources` table
contains the source descriptors referenced by returned rows. Retrieve all
occurrences by route ID when independent supporting evidence matters. Source
ranges use one-based lines and zero-based UTF-16 columns with exclusive ends;
filename-only discoveries have no invented AST range.

The shared parser handles literal router calls, nested route objects, typed
`_$` trees with explicitly inferred property-name fallbacks, Next App Router
page paths, and navigation targets. It follows stable lexical bindings and
keeps unresolved parents, mutations, spreads, and dynamic fields explicit.
A selected route-builder root owns its configuration even when mutation prevents
trusting its value. Ordinary wrapper keys do not become route ancestors. Missing
outer ancestors of unbound typed subtrees remain unknown rather than invented.
Generic Next runtime path constants require a top-level application segment
supported by structural or navigation candidates across the supplied sources.
This limits framework filesystem noise, while leaving unsupported candidates
unknown. The parser shares the existing AST traversal and lexical index.

[Next dynamic segments](https://nextjs.org/docs/app/api-reference/file-conventions/dynamic-routes)
map to `:id`, `:slug+`, or `:slug*`; groups and parallel slots do not contribute
URL segments. Intercepted routes remain unresolved. A prefix before `/_next/`
is an **inferred** routing base: [assetPrefix](https://nextjs.org/docs/app/api-reference/config/next-config-js/assetPrefix)
can differ from the routing base. Every affected occurrence keeps
`unprefixed_path`, `inferred_base_path`, and low confidence. `system` classification
is explicitly a path-name heuristic; `page` uses page-file or structured/typed configuration support. Name-only
`route`/`addRoute` calls remain `unknown` because they can also register server APIs.

Known capture omissions remain inline in `summary.reported_capture_omissions`
and queryable as `unknowns` of kind `capture-omission`. Each keeps a stable gap ID,
its script-record/script-source unit, and the reported count (including `null`
for unknown). They do not invent missing script identities or source ranges.

Counts describe deduplicated patterns in the provided code sources. They are
not a denominator for complete application or capture coverage. In particular,
server-only, lazy, inaccessible, or unselected sources may be missing.
`coverage.application_routes` always remains `unknown`; parsing and candidate
enumeration have their own completeness. Static work and fact admission share
the existing 8 MiB per-source transfer ceiling, and the root inventory has an
8 MiB admission budget. Exhaustion preserves a prefix with explicit capacity;
the serialization owner also admits route facts within the actual space left by
legacy facts. `result-bytes` capacity preserves an earlier work-capacity reason;
if even that envelope cannot fit, the optional route facet remains unmeasured.
These are accounting bounds, not a claim that total process memory is 8 MiB.

Projection only reduces delivery, not analysis work. Retained immutable Evidence
can reuse validated tables through a weak cache with the snapshot's lifetime;
subject identity is checked on every query. No live state or source content is
cached as current. Use existing source selection and resource controls when
they match the investigation, keeping their partial coverage visible.
