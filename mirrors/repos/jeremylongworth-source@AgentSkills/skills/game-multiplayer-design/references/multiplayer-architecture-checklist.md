# Multiplayer Architecture Checklist

Use this checklist for client/server gameplay, netcode, matchmaking, lobbies, and multiplayer debugging.

## Product Fit

- Game mode, player count, session length, platform, and latency tolerance are known.
- Hosting model is explicit: dedicated server, listen server, relay/P2P, distributed authority, or asynchronous backend.
- Competitive integrity and economy risk are classified.
- Matchmaking, party, lobby, invite, reconnect, and post-match flows are included.

## Authority

- Server, host, client, or backend ownership is defined for movement, combat, inventory, spawning, RNG, scoring, progression, and match results.
- Client requests are validated and rate-limited.
- Private or trusted state is never replicated to clients unnecessarily.
- Host advantage, host migration, and disconnect consequences are accepted or mitigated.

## Synchronization

- Replicated state has ownership, frequency, priority, relevancy, and compression rules.
- Prediction and reconciliation are defined for responsive local actions.
- Interpolation, extrapolation, smoothing, or rollback handles remote actors.
- Time synchronization, tick rate, clock drift, and server correction behavior are explicit.
- Interest management prevents unnecessary replication at scale.

## Reliability And Failure

- Packet loss, jitter, high latency, out-of-order delivery, reconnect, timeout, and suspend/resume are tested.
- Critical messages use reliable delivery or durable backend state.
- Noncritical high-rate state avoids reliable flooding.
- Match state can recover from partial failure where the design requires it.

## Security And Abuse

- Treat clients as untrusted.
- Validate movement, hits, cooldowns, inventory changes, purchases, matchmaking requests, and ranked results.
- Log suspicious behavior with enough context to investigate.
- Avoid exposing admin, debug, economy, or matchmaking controls to clients.

## Verification

- Test with multiple machines or processes, not only same-process editor simulation.
- Use network emulation for latency, jitter, and packet loss.
- Add debug overlays for authority, ping, packet rate, replicated object count, prediction errors, and correction frequency.
