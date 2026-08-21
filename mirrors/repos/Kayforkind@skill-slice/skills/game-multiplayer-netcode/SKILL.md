---
name: game-multiplayer-netcode
version: 1.1.1
description: "Use when designing or debugging real-time netcode in any engine — choosing a sync model (authoritative server vs deterministic lockstep vs rollback/GGPO), client-side prediction with server reconciliation, snapshot interpolation, lag-compensated hit registration, and bandwidth work (delta compression, quantization, interest management). Triggers on 'rubber-banding', 'desync', 'hit reg', 'client prediction', 'reconciliation', 'rollback', 'GGPO', 'tick rate', 'lag compensation', 'jitter buffer'. Not for Godot connection plumbing — peers, @rpc semantics, node authority (use game-multiplayer-basics), MultiplayerSynchronizer setup and tuning (use game-multiplayer-sync), headless/dedicated server builds (use dedicated-server), or lobbies and matchmaking services (use game-steamworks-sdk)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Multiplayer Networking & Netcode

Authoritative simulation, prediction, and interpolation are what make a laggy network feel instant. Pick the sync model from the genre, never the other way around.

## When to Use

Activate this skill when the task involves:

- Choosing a **network topology / sync model** (authoritative server vs deterministic lockstep vs rollback) for a given genre.
- Implementing **client-side prediction and server reconciliation** for a local player.
- Adding **entity/snapshot interpolation** for remote players and dynamic objects.
- Building **rollback netcode (GGPO-style)** for fighting/lockstep games.
- Designing **RPCs** and replicated state (reliable/unreliable, ordered/unordered channels).
- Implementing **lag compensation** (server rewind) for fair hit registration.
- Reducing bandwidth with **delta compression, quantization, and bit-packing**.
- Diagnosing **rubber-banding, warping, desync, or hit-reg complaints**.
- Picking a **transport** (UDP reliability layers: ENet, GameNetworkingSockets, LiteNetLib, Netcode for GameObjects, Mirror, Photon, Unreal replication, Godot high-level multiplayer; WebRTC/WebTransport for browser targets).

### When NOT to use — route to the skill that owns them

| If the task is… | Use instead | Why not here |
|-----------------|-------------|--------------|
| Godot connection plumbing: creating peers, `@rpc` annotation semantics, per-node authority, lifecycle signals | `game-multiplayer-basics` | That is the wiring layer this skill's sync models sit on top of. |
| `MultiplayerSynchronizer` / `MultiplayerSpawner` configuration and replication tuning in Godot | `game-multiplayer-sync` | Engine-specific state-sync components; this skill covers the engine-agnostic algorithms behind them. |
| Headless/dedicated server exports, deployment, process lifecycle | `dedicated-server` | Build and ops concerns, not simulation design. |
| Lobbies, matchmaking, P2P session brokering, relay transport | `game-steamworks-sdk` / `game-mobile-store-integration` | Platform services territory, not real-time state synchronization. |
| AI or animation behavior that happens to run on a networked entity | `game-ai-behavior` / `runtime-animation` | Own the *replication* of state here, not the behavior itself. |
| Web/HTTP request-response APIs (accounts, leaderboards) | — (backend work) | This skill is for sub-frame state sync over unreliable transports, not REST. |
| Single-player or local-only gameplay | — | No network boundary, nothing to synchronize. |

## Prerequisites

- A game engine or networking stack that exposes a transport layer (UDP-based with optional reliability). Examples: ENet, GameNetworkingSockets, LiteNetLib, Netcode for GameObjects, Mirror, Photon Fusion/Quantum, Unreal replication, Godot ENetMultiplayerPeer, WebRTC/WebTransport.
- A fixed-timestep simulation loop already decoupled from render framerate, or willingness to add one (see Procedure step 2).
- For rollback/GGPO: a **bit-deterministic** simulation (fixed-point or strictly-ordered float math, frame-seeded RNG) and cheap `SaveState`/`LoadState`.
- For lag compensation: a history buffer of past entity hitbox positions, queryable by tick.

## Procedure

### 1. Choose the sync model from the genre

