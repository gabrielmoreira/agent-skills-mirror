---
name: game-multiplayer-design
description: Design, implement, debug, and review multiplayer game systems. Use when Codex is asked about client/server architecture, authoritative servers, listen servers, dedicated servers, peer-to-peer, replication, prediction, interpolation, rollback, lag compensation, matchmaking, lobbies, sessions, state synchronization, netcode, anti-cheat risk, network testing, Unity Netcode, Unreal networking, Godot multiplayer, or custom multiplayer backends.
license: MIT
---

# Game Multiplayer Design

## Core Workflow

1. Identify the game mode, player count, genre, platform, latency tolerance, cheat risk, session length, persistence needs, and hosting model.
2. Choose topology deliberately: dedicated server, listen server, relay-assisted peer-to-peer, distributed authority, or turn-based/asynchronous backend.
3. Define authority before implementation. State which machine owns simulation, movement, inventory, combat, RNG, spawning, scoring, economy, and match results.
4. Design data flow as messages and replicated state, not as local single-player code with networking added later.
5. Separate input, prediction, server validation, reconciliation, interpolation, presentation, persistence, and matchmaking concerns.
6. Test with real network conditions: latency, jitter, packet loss, disconnects, reconnects, host migration if applicable, low frame rate, and platform suspend/resume.

## Architecture Priorities

- Server authority: prefer server-owned game state for competitive, economy-sensitive, or cheat-prone systems.
- Client responsiveness: use client-side prediction, local input echo, interpolation, animation smoothing, and rollback where appropriate.
- Replication scope: send only relevant state at the right frequency; avoid broadcasting private, unnecessary, or high-rate data.
- Determinism: use deterministic simulation only when the project can enforce it; otherwise design explicit reconciliation and correction paths.
- Ownership: distinguish authority, ownership, visibility, and permission. Owning a player object does not automatically mean trusting the client.
- Persistence: keep durable progress, purchases, inventory, ranked results, and social state on trusted services.
- Security: validate all client requests, rate-limit network actions, and treat clients as potentially modified.
- Observability: add logs, network stats, replay traces, packet captures, and debug overlays where they reduce multiplayer guesswork.

## Topology Guidance

- Dedicated server: use for competitive games, public matchmaking, ranked play, economy-sensitive state, and stronger anti-cheat posture.
- Listen server: use for small co-op or private sessions when host advantage, migration, and disconnect tradeoffs are acceptable.
- Peer-to-peer or distributed authority: use only when trust requirements are low, cost/latency constraints justify it, and ownership boundaries are explicit.
- Turn-based/asynchronous: use a backend command log or authoritative service rather than real-time replication when the design allows it.

## Freshness Rule

Verify current networking docs before giving version-sensitive advice about Unity Netcode, Unreal networking, Godot multiplayer, Steam/EOS/console services, relay/lobby/matchmaking products, platform certification, or transport/security behavior.

## Engine Mapping

- Unreal: map rules to GameMode/server authority, PlayerState/GameState, replicated actors/properties, RPC direction, relevancy, prediction, and network emulation.
- Unity: map rules to Netcode authority/ownership, NetworkObjects, RPCs, NetworkVariables, Relay/Lobby/Matchmaker, Multiplayer Play Mode, and transport settings.
- Godot: map rules to multiplayer authority, RPC modes, scene replication, synchronization config, ENet/WebRTC/transport choices, and host/client scene ownership.
- Custom backend: define protocol, tick/update cadence, serialization, interest management, connection lifecycle, authentication, persistence, and deployment model.

## Deliverable Shape

For multiplayer work, provide:

- Mode, topology, player count, and trust assumptions
- Authority map by system
- Replicated state, RPC/message, and interest-management plan
- Prediction, interpolation, reconciliation, or rollback approach
- Matchmaking/lobby/session lifecycle if relevant
- Security, abuse, and persistence risks
- Network test plan with latency, jitter, packet loss, reconnect, and disconnect cases

## References

- Read `references/multiplayer-architecture-checklist.md` when planning or reviewing multiplayer systems.
