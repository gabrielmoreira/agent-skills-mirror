---
name: threat-model-files
description: "Inspect Microsoft Threat Modeling Tool .tm7 XML read-only: discover serialized dictionaries and nested properties, map diagrams and flows, summarize STRIDE and triage states, and report unresolved references without inventing threats or rewriting the model."
---

# Read-only threat-model file analysis

Analyze only models explicitly provided and authorized by the user. A `.tm7`
can contain confidential system diagrams, descriptions, mitigation decisions,
and identities. Do not fetch private models, upload them to a service, or place
their content in a public example. Use synthetic fixtures for development.

This is format inspection and reporting, not evidence that a system is secure.
The original model stays unchanged; write any requested report to a separate
location and record its source hash/version.

## Identify the serialization before querying it

1. Record file size, SHA-256, tool/export version when known, XML root local name
   and namespace, and the model's `Version` element. File extension alone is not
   a schema guarantee.
2. Parse with DTD processing prohibited and external entity resolution disabled.
   Bound input size; do not load arbitrary external references.
3. Inspect immediate child names before choosing XPath. Public model examples
   use `ThreatModel`, `DrawingSurfaceList/DrawingSurfaceModel`, `Borders`,
   `Lines`, and `ThreatInstances`. Borders/lines may be serialized dictionaries
   whose wrapper entries contain **Key** and **Value** children.
4. Read nested `Properties` entries inside each value. A property's stable
   `Name` or dictionary `Key` is different from its display label; values can
   themselves be structured. Preserve unknown/nested content as unknown rather
   than flattening it into a misleading string.
5. Establish a mapping for this export's element IDs, diagram IDs, flow endpoints,
   threat-to-flow references, title, category and triage state. Do not guess a
   missing reference from visual proximity or duplicate display names.

The public [Azure model example](https://github.com/Azure/Industrial-IoT/blob/f8b888700af6e6b593da314b40a9961e3fda4780/docs/opc-publisher/threatmodel/OpcPublisher.tm7)
demonstrates a 4.1 root/diagram/KeyValue dictionary shape, not a stable schema
promise for all releases. Its real diagram content is not reproduced here.
Use [Microsoft's tool documentation](https://learn.microsoft.com/azure/security/develop/threat-modeling-tool)
and the actual export for the version you are inspecting.

## Namespace handling is not serialization handling

For XPath over a default namespace, bind a prefix in `XmlNamespaceManager`
and use it in expressions, for example `tm:DrawingSurfaceList`.
Unprefixed XPath selects elements in no namespace, so it often returns nothing
against a namespaced model.

That does **not** mean default namespaces inherently make
`GetElementsByTagName("DrawingSurfaceModel")` fail. The one-argument DOM method
matches the qualified name; use the local-name/namespace overload when
prefix-independent matching is intended. A correct namespace still does not
remove Key/Value wrappers or make nested properties into direct attributes.

## Preserve relationship and triage semantics

| Report field | Rule |
|---|---|
| Diagram | Keep diagram ID and label separate. Build indexes per diagram; IDs/names can repeat across diagrams. |
| Flow | Resolve source and target by exported IDs. Distinguish missing ID, absent endpoint, duplicate ID and unknown mapping. |
| Threat | Keep its own key, diagram/flow references and property evidence. An unresolved reference is not a dropped threat. |
| STRIDE | Report exported category and counts. Do not infer category solely from a title or confuse risk severity with STRIDE. |
| Triage | Preserve exported state and justification. Missing state is `Unknown`, not `Mitigated` or `NotApplicable`. |
| Findings | Separate **extracted facts**, **inferred relationships**, and **analyst recommendations**, with source IDs for each. |

Count unresolved references and unknown states explicitly. Summaries should
include total diagrams/elements/flows/threats, category and triage distributions,
missing properties, and integrity problems. A successful parse is not successful
relationship resolution or proof that mitigation was implemented.

## Synthetic parsing example

The bundled `examples/synthetic.tm7` is a **reduced fictional XML fixture**, not
a file certified to open in Threat Modeling Tool. It reproduces the dictionary
and nested-property patterns and deliberately includes two diagrams, a missing
property, and unresolved references.

`examples/Read-SyntheticModel.ps1` supports only its explicitly marked
`Synthetic-TM7-1` profile. Its `DiagramId`, `FlowId`, `SourceGuid`, `TargetGuid`,
`Title`, `Category`, and `State` mappings are **fixture definitions**, not claims
that every real tool template uses those fields. It rejects unrecognized input
instead of guessing. Use its traversal pattern after verifying the mappings of
a real export; do not bypass the guard and call that full `.tm7` support.

```powershell
pwsh -NoProfile -File .\examples\Read-SyntheticModel.ps1 -Path .\examples\synthetic.tm7
pwsh -NoProfile -File .\examples\Test-SyntheticModel.ps1
```

Resolve paths relative to this installed skill. The reader emits data only;
the test compares the original fixture hash before/after and checks diagram
scope, category/state counts, missing properties, and unresolved references.
Neither opens a real model, generates threats, or resolves external XML data.

## Apply the technique to an authorized export

Read a copy or read-only handle, retaining the original hash. Inspect the tool
version, namespaces, dictionary wrappers and property names; record those as the
parser profile. Explicitly reject unsupported collection shapes. Verify the
profile against a small known export and compare counts/IDs with the tool UI
before reporting a large model.

If the format differs, return the observed shape and explain the unsupported
mapping. Do not report zero threats merely because a query selected nothing.
If the user requests a report, keep it separate from the `.tm7` and include:
source hash, profile, extracted facts, unresolved references/unknowns, inference
rules, recommendations, and analysis limits. Never silently save a modified
model or treat a triage label as proof of a fix.

API references: [XmlReaderSettings.DtdProcessing](https://learn.microsoft.com/dotnet/api/system.xml.xmlreadersettings.dtdprocessing),
[XmlNamespaceManager](https://learn.microsoft.com/dotnet/api/system.xml.xmlnamespacemanager),
[GetElementsByTagName](https://learn.microsoft.com/dotnet/api/system.xml.xmldocument.getelementsbytagname).