| Model | Best for | Authority | Cost |
|---|---|---|---|
| **Authoritative server + prediction/interpolation** | FPS, shooters, MMO, battle royale | Server | Server CPU, needs reconciliation |
| **Deterministic lockstep** | RTS (hundreds/thousands of units) | All peers (input only) | Input latency = RTT; requires perfect determinism |
| **Rollback (GGPO)** | Fighting, 1v1/2v2 deterministic | All peers | Re-simulation cost; requires determinism + small state |
| **State sync / dead reckoning** | Casual, co-op, racing | Server or host | Simple; weaker cheat resistance |

**Default for action games:** authoritative server, clients **predict** their own actor and **interpolate** everyone else.

### 2. Simulate on a fixed tick

All netcode rests on a **fixed timestep** decoupled from render framerate. Inputs, physics, and state snapshots are stamped with a monotonic tick number.

```csharp
const float TICK_RATE = 60f;
const float FIXED_DT = 1f / TICK_RATE;
float _accumulator;
uint  _tick;

void Update() {
    _accumulator += Time.deltaTime;
    while (_accumulator >= FIXED_DT) {
        InputCmd cmd = SampleInput(_tick);     // stamp with tick
        SimulateTick(cmd, FIXED_DT);           // deterministic step
        _accumulator -= FIXED_DT;
        _tick++;
    }
    Render(_accumulator / FIXED_DT);           // interpolate render between ticks
}
```

**Clock/tick sync:** the client's input tick must run *ahead* of the server by ~RTT/2 plus a small safety margin, so each input arrives just before the server simulates that tick. Estimate the offset from ping samples, nudge it gradually when RTT drifts, and have the server report how early/late inputs arrive so clients can self-correct.

### 3. Client-side prediction + server reconciliation (local player)

The client applies input **immediately** and stores every unacknowledged input. The server is authoritative; when its state arrives, the client snaps to the acked state and **replays** the inputs the server hasn't processed yet. If prediction was correct, nothing visibly moves.

```csharp
// CLIENT
struct InputCmd { public uint tick; public Vector2 move; public bool jump; }
readonly List<InputCmd> _pending = new();
PlayerState _predicted;

void OnTick(InputCmd cmd) {
    _predicted = Step(_predicted, cmd, FIXED_DT); // predict now
    _pending.Add(cmd);
    Net.SendUnreliable(cmd);                      // ship input to server
}

void OnServerState(PlayerState authoritative, uint ackTick) {
    _pending.RemoveAll(c => c.tick <= ackTick);   // drop acknowledged inputs
    PlayerState s = authoritative;                // snap to truth
    foreach (var c in _pending)                   // replay the rest
        s = Step(s, c, FIXED_DT);
    // Reconcile: if |s - _predicted| > epsilon, correct (snap or smooth)
    if (Vector3.Distance(s.pos, _predicted.pos) > 0.01f) _predicted = s;
}
```

**HARD RULE:** `Step()` **must be identical** on client and server. Share the movement code; do not fork it.

### 4. Entity/snapshot interpolation (remote actors)

Render remote entities ~100 ms **in the past**, smoothly interpolating between the two buffered snapshots that bracket `renderTime`. This hides jitter and packet loss at the cost of a small, constant visual delay.

```csharp
const float INTERP_DELAY = 0.1f; // 100 ms jitter buffer
readonly SortedList<float, Snapshot> _buffer = new(); // keyed by server tick time

Vector3 Sample(float now) {
    float renderTime = now - INTERP_DELAY;
    Snapshot a = Older(renderTime), b = Newer(renderTime);
    if (a == null || b == null) return (b ?? a).pos;       // extrapolate/hold
    float t = Mathf.InverseLerp(a.time, b.time, renderTime);
    return Vector3.Lerp(a.pos, b.pos, t);                  // smooth
}
```

Tune `INTERP_DELAY` to ≥ one snapshot interval + expected jitter. Extrapolate (dead reckoning) only briefly when the buffer starves.

### 5. Rollback (GGPO) for deterministic games

