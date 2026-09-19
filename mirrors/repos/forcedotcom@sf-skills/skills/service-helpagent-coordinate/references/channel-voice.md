# Channel branch — Voice

> **When to read this file.** Load it only when the user has selected **Voice** at Checkpoint 3 of `assets/help-agent-spec.md`. If they selected Web Chat, read `channel-web-chat.md` instead. If they selected Help Portal, delegate to the sibling skill `service-concierge-portal-generate` — do not inline portal steps here.

Voice wires the Help Agent to a `PstnVoice` MessagingChannel via an inbound RoutingFlow. This skill never calls the Number Management API itself — if no `PstnVoice` channel exists yet, it delegates number procurement to `service-agentforce-contact-center-coordinate`, which owns that end-to-end (fetch → procure → verify live → create the channel).

---

## Existing number path

Query existing channels:

```bash
sf data query --target-org $ORG --json \
  --query "SELECT Id, DeveloperName, MasterLabel, MessagingPlatformKey, IsActive FROM MessagingChannel WHERE MessageType='PstnVoice' ORDER BY MasterLabel"
```

If any are returned, present them and let the user choose. Capture the channel's `DeveloperName` as `CHANNEL_DEV_NAME`, then continue to **Step 8 — Wire the channel to the agent**. Fallback queue resolution (including the `SobjectType='VoiceCall'` requirement) is owned by `service-agentforce-channel-configure` — do not resolve or create the queue here.

If none are returned, continue to **No existing number** below.

---

## No existing number — delegate provisioning

Ask the user (`AskUserQuestion`): **provision a new number now** (delegate to `service-agentforce-contact-center-coordinate`), or **provision manually in Setup → Feature Settings → Service → Communication Channels** and come back once a `PstnVoice` channel exists.

If they choose to provision now, delegate to `service-agentforce-contact-center-coordinate`, passing `$ORG`. Instruct it to run its full number-procurement flow through channel creation, but steer the routing-model choice (its Step 7) to **Omni Queue**, not Omni Flow — the Help Agent already exists and owns its own agent authoring; Omni Flow's agent/flow-authoring steps would create a second, redundant agent. `service-agentforce-channel-configure` Branch B (this skill's Step 8, below) rewires the created channel's `SessionHandlerId`/`FallbackQueueId` to the Help Agent regardless of which routing model created it, so Omni Queue is the correct, minimal choice here.

Once `service-agentforce-contact-center-coordinate` reports the created `PstnVoice` MessagingChannel, capture its `DeveloperName` as `CHANNEL_DEV_NAME` and continue to **Step 8 — Wire the channel to the agent**.

---

## Step 8 — Wire the channel to the agent

Delegate to `service-agentforce-channel-configure` Branch B. Pass:
- **Agent DeveloperName** — the Help Agent
- **Channel type** — Voice
- **Channel identifier** — `CHANNEL_DEV_NAME`

The delegated skill resolves and configures the fallback queue itself.

---

## Step 9 — Loop

Return to the Checkpoint 3 loop — offer the user the option to add another channel or proceed to go-live.

---

## Rules / constraints

| Rule | Rationale |
|---|---|
| This skill never calls the Number Management API itself | Delegate provisioning to `service-agentforce-contact-center-coordinate` — do not hand-roll fetch/procure/verify-live here |
| When delegating provisioning, steer its routing-model choice to Omni Queue | Omni Flow would author a second, redundant Agentforce agent; Branch B rewires the channel's routing to the Help Agent regardless of which model created it |
| Never resolve or create the fallback queue here | `service-agentforce-channel-configure` owns queue resolution end to end — resolving it twice can double-prompt the user |
