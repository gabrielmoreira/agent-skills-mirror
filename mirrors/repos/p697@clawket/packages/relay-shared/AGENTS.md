# Relay Shared

Shared relay protocol and types package inside the Clawket monorepo. This package is consumed by `apps/relay-registry`, `apps/relay-worker`, and bridge/mobile layers.

Owner roundtrip capability `relay.owner-pong.v1` is additive. Preserve unknown-capability fallback and byte-identical capability-free legacy handshakes. Its reserved controls use the existing Relay prefix, `type: control`, `event: relay.owner-ping|relay.owner-pong`, and `payload.nonce` containing exactly 32 lowercase hex characters; capability presence alone is not health evidence.

Client-initiated `relay.client-ping.v1` uses the same envelope with `relay.client-ping|relay.client-pong`; it is distinct from the legacy server-initiated `client_pong` acknowledgement. Only an explicitly advertising, authenticated full client may negotiate it. An exact current-socket echo proves Relay reachability, never native backend readiness. Preserve legacy expiry and reject owner, channel, restricted pairing and retired socket use without forwarding these reserved controls.

`relay.transfer-hint.v1` is independently negotiated by full clients and authenticated owners/channels. Only Relay may emit `relay.transfer-start` with the next frame's UTF-8 byte count (128 KiB through 8 MiB inclusive), immediately before that unchanged frame with no await between sends. Never forward peer-forged hints or persist frame contents. Receivers may defer liveness/request deadlines within one absolute 90-second socket budget; repeated transfers do not renew it, and only an exact round trip initiated after the latest transfer generation can clear it early. Transfer hints and arbitrary traffic never prove health or authorize replay.

For new full-auth transfer peers only, Relay's fallback client ACK expiry and Hermes owner watchdog use `max(existing timeout, 3 × heartbeat interval + 90s)`; the owner alarm uses the same effective deadline. Preserve longer operator settings, legacy peer deadlines, and the 20-second owner admission lease. New full transfer clients have a server handshake/awaiting cleanup floor of max(existing TTL, 90s); peers still cap each handshake/request at 90s from its own start. Do not infer completion from a response ID or expand connect-start/pending-challenge buffers.

## Hermes Relay Isolation Rule

When implementing Hermes relay support:

1. Do not change OpenClaw relay public routes, storage keys, or existing worker bindings as part of Hermes rollout work.
2. Hermes relay must use separate worker services, separate KV bindings, separate Durable Object classes, and separate bridge/mobile state.
3. Reuse implementation helpers only when doing so does not change OpenClaw deploy units or public contracts.
4. Do not switch the product-facing shared `pair` command from Hermes local to Hermes relay until the isolated Hermes relay stack is validated end-to-end.
5. In mobile/runtime code, treat relay behavior as a transport concern. Hermes relay connection decisions must key off `transportKind === 'relay'` or shared transport resolvers, not legacy `mode === 'relay'` checks.
6. For local Hermes relay testing, the registry must advertise a device-reachable relay URL. Do not emit `127.0.0.1` or placeholder example domains in pairing QR payloads when the target test path is a real phone or another device.