Predict remote inputs (usually "repeat last input"), simulate forward, and when the real input arrives mismatched, **roll back** to the last confirmed frame and re-simulate to present with corrected inputs. Requires bit-deterministic simulation and a cheap `SaveState`/`LoadState`.

```text
each frame:
  local_input = poll()
  send(local_input, frame)
  for f in [last_confirmed+1 .. current]:        # re-sim predicted window
      inputs = confirmed_or_predicted(f)
      if inputs_changed_since_last_sim(f):
          LoadState(checkpoint[last_confirmed])
          for g in [last_confirmed+1 .. current]:
              Simulate(g, inputs_for(g))
              checkpoint[g] = SaveState()
  Simulate(current, [local_input, predict_remote()])
```

Keep simulation state small, use fixed-point or strictly-ordered float math, and seed RNG from the synchronized frame.

### 6. RPCs and channels

- **Unreliable unordered:** movement/state snapshots (latest wins; loss is fine).
- **Reliable ordered:** discrete game events (spawn, death, chat, score).
- **HARD RULE:** Never send authoritative gameplay decisions over reliable RPC from the client — send **inputs**, let the server decide.

### 7. Lag compensation (server rewind)

On a hitscan/shot, the server **rewinds** every target's hitboxes to the tick the shooter actually saw (their render time), tests the ray, then restores. This makes "I clearly hit them" true without letting high-ping players dominate.

```csharp
// SERVER
void OnFire(uint shooterTick, Ray ray) {
    float rewindTo = TickToTime(shooterTick) - shooterInterpDelay;
    using (history.Rewind(rewindTo)) {     // restore hitboxes to past positions
        if (Physics.Raycast(ray, out var hit)) ApplyDamage(hit);
    } // hitboxes auto-restored to present
}
```

**HARD RULE:** Cap rewind to a max (e.g. 250–500 ms) to bound abuse.

### 8. Bandwidth: delta + quantization

- **Delta compression:** send only fields that changed vs the client's last *acknowledged baseline*.
- **Quantize:** positions to fixed-point (e.g. 1/512 m), angles to bytes, bools to bits.
- **Bit-pack** with a serializer; group rarely-changing state out of the per-tick snapshot.
- **Interest management / AoI:** only replicate entities near the client (grid/relevancy).

### 9. Engine mappings

```text
Unreal:  Replicated UPROPERTYs + DOREPLIFETIME; Server/Client/NetMulticast UFUNCTIONs;
         CharacterMovementComponent ships built-in prediction + reconciliation.
Unity:   Netcode for GameObjects (NetworkVariable, ServerRpc/ClientRpc) or Mirror
         ([SyncVar], [Command]/[ClientRpc]); Photon Fusion/Quantum for prediction+rollback.
Godot 4: MultiplayerSpawner + MultiplayerSynchronizer; @rpc("authority"/"any_peer",
         "unreliable"/"reliable") annotations; ENetMultiplayerPeer transport.
```

### 10. Test under simulated network conditions from day one

Use tools like `clumsy` (Windows), `netem` (Linux), or in-engine latency/jitter/loss simulation. Never validate netcode only on LAN.

## Pitfalls

### Rubber-banding / warping of remote entities

**Symptom:** "Enemies teleport/warp when my ping spikes."
**Cause:** Interpolation buffer too short or extrapolating past buffer starvation.
**Fix:** Raise `INTERP_DELAY` to ≥ snapshot_interval + p95 jitter; clamp extrapolation to ~2 ticks; verify snapshots are timestamped by server tick, not arrival time.

### Local player rubber-bands on reconciliation

**Symptom:** "My own movement rubber-bands."
**Cause:** Reconciliation snapping because client `Step()` ≠ server `Step()`.
**Fix:** Unify the movement function, replay ALL unacked inputs after the acked state, and smooth sub-threshold position error instead of hard-snapping.

### Forked simulation logic

If the client and server have separate movement implementations, prediction will always diverge and every reconcile will snap. Share one `Step()` function across the project boundary.

### Sending state instead of inputs

Clients that send desired *state* ("move to X") instead of *inputs* ("pressing forward") cannot be reconciled and are trivially exploitable. Always send inputs up, state down.

### Wall-clock timestamps instead of tick numbers

