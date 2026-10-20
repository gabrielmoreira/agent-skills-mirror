# IL2CPP metadata

`inspect_il2cpp_metadata` / `inspect-il2cpp-metadata` decodes one selected local
Unity IL2CPP `global-metadata.dat` file and returns its assembly images, type
definitions and method definitions by name, namespace, index range and count,
with the header sections and serialized index widths. It reads the file without
running it and requires no Unity installation, IL2CPP binary, active target,
Hopper, Ghidra or IDA.

Metadata versions 29, 31 and 39 are supported. For example, Unity 2022.3.30f1
wrote version 29, 2022.3.62f3 wrote 31 and 6000.4.2f1 wrote 39; other Unity
releases that write these numbers have not been checked. Other versions are
rejected as unsupported. The path must name a regular file; directories and
symbolic links are rejected.

## MCP

MCP defaults to a compact summary and retains the complete decoded Evidence in
the session. MCP requires an absolute filesystem path:

```json
{
  "name": "inspect_il2cpp_metadata",
  "arguments": {
    "path": "/artifacts/Data/Managed/Metadata/global-metadata.dat"
  }
}
```

The summary retains the complete decoded Evidence in the session and returns a
linked `inspect_analysis_view` overview: artifact identity, metadata version,
index widths and `counts` (`sections`, `images`, `types`, `methods` and
`nested_types`) without rows. Use `normalized_result.parent_evidence_id` to page
the original rows without reopening or decoding the file:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "<parent_evidence_id>"
  },
  "view": {
    "kind": "il2cpp-metadata",
    "collection": "types",
    "offset": 0,
    "limit": 64
  }
}
```

Collections are `sections`, `images`, `types` and `methods`. Every returned row
includes its source `index`, scoped by artifact SHA-256 and collection. All
collections accept batch `indices`, exact `names` and `fields`. Types also accept
`image_indices`, `namespaces` and `declaring_types`; methods accept
`declaring_types`. Filters intersect, duplicate indices are returned once, and
rows retain metadata order. An empty filter selects no rows; `fields: []`
returns indices only. Omitted fields return the complete selected rows.

For example, after resolving a type index, retrieve selected method facts:

```json
{
  "source": {
    "kind": "retained-evidence",
    "evidence_id": "<parent_evidence_id>"
  },
  "view": {
    "kind": "il2cpp-metadata",
    "collection": "methods",
    "declaring_types": [1555],
    "names": ["SendMessage"],
    "fields": ["name", "declaring_type"]
  }
}
```

`offset` counts matching rows, not source indices. `limit` defaults to 64;
`coverage.next_offset` continues that filtered page. Coverage describes retained
metadata facts only; runtime behavior and correspondence to native code remain
unknown. Each view preserves the parent Evidence link, artifact identity and
limitations. Queries work after the source file is removed. Select
`detail: "complete"` to return every row inline within the separate MCP response
budget.

## CLI

```bash
rea inspect-il2cpp-metadata /absolute/path/global-metadata.dat --json
```

The CLI defaults to complete Evidence. For compact delivery, explicitly preserve
the full Evidence in a new file:

```bash
rea inspect-il2cpp-metadata /absolute/path/global-metadata.dat \
  --detail summary --evidence_output /tmp/metadata-evidence.json --json
jq -c '{source: {kind: "inline", evidence: .records[0]}, view: {kind: "il2cpp-metadata", collection: "methods", indices: [9785], fields: ["name", "declaring_type"]}}' \
  /tmp/metadata-evidence.json > /tmp/metadata-query.json
