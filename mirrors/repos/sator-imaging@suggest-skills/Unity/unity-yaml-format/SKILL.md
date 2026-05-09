---
name: unity-yaml-format
description: Inspect, explain, diff, and carefully edit Unity text-serialized files such as .unity, .prefab, .asset, and related YAML-based project files. Use when mapping class IDs and fileIDs, tracing object references, reviewing merge conflicts, or making minimal safe edits to existing UnityYAML documents.
---

# Unity YAML Format

Use this skill when working directly with Unity text-serialized files rather than higher-level C# or Editor APIs.

## First Pass

- Read [references/source-summary.md](references/source-summary.md).
- Identify the file type and intent: inspect, explain, diff, repair, or minimally edit.
- If the task involves object or component type numbers, read [references/class-id-reference.md](references/class-id-reference.md).
- If the task involves `fileID`, `guid`, `type`, script links, or external asset links, read [references/reference-semantics.md](references/reference-semantics.md).
- If the task involves hand-editing, read [references/examples.md](references/examples.md) before changing anything.

## Working Rules

- Treat UnityYAML as a Unity-specific serialization format, not as generic full YAML.
- Prefer the Unity Editor for broad structural changes; use manual edits only for narrow, justified repairs to existing text-serialized files.
- Keep edits as small and local as possible.
- Preserve existing indentation, document order, anchors, `fileID` links, and scalar style unless the task requires otherwise.
- Explain reference relationships explicitly when reviewing a file.

## Gotchas

- UnityYAML is a custom subset and does not support the full YAML specification.
- Unity docs warn against externally producing or editing UnityYAML files; only make manual edits when the narrow reference or scalar repair is justified.
- Comments are not supported by UnityYAML.
- Multi-line plain scalars require deeper indentation on continuation lines.
- UTF-8 characters are decoded only inside double-quoted scalars.
- Chomping indicators, complex mapping keys, raw top-level block sequences, and arbitrary YAML tags are not supported.
- Unity scene and prefab files are multi-document files where each serialized object starts with `--- !u!<classID> &<fileID>`.
- `classID` and `fileID` have different roles: `classID` identifies the object type, while `fileID` identifies one object instance inside the file.
- In external references, `guid` identifies the target asset file and `fileID` identifies an object local to that asset; preserve `type` as part of the serialized reference tuple without guessing a new value.
- `type: 2` commonly indicates a non-built-in Unity asset whose contents are text-serialized in UnityYAML, such as a project material or similar asset.
- A `GameObject` references attached components through `m_Component`, and components usually point back through `m_GameObject`.
- Script components use class ID `114` (`MonoBehaviour`) and often require script references to remain intact.
- Floats may appear in decimal or IEEE 754 hexadecimal forms; when Unity writes `0x...(decimal)` the hex value is the parsed value, and manual edits should usually replace it with a plain decimal.
- References such as `{fileID: 0}` often mean a null-like Unity reference, not a missing parse failure by itself.

## Focus Areas

- UnityYAML document structure and document headers
- `classID`, `fileID`, `guid`, and `type` reference semantics
- Local in-file references versus external asset references
- Common object relationships across `GameObject`, `Transform`, and Components
- Merge-conflict review and broken-reference diagnosis
- Safe minimal edits to existing serialized files
- Limits of external editing and generation

## Checklist

- Confirm the file is text-serialized Unity data and not arbitrary YAML.
- Identify each relevant document header `--- !u!<classID> &<fileID>`.
- Map the target object graph before editing: owning `GameObject`, linked Components, parent or child references, external asset references.
- Resolve unknown class numbers with [references/class-id-reference.md](references/class-id-reference.md) or the official reference page.
- Distinguish local references like `{fileID: 8}` from external references like `{fileID: ..., guid: ..., type: ...}` before editing.
- Preserve every unrelated field, anchor, and reference line around the edit.
- If changing local references, verify both sides of the relationship still point to valid objects.
- If changing external references, keep `guid`, `fileID`, and `type` together unless a Unity-derived source gives the replacement tuple.
- If reviewing a merge conflict, compare semantic object links, not just textual proximity.
- Re-read the edited block for indentation, list formatting, and scalar syntax before finalizing.

## Validation

- Confirm the edit could plausibly round-trip through Unity without changing unrelated objects.
- Re-check every modified `fileID`, `guid`, `type`, and `classID` reference.
- If the change was structural rather than scalar, prefer reopening or reserializing in Unity before trusting it.
- When uncertain, stop at explanation or diagnosis instead of inventing new serialized structure.

## Output

- Explain the relevant object structure in plain language.
- Call out the exact documents and references touched by the change.
- State any risky assumptions, especially around inferred links or manual repairs.
- If editing, summarize the minimal intended change and the references verified afterward.

## References

- Read [references/source-summary.md](references/source-summary.md) for UnityYAML structure and limitations.
- Read [references/reference-semantics.md](references/reference-semantics.md) for `fileID`, `guid`, and `type` usage.
- Read [references/class-id-reference.md](references/class-id-reference.md) for common Unity class IDs and how to use them.
- Read [references/examples.md](references/examples.md) for safe bad-to-good editing and inspection patterns.
