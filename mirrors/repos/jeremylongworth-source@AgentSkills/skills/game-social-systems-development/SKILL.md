---
name: game-social-systems-development
description: Design, implement, debug, and review player social interaction systems for games. Use when Codex is asked about chat, voice, friends, parties, lobbies, guilds, clans, presence, invites, matchmaking social flow, emotes, pings, reputation, blocking, muting, reporting, moderation, privacy, parental controls, user-generated content, community safety, trust and safety, or social UX.
license: MIT
---

# Game Social Systems Development

## Core Workflow

1. Identify the player audience, age range, platform requirements, social graph, communication channels, privacy expectations, and risk profile.
2. Define the social goal: coordinate play, find groups, express identity, trade, compete, mentor, roleplay, spectate, create, or build long-term community.
3. Design the safety model with the feature, not after it: consent, privacy, muting, blocking, reporting, moderation, abuse prevention, auditability, and escalation.
4. Map the lifecycle: discovery, invite, join, communicate, leave, reconnect, report, moderate, appeal, and recover.
5. Choose backend ownership for durable social state: friends, blocks, reports, guild membership, reputation, sanctions, chat logs, presence, and parental settings.
6. Verify social flows with edge cases: strangers, minors, blocked users, cross-platform players, offline users, party leadership changes, spam, harassment, and network failure.

## Social Feature Priorities

- Chat and voice: provide channel scope, consent rules, moderation hooks, mute/block/report actions, rate limits, logs where policy allows, and accessibility alternatives.
- Friends and presence: expose online state with privacy controls, platform constraints, cross-platform identity mapping, and clear invite permissions.
- Parties and lobbies: define ownership, leadership transfer, ready checks, matchmaking handoff, reconnect behavior, voice channel membership, and failure states.
- Guilds, clans, and groups: define roles, permissions, invitations, moderation powers, audit logs, naming rules, discovery, and inactivity handling.
- Emotes, pings, and nonverbal communication: support coordination without forcing voice/chat, and guard against spam or harassment patterns.
- User-generated content: moderate names, profiles, avatars, custom text, images, maps, posts, screenshots, and shared loadouts.
- Reputation and sanctions: distinguish player-facing reputation, hidden trust scores, enforcement history, temporary limits, suspensions, and appeals.

## Safety And Privacy Requirements

- Give players immediate local controls: mute, block, report, leave, restrict invites, and disable voice/chat where appropriate.
- Never rely on players to tolerate harm while waiting for moderation.
- Treat private data, account identifiers, location, age, voice, chat logs, and moderation history as sensitive.
- Support platform and regional requirements for minors, parental controls, consent, reporting, and data retention.
- Keep moderation actions explainable enough for player trust while preserving abuse-detection integrity.
- Design for human review in ambiguous or high-impact cases.

## Integration Guidance

- Use platform social systems where required or beneficial, such as Xbox, PlayStation, Steam, Epic Online Services, Discord, or mobile platform identity.
- Keep game social identity separate from platform account internals when possible.
- Store durable social state on trusted services, not client files.
- Add telemetry for abuse patterns, failed invites, blocked communication attempts, churn after negative interactions, and moderation queue health.

## Deliverable Shape

For social systems work, provide:

- Social goal and relationship model
- Feature lifecycle and user flows
- Privacy, consent, block/mute/report controls
- Backend ownership and durable state
- Moderation, safety, and abuse-resistance plan
- Platform integration notes
- Edge cases and verification steps

## References

- Read `references/social-systems-checklist.md` when designing or reviewing any player-to-player interaction feature.
