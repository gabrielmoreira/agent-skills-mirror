# content_ops_item_v0

Status: provider-neutral content-item lifecycle contract v0.

`content_ops_item_v0` gives the existing `content_ops` capability one stable
identity and transition contract for articles, posts, replies, reposts, and
profile updates. It is the state layer behind a managed operations queue. It is
not a publisher and does not store draft bodies.

## Item Boundary

An item stores:

- stable `item_id`, `item_kind`, and channel;
- a positive revision plus exact `sha256:` content digest;
- opaque `content_ref` and source refs owned by local/provider storage;
- approval, delivery-intent, delivery, and readback receipts;
- supersession lineage and the last applied event digest.

The public record never stores post/article bodies, credentials, browser
profiles, login state, media payloads, raw timelines, or private source maps.
Unknown fields fail validation so an adapter cannot silently add them.

## Lifecycle

```text
captured -> draft -> review_ready -> approved -> delivery_ready
    |          |          |             |             |
    +----------+----------+-------------+-------> published -> readback_verified
                         \-> skipped
                         \-> superseded
```

`delivery_ready` is optional. A provider may write a delivery receipt directly
from `approved` when no scheduling intent is needed.

Supported events are:

- `revise`: increments the revision and clears approval/effect state;
- `submit_review`;
- `approve`: binds an owner-authorized approval ref to one revision, digest,
  effect kind, optional account, and optional time window;
- `set_delivery_intent`: selects a provider without performing an effect;
- `record_delivery`: records a provider effect that already happened;
- `verify_readback`: proves exact URL and digest readback;
- `revoke_approval`, `skip`, and `supersede`.

Every event supplies `expected_state` and `expected_revision`. The transition
fails closed on stale state, stale revision, digest mismatch, provider/account
mismatch, expired approval, or changed reuse of an event id. An exact retry of
the latest event returns `already_applied`.

## Authority

The lifecycle validates that approval, intent, delivery, and readback refer to
the same item revision. It does not create approval authority. The caller must
resolve `approval_ref` from an authorized LoopX decision or provider-owned
receipt before persisting an `approve` event.

Likewise, `record_delivery` does not call a provider. X through Ego Lite, a
document publisher, or another extension performs the external effect under
its own authority and writes back a compact receipt. Every CLI packet reports
`external_writes_performed=false`.

## CLI

Create a compact item:

```bash
loopx content-ops item-create \
  --item-id launch-post-v1 \
  --item-kind post \
  --channel x \
  --content-digest sha256:<digest> \
  --content-ref draft:launch-post-v1 \
  --created-at 2026-08-03T09:00:00+08:00 \
  --format json
```

Apply one event from caller-owned JSON:

```bash
loopx content-ops item-transition \
  --item-json item.json \
  --event-json event.json \
  --format json
```

The command returns the updated item, a read-only projection, and
`content_ops_item_transition_receipt_v0`. Persistence remains caller-owned so
private queues can stay ignored and provider-specific.

## Relationship To X

[`x_public_channel_ops_v0`](x-public-channel-ops-v0.md) remains the X-specific
source, draft, approval, and result protocol. Its records may be projected into
this generic lifecycle, while account calendars, exact drafts, and Ego Lite
session state remain local.
