# Agent Activity Tuttid Adapter

Monorepo-private, platform-neutral mapping between the generated tuttid
workspace-agent DTOs and the canonical `@tutti-os/agent-activity-core`
entities.

Application hosts continue to own transport, lifecycle, logging, storage, and
command execution. This package intentionally contains no React, DOM, Electron,
or React Native dependencies.

It also owns the single `agentActivityComposerOptionsFromTuttidResult` mapper
for the daemon Composer-options response. Hosts execute the request through
their engine command port, then feed this canonical activity-core projection
back to the engine; they do not duplicate provider capability parsing. The
public mapper accepts the generated `AgentProviderComposerOptionsResponse`
contract. Only its documented `runtimeContext` remains opaque; typed Skill and
capability catalogs do not grow compatibility fields in this adapter.

`tuttiAgentSessionComposerSettingsFromActivity` is the reverse request
projection shared by Desktop and Mobile. It forwards only fields declared by
the generated `AgentSessionComposerSettings` contract. Broader Engine or
presentation settings such as `computerUse` remain local unless OpenAPI first
adds a matching request field.

The package also owns the outbound create-Session and send-input request
projections. They accept canonical activity-core inputs and construct generated
tuttid request DTOs through explicit field allowlists. Desktop and Mobile keep
transport execution, cancellation, logging, and platform policy, but must not
spread activity-core values into HTTP request bodies or cast them to generated
DTOs. In particular, local prompt fields such as `uri`, `hostPath`,
`uploadStatus`, and `assetId` never cross the HTTP boundary.

`agentActivitySessionDetailFromTuttid` is the single detail aggregate mapper for
Desktop and Mobile. It validates and maps the root Session, nested child
Sessions, and Turns as one value. The caller supplies the requested Session id;
the mapper rejects a mismatched response root, a child outside that hierarchy,
or a Turn not owned by the requested Session. A host dispatches the result
through one `session/detailSnapshotReceived` intent; it must not partially
publish a root when a child or Turn violates the generated protocol contract.
Transport reads, message paging, retries, and Engine dispatch remain in the host
adapter.

Turn mapping preserves validated `capabilityRefs` so an immediate send result
and a later detail reconciliation project the same durable capability
provenance.