Using `Time.time` or system clock for snapshot timestamps breaks under jitter and clock drift. Stamp everything with monotonic tick numbers.

### Extrapolation runaway

When the snapshot buffer starves, unlimited extrapolation causes entities to fly off. Clamp dead-reckoning to ~2 ticks, then hold position.

### Uncapped lag compensation

Without a max rewind window, high-ping players can shoot enemies far in the past, dominating gameplay. Cap to 250–500 ms.

### Reliable channel for state snapshots

Sending per-tick state updates over a reliable ordered channel causes head-of-line blocking: one lost packet stalls all subsequent updates. Use unreliable unordered for snapshots.

## Verification

Check each item with the corresponding test or inspection:

- [ ] **Fixed tick:** Simulation runs on a fixed tick decoupled from render framerate; ticks are monotonic. Verify by logging `_tick` — it should increment by exactly 1 per simulation step, independent of FPS.
- [ ] **Clock sync:** Client input tick leads the server by ~RTT/2 + margin, and the offset self-corrects as RTT drifts. Verify by logging server-reported input arrival offset; it should converge to near-zero.
- [ ] **Prediction + reconciliation:** The local player predicts immediately and reconciles by replaying all unacknowledged inputs after the server-acked state. Verify: with 0 ms latency, no visible correction occurs; with 100 ms, corrections are sub-pixel.
- [ ] **Shared simulation:** Client and server run the *same* movement/simulation step (no forked logic). Verify by code review: one `Step()` function, shared module.
- [ ] **Remote interpolation:** Remote entities interpolate from a timestamped snapshot buffer with a tunable interpolation delay. Verify: remote movement is smooth at 60 FPS even with 5% packet loss.
- [ ] **Server authority:** The server is authoritative; clients send inputs only and all inputs are validated server-side (range, cooldown, rate). Verify: sending an out-of-bounds input from a modified client is rejected.
- [ ] **Channel selection:** Reliable vs unreliable channels are chosen correctly (events reliable, state snapshots unreliable). Verify: dropping 10% of packets does not stall state updates.
- [ ] **Lag compensation:** Server rewinds hitboxes to the shooter's view tick and is capped to a max rewind window. Verify: a shot that visually connects on the client registers on the server; a shot beyond the cap is rejected.
- [ ] **Delta compression:** State is delta-compressed against an acknowledged baseline and quantized/bit-packed. Verify: measure per-client bandwidth at 64 players; it should stay within budget (e.g. < 100 kbps).
- [ ] **Interest management:** Replication is limited to relevant entities per client. Verify: an entity outside the client's AoI produces zero snapshot traffic for that client.
- [ ] **Network simulation testing:** Tested under simulated latency, jitter, and packet loss (not just LAN). Run with `clumsy` or `netem`: 100 ms latency, 5% loss, 20 ms jitter.
- [ ] **Smooth corrections:** Corrections smooth small errors and snap only large ones (no per-tick teleporting). Verify: log position delta on reconcile; small deltas (< 0.01 m) are smoothed, large deltas snap.
- [ ] **Rollback determinism (if applicable):** Simulation is bit-deterministic with cheap save/load state and frame-seeded RNG. Verify: two clients given identical inputs produce identical state hashes per frame.

## Related skills

- **game-multiplayer-basics** — Godot peer creation, `@rpc` semantics, authority, and connection lifecycle under these sync models.
- **game-multiplayer-sync** — `MultiplayerSynchronizer`/`Spawner` configuration that implements this skill's replication design in Godot.
- **game-ai-behavior** — Replicate AI agent state/decisions produced by behavior trees and steering.
- **runtime-animation** — Network-drive locomotion params and sync animation state across clients.
- **game-performance-profiling** — Budget server tick CPU and per-client bandwidth; profile serialization cost.
- **game-steamworks-sdk** — Lobbies, P2P sessions, and relay transport on top of this netcode.

### External resources

- Gaffer On Games (networked physics, snapshot compression, deterministic lockstep).
- Valve "Source Multiplayer Networking" (prediction, interpolation, lag compensation).
- GGPO / rollback design notes.
