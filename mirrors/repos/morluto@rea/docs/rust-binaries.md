# Rust binary dependency metadata

`inspect_rust_binary` / `inspect-rust-binary` answers which crate names,
versions, sources, and dependency edges are embedded by cargo-auditable in one
selected local executable or library. It reads the file without running it and
requires no Rust installation, active binary target, Hopper, Ghidra, or IDA.

```bash
rea inspect-rust-binary /absolute/path/to/application --json
```

The CLI resolves relative paths against the caller's working directory. MCP
requires an absolute filesystem path and preserves that exact selection:

```json
{
  "name": "inspect_rust_binary",
  "arguments": { "path": "/artifacts/application" }
}
```

## Observations

Complete delivery remains the default. For a dependency question, select the
needed records on the first call instead of returning the complete graph:

```json
{
  "name": "inspect_rust_binary",
  "arguments": {
    "path": "/artifacts/application",
    "view": {
      "collection": "packages",
      "names": ["serde", "serde_derive"],
      "fields": ["name", "version", "source", "dependencies"]
    }
  }
}
```

`detail: "summary"` returns section ranges, root index, package/edge/cycle counts
and compiler-hash count. A `view` selects compact delivery automatically;
combining it with explicit `detail: "complete"` is an input error. The complete
parent Evidence is retained in the MCP session and remains exportable. Subsequent
`inspect_analysis_view` calls accept that `parent_evidence_id`, or its portable
Evidence file, without reopening the binary:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "ev_<parent digest>"
  },
  "view": {
    "kind": "rust",
    "collection": "edges",
    "from_indices": [12],
    "limit": 20
  }
}
```

Package filters accept exact `names`, `versions` and original `indices`; edge
filters accept original edge `indices`, `from_indices` and `to_indices`.
Filters intersect, and an empty filter array selects nothing. `offset` counts
matching records; `limit` defaults to 64. Pages retain original indices scoped
to the parent Evidence, selected fields, examined coverage and the next offset.
Default package fields omit dependency vectors; explicitly select
`dependencies` to obtain direct references. No dependency path is traversed.

The CLI uses the same views and requires an exclusive output bundle for compact
delivery so the complete Evidence survives process exit:

```bash
rea inspect-rust-binary /artifacts/application --json \
  --view '{"collection":"packages","names":["serde"],"fields":["name","version"]}' \
  --evidence_output /artifacts/rust-evidence.json
```

Compact results distinguish complete embedded-record coverage from unknown
runtime dependency coverage. A missing section remains unknown rather than an
empty dependency set. Retained views describe the captured artifact digest;
they do not assert that the current file or running application is unchanged.

The inline Evidence result contains the artifact path, SHA-256, byte length,
container format, architecture, word size, and byte order. When a `.dep-v0`
section is present, `auditable_metadata` contains:

- `section_name`, `.dep-v0` for ELF and PE or `__DATA,.dep-v0` for Mach-O;
- `file_offset` and `section_bytes`, the exact file range of the compressed section;
- `compressed_bytes` and `uncompressed_bytes`;
- `format_version`, the embedded integer, or `null` when the field is omitted;
- `packages`, in the section's original order, with `name`, `version`, `source`,
  `kind`, `dependencies`, and `root`;
- `root_package_index`, the single package marked `root`, or `null` when none is marked;
- `dependency_edges`, pairs of package indices in package-then-dependency order;
- `cyclic_dependency_indices`, sorted unique indices that participate in a cycle.

An omitted `kind` stays `null`. The embedded format treats that omission as
runtime, and that default is not stored in the section. An omitted dependency
list is an empty array. An omitted `root` flag is false.

`rustc_commit` is present only when a `/rustc/<40-hex>/` path is found in
read-only data. Its `evidence_kind` is `inferred`. The hash is not a claim that
that compiler produced the binary. Several distinct hashes leave a single
commit unknown.

## Limits and failures

The selected file is limited to 256 MiB. A dependency section is limited to 1
MiB compressed. Inflated JSON is limited to the smaller of 8 MiB and 64 times
the compressed size. The complete report is limited to 8 MiB. Empty sections,
truncated or trailing zlib bytes, invalid JSON, unknown fields, dependency
indices outside the package list, more than one root package, and compressed
dependency sections are typed failures. A cycle is reported and is not walked.

A missing section returns success with `auditable_metadata: null` and a
limitation. Absence of `.dep-v0` does not mean the binary has no dependencies.
Unknown embedded format revisions are retained in `format_version` and
interpreted using the highest known preceding revision, following the
cargo-auditable schema. The output includes a limitation that identifies this
fallback and notes that the particular revision has not been independently
verified. An omitted revision remains `null` and follows revision 0 semantics.
Embedded names and versions are file content. They do not authenticate the
packages or the compiler.

ELF, PE, thin Mach-O and one selected slice of a universal Mach-O are the
supported containers.
A universal (FAT) Mach-O needs `architecture` (`x86`, `x86_64`, `arm`
or `arm64`; CLI `--architecture`). REA reads its own FAT table, without `lipo`,
and validates the selected slice's range, alignment and Mach-O header CPU
against the table. The result keeps the universal file as `artifact` (its
SHA-256 and size), adds `selected_slice` with the slice offset, length, raw CPU
type/subtype and the FAT table digest, and reports the section and rustc-path offsets as a
file offset inside that slice. Without `architecture`, or when the file has no
such slice or several, the request fails on `architecture` and lists the slices
present. `architecture` on any other image is rejected rather than ignored.

Package and dependency counts are checked against the minimum required JSON
representation before graph allocation or schema cloning. Oversized graphs
report the output byte budget; the compiler-path capacity reports
`maximum_rustc_hashes` in hashes, independently of byte limits.