rea inspect-analysis-view /tmp/metadata-query.json --json
```

Use the exported Evidence with the CLI's inline Evidence source format described
in [CLI and Evidence](cli.md#run-a-command). Compact delivery requires
`--evidence_output`; existing files are never overwritten. The full export
preserves every decoded row for subsequent queries without the original file.

## Observations

The result contains:

- `artifact`: path, SHA-256 and byte length;
- `magic`: unsigned little-endian header signature (`0xFAB11BAF`, delivered as a JSON number);
- `metadata_version`: `29`, `31` or `39`;
- `index_widths`: the serialized widths (1, 2 or 4 bytes) of
  `type_definition`, `generic_container`, `parameter` and `type` indices, and
  `type_width_source`. Version 39 derives the type index width from the
  `interface-offsets-record` or the `type-definition-record`; versions 29 and
  31 always use 4-byte indices (`fixed-width-version`);
- `sections`: all 31 header sections in header order, each with `offset`, `size`
  and `count`. Versions 29 and 31 record no counts, so `count` is `null` and
  record counts come from the section sizes;
- `images`: `name`, `type_start` and `type_count`;
- `types`: `name`, `namespace`, `method_start`, `method_count`,
  `nested_type_start`, `nested_type_count` and `declaring_type`;
- `methods`: `name` and `declaring_type`;
- `limitations`.

A row's position in its collection is its metadata index, so `type_start`,
`method_start` and `declaring_type` refer to positions in `types` or `methods`.
`nested_type_start` instead indexes the metadata's `nestedTypes` table, which is
not returned; each nested type's `declaring_type` carries that relationship.
A type's `declaring_type` is derived from the `nestedTypes` section and is `-1`
for top-level types. The start of an empty range can retain the original value
`-1`.

The complete inventory of a large game is several megabytes and can exceed
the MCP response budget. Summary delivery and filtered, projected pages keep
unneeded rows out of agent context without discarding the source Evidence.

## Failures

A file whose magic is not `0xFAB11BAF` fails as an unsupported target with
`unrecognized-magic`. The file may be encrypted or may not be IL2CPP metadata.
A version other than 29, 31 or 39 fails as an unsupported target with
`unsupported-version`.

Damaged metadata returns an input error (`invalid_format`) whose
message names one reason:

| Reason                    | Meaning                                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `truncated-header`        | The file is shorter than the header.                                                                             |
| `unexpected-header-size`  | `stringLiterals.offset` is not the header size: 256 bytes for versions 29 and 31, 380 for 39.                    |
| `section-out-of-bounds`   | A section extends beyond the file, or a non-empty section starts inside the header.                              |
| `section-overlap`         | Two sections overlap. Zero-size sections are exempt and gaps are allowed.                                        |
| `record-size-mismatch`    | A section size does not divide into its records, or the record size differs from the one the index widths imply. |
| `type-index-width`        | The record used to derive the type index width implies no 1, 2 or 4 byte width.                                  |
| `index-out-of-range`      | A serialized index or range points outside its target collection.                                                |
| `nested-type-conflict`    | A type is listed as nested in two types, in itself, or in a cycle of declaring types.                            |
| `declaring-type-mismatch` | A method inside a type's method range names a different type, or a method lies outside its type's range.         |
| `image-range-overlap`     | Two images claim the same type definitions.                                                                      |
| `invalid-string`          | A name index does not start a string, or the name is unterminated or not valid UTF-8.                            |

A version field that disagrees with the file's layout, for example a version
39 file relabeled as 29, usually surfaces as `unexpected-header-size` or
`record-size-mismatch`.

Two checks are stricter than the IL2CPP runtime: a name index must start a
string, and an empty range's start must lie between -1 and the collection size.
Every Unity-written file checked so far satisfies both; metadata rewritten by
other tools may be rejected.

An incomplete inventory is never reported as complete. Failures after a verified
snapshot retain partial source Evidence with its SHA-256, byte length and any
validated section row counts; these counts do not establish that names and
relationships were decoded. A file that changes during reading and a cancelled
request keep distinct errors. Decode checkpoints yield for cancellation, and
close waits for active work. Each reader admits one inspection at a time.
Resource guards bound the selected file to 256 MiB and the encoded complete
report to 64 MiB, checking JSON/UTF-8 expansion before serialization. MCP also applies its
[response transport budget](mcp-contracts.md); a complete report within the
report limit can still require the summary and paging path.

## Outside this tool

- Decrypting or deobfuscating protected metadata.
- Linking metadata to the native binary (`GameAssembly`, `UnityFramework`),
  including method RVAs and code addresses.
- Fields, properties, signatures, parameters and generic instances.
- Ghidra or other disassembler integration. Use the
  [native workflow](native-investigation.md) for native code.
- Metadata versions other than 29, 31 and 39.

Names come from the metadata file only. They do not establish which methods
were compiled into the native binary or how they behave at runtime.

## Real producer verification

`npm run verify:il2cpp:metadata -- --metadata PATH` exercises a caller-supplied
`global-metadata.dat` through the public CLI and MCP. It is opt-in, like
`verify:pcap`, because no real game metadata ships with the repository. Normal
inspection does not need it.

The follow-up was checked against the public Cpp2IL
[`Simple_2022_3_35` sample](https://github.com/SamboyCoding/Cpp2IL/tree/b5ad444b82267cb1e4b88b8b373c008105bdea52/TestFiles/Simple_2022_3_35):
version 31, 1,892,268 bytes, SHA-256
`2441635a7c234a1a34deccc6a9906d6f5abcbdab078a38b2bf488a52a4962c48`.
An independent byte-layout oracle matched all 36 images, 2,468 types and 12,409
methods. Corresponding managed DLLs independently matched names and ownership
for 35 images, 2,463 types and 12,406 methods; the generated image has no matching
DLL. This does not establish real-producer coverage for versions 29 or 39.
