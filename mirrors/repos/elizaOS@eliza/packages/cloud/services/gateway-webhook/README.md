# @elizaos/gateway-webhook

Stateless multi-platform webhook gateway for Eliza Cloud.

Install workspace dependencies with `bun install` at the repository root.

Build from the repository root:

```bash
bun run --cwd packages/cloud/services/gateway-webhook build
```

Test from the repository root:

```bash
bun run --cwd packages/cloud/services/gateway-webhook test
```

## Network on the existing Shared phone route

Shared takeover is off by default. Configure these inputs through the normal
release process after the matching Cloud admission and delivery chain passes:

- `NETWORK_TAKEOVER=1` enables service routing.
- `NETWORK_SHARED_PROJECT` must equal the existing
  `ELIZA_APP_WEBHOOK_PROJECT` (default `eliza-app`). Keep that ingress project,
  its connector account and the existing message-ID namespace.
- `NETWORK_TAKEOVER_ALLOWLIST` must contain a nonempty comma-separated list of
  owned E.164 senders. Other Shared senders keep the existing route.
- `NETWORK_SERVICE_URL` and the existing `SERVICE_TURN_SECRET` must identify
  the Network service authority. Admitted turns fail closed if it is missing.

This Shared path handles direct Blooio and Twilio phone traffic. Group and
explicit-agent traffic keep their existing routing. The original `network`
project keeps its existing rollout policy.

STOP fences apply before provider dispatch, including failure replies.
Completed Network receipts need the matching connector/thread target hash,
acceptance timestamp and provider IDs; missing proof returns unknown without
resending. Phone authentication and same-account/history acceptance remain
separate release checks.
