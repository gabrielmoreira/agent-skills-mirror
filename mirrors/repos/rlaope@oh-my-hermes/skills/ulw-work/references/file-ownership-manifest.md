# File-Ownership Manifest

`references/dependency-topology.md` requires that no two concurrently runnable
lanes share a write scope. This is the artifact that makes the requirement
checkable before dispatch instead of discoverable at integration. Load it when a
unit of work is about to fan out into more than one concurrent lane.

A declared manifest is preparation. It is not dispatch, execution, or
verification evidence, and a lane that has one can still be wrong about which
files it will touch - which is why the manifest is compared against the diff
afterwards.

## Derive the file list before naming the streams

Naming streams first produces plausible-sounding lanes whose file lists overlap.
Derive in this order.

1. **Enumerate** every file the work creates or modifies. A file nobody can name
   yet is itself a finding: the work is not understood well enough to split.
2. **Cluster** by directory proximity, by import relationship, and by layer.
   Files that import each other belong to one owner.
3. **Assign** one cluster per stream. No file may appear in two clusters.
4. **Separate the interface** - the types, signatures, event names, and payload
   shapes that two clusters agree on. These get one owner, named explicitly, and
   every other stream consumes them read-only.

## Manifest shape

One manifest per unit of work, written before the first lane starts.

```
unit: <issue or task id>
streams:
  - id: <stream id>
    scope: <one sentence: what this stream is responsible for>
    files: <explicit paths or a single directory glob; never "related files">
    starts: immediately | after <stream id>
    verify: <the command that proves this stream alone>
shared:
  - path: <file>
    owner: <stream id>
    consumers: [<stream id>, ...]
conflict_risk:
  - paths: [<file>, ...]
    streams: [<stream id>, ...]
    resolution: split | single-owner | sequential
```

Three rules make it worth writing:

- **`files` is explicit.** A glob is allowed when the whole directory belongs to
  one stream. A prose description is not a file list, and a manifest of prose
  descriptions cannot be checked for overlap by anyone.
- **`shared` is not empty by default.** Almost every multi-stream change has a
  type file, a registry, a schema, or a config map that more than one stream
  wants. Finding none usually means the interface was not looked for.
- **`conflict_risk` names files, not worries.** An entry with no paths is a
  feeling. Leave the section out rather than filling it with one.

## Resolving an overlap

When two streams need the same file, take the first of these that applies.
Higher options cost more design and save more integration time.

1. **Split the file.** Extract the concern each stream needs into its own file
   and give each stream one of them. This is the only resolution that leaves
   both streams fully parallel.
2. **Single owner, change requests.** One stream owns the file; the other states
   what it needs and does not edit. The owner's lane carries both changes.
3. **Sequential.** One stream finishes the file, then the other takes it. Record
   this as a dependency edge, because that is what it is - the streams are no
   longer concurrent and the plan should stop saying they are.

Two streams editing one file concurrently is never an option, whatever the
merge tooling promises. The failure is not the textual conflict, which is
visible; it is the clean auto-merge of two edits that each assumed the other's
absence.

## Check the manifest against what happened

After the lanes return, compare the manifest to the actual diff and report the
comparison rather than the intent.

- A file touched by a stream that did not declare it is a manifest defect. Say
  which stream, which file, and whether another stream also touched it.
- A file touched by two streams is the failure this artifact exists to prevent.
  Report it even when the merge was clean, because a clean merge of two
  independent edits to one file is where the silent defect lives.
- A declared file nobody touched is usually harmless and occasionally the tell
  that a stream stopped early.

## Reporting

A parallel split earns its coordination cost only when the lanes are genuinely
independent. State the stream count and the deepest dependency chain; those two
numbers say what the split can and cannot buy. Do not report a wall-clock
saving that was not measured - an estimate presented beside real observations
reads as one of them.
