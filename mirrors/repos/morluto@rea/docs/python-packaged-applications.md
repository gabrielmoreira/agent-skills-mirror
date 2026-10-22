# Python packaged applications

REA statically inventories PyInstaller executables with an appended CArchive.
`inspect_artifact` and `extract_artifact` share the same reader through CLI and
MCP. They read archive bytes without launching the application. Bytecode
source decompilation, encrypted PYZ recovery, zipapp and PEX analysis are outside
this capability.

## Facts and focused queries

The root occurrence's `format_metadata` records the CArchive layout (2.0 or
2.1), archive and cookie offsets, table extent, entry count, raw Python version,
normalized major/minor when known, library name and encryption marker. Member
metadata retains the original name, table index, type, compression flag,
relative offset and known directory record extent. Logical paths use archive
path rules; the source name retains its spelling, including backslashes.
`relative_offset` is relative to the CArchive start for CArchive rows, or to
the decoded PYZ image for PYZ rows. A CArchive directory record starts at
`archive_start + toc_offset + directory_record_offset`; its size is
`directory_record_size`. PYZ row directory extents remain unknown.

Namespace packages remain directories. Their `relative_offset` and
`compressed_size` preserve any payload declared by older producers, while
`declared_size` is zero because no bytecode is materialized for a namespace.
Every declared span must end before the PYZ table of contents.
PYZ `compression_flag` is derived from storage: nonempty payloads are compressed,
including legacy namespaces; an empty namespace has no compressed payload.

CArchive type `o` entries are runtime options. They are metadata occurrences,
with no content artifact or extractable file. Their query paths are
`__pyinstaller__/runtime-options/<table index>`; the option text is
`format_metadata.source_name`. Repeated declarations retain distinct occurrence
identities. These paths do not claim output filesystem names.

Type `d` entries are multipackage dependencies. They are also metadata, under
`__pyinstaller__/dependencies/<table index>`, and never materialize an empty file.
The reader preserves the raw reference and splits its first colon into
`dependency_archive` and `dependency_member`. `dependency_status` remains
`unresolved`, or `invalid-reference` with unknown parts for malformed references.
`external_dependency_count` summarizes these declarations. REA does not open
another executable or claim its contents are available. A real file with the
same logical path as metadata remains independently extractable.
Both declaration types require empty payloads and no compression. Their query
paths do not participate in filesystem collision checks, directory ancestry or
source-map target lookup; their parent identifies the declaring container.
Complete authenticated inventory page sets preserve producer identities in any
merge order, including metadata/file aliases. Malformed TOC diagnostics name the
table index; original names remain available in the supplied artifact.
Path failures use bounded escaped previews and report the original length;
accepted paths and retained source names are not shortened.

Request `detail: "summary"` for a compact inspection, then query retained
Evidence with `inspect_analysis_view`. An inventory view can select
`collection: "occurrences"`, `entry_kinds: ["metadata"]`, exact logical paths or
occurrence IDs, requested `fields`, and `offset`/`limit`. Filters intersect;
identities, parent Evidence and coverage survive projection. Full inventory
Evidence remains available for export. A compact reply reduces returned context;
it still performs the complete member inventory and hashing work.
Focused views add calls and tool-schema costs. A complete small inventory can
cost less overall; prefer compact delivery when the full member graph would
overwhelm the answer.

```bash
rea inspect-artifact /absolute/path/hello --detail summary --evidence_output /absolute/new/evidence.json --json
rea extract-artifact /absolute/path/hello --json
```

## Decoding and evidence limits

Inventory hashes members individually through bounded streams. Stored PYZ
images use descriptor ranges; outer-compressed images stream to private files,
which the reader owns through cleanup and any cleanup retry. Extraction binds
the selected carrier to its inventoried digest and checks source identity and
state before and after reading. It does not retain expanded module bodies.
Opaque outer-compressed images reuse that verified private image when opened,
instead of inflating the carrier again. Direct source spans describe stored
CArchive bytes; decompressed content has no direct span even when its encoded
and decoded sizes coincide. Original offsets and compression remain metadata.

Only the PYZ header and marshal directory are loaded for listing. PYZ tables
have a 16 MiB budget; CArchive tables have a 32 MiB budget. Parsed facts have a
32 MiB serialized budget. Projected entries share a 64 MiB retained budget,
including metadata, bookkeeping and conservative reservations for namespace
objects and possible case-collision annotations at each path component. These
reservations happen before normalization or trie allocation.
Outer-compressed PYZ images have a separate per-reader capacity of 128 private
files, bounding retained inodes and image identities. The complete image count
is admitted before any temporary file is created; excess images return a
capacity failure. This is a resource policy, not a PyInstaller format limit.
Only a zero-byte read establishes EOF; short successful descriptor reads fill
the bounded range. Compressed members must consume their complete declared
input span; trailing junk and concatenated streams are refused.
Plaintext expansion has an aggregate archive-derived budget. Exceeding a budget
returns a resource failure.

Supported final Python bytecode magic values cover Python 3.7 through 3.14.
Supported marshal directory values are lists, tuples, strings, integers and
bytes. An unsupported magic or directory stays an opaque member with a
limitation and `pyz_status: "opaque"`; its module contents remain unknown.
Any opaque PYZ makes producer traversal coverage unknown, including retained
summaries and exhausted queries. Per-archive reasons remain on the opaque
occurrences; the coverage observation summarizes their count without repeating
every limitation. An empty result does not establish module absence.
Observed `pyz_python_magic` bytes remain available even when their Python version
is unknown.
The directory declares compressed module lengths, so uncompressed declared
sizes and source spans inside decoded data remain unknown.

PYZ modules receive a derived 16-byte `.pyc` header from their own supported
magic. CArchive bytecode receives that header only when every sibling PYZ magic
and the cookie's Python version agree. Otherwise it retains its original bytes
and `bytecode_header: "unknown"`. `bytecode_magic` and graph derivation edges
identify synthesized headers; member digests cover the resulting derived files.
These headers do not establish successful execution or decompilation.

The nonempty CArchive Python module `pyimod00_crypto_key` (`m`/`M`) is recorded
as an encryption marker; a same-named data file or script is not. Affected
PYZ blobs are reported without decoding; extraction refuses encrypted entries.
The raw PYZ container remains readable and hashable, including when its module
table is opaque. Its marker stays in metadata and opaque child coverage stays
unknown; extracting the container does not decrypt its payloads.
The marker also applies to nonempty legacy namespace payloads. Empty namespaces
have no payload to encrypt and retain a null encryption source.

Detection searches the last 16 MiB for a cookie, allowing a trailing macOS code
signature within that bound. Member offsets are relative to the archive start:
cookie position plus cookie size minus package length. Native bootloader
analysis remains available through the native tools.
