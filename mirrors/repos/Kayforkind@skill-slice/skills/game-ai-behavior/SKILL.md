---
name: game-ai-behavior
version: 1.0.1
description: "Designs classical game AI as three layers: decision (FSM, behavior trees, utility, GOAP/HTN), NavMesh/A-star pathfinding with funnel smoothing, and Reynolds steering/flocking plus bounded perception. Use when building or debugging enemy/NPC agents that get stuck, jitter, or clump. Not for netcode replication, animation blending, ML/RL policy training, or dialogue trees with no movement loop."
risk: safe
source: opus
date_added: 2026-06-27
---

# Game AI & Behavior

Decision-making (what to do), pathfinding (how to get there), and steering (how to move) are three separate layers. Keep them separate and most AI bugs disappear.

**Three layers, one direction:** Decision → Pathfinding → Steering. Decision sets a goal; pathing finds the route; steering moves the body. Violating this one-way data flow is the single most common source of AI bugs.

## When to Use

Activate when the task involves:

- Choosing a **decision architecture** (FSM vs behavior tree vs utility AI vs GOAP/HTN) for an agent.
- Implementing a **behavior tree** with composites, decorators, services, and a **blackboard**.
- **Pathfinding** on a NavMesh or grid: A*, path smoothing (funnel), hierarchical/portal graphs, flow fields.
- **Steering**: seek, flee, arrive, pursue, wander, obstacle/agent avoidance, path following, flocking.
- **Perception**: sight cones, line-of-sight raycasts, hearing/stimulus, target memory and forgetting.
- **Spatial reasoning**: influence maps, cover/EQS-style environment queries, tactical positioning.
- Debugging agents that get **stuck, jitter, oscillate between states, or clump**.

**Trigger keywords:** enemy AI, NPC behavior, behavior tree, blackboard, decorator, state machine, utility AI, GOAP, HTN planner, NavMesh, A*, path smoothing, funnel, flow field, steering, flocking/boids, perception, sight cone, influence map, EQS.

### Do not use for

- **Replicating AI state across the network** — own the *behavior*; let `multiplayer-netcode` own replication and authority.
- **Playing/blending the animations** an AI decision triggers — that is `runtime-animation` (locomotion blend trees, IK). This skill outputs intent (move here, attack); the animation skill realizes it.
- **ML/RL training pipelines** — this skill is classical, hand-authored game AI, not neural policy training.
- **Dialogue trees / narrative scripting** with no autonomous movement or decision loop.

## Prerequisites

- A game engine or framework with a navigation system (NavMesh, grid, or graph) and basic vector math utilities.
- For Unreal: built-in Behavior Trees, Blackboard, AIController, NavMesh (Recast), EQS, Perception component.
- For Unity: NavMeshAgent + NavMesh baking; behavior via Behavior Designer or custom BT; A* Pathfinding Project for grids/flow.
- For Godot 4: NavigationAgent2D/3D + NavigationServer (funnel built in), Area-based detection for perception, custom BT/FSM scripts.
- Windows host is primary (PowerShell). No external CLI tools required — this skill is architecture and code patterns, not a build pipeline.

## Procedure

### 1. Pick the decision architecture

| Architecture | Strength | Use when |
|---|---|---|
| **FSM / Hierarchical FSM** | Simple, debuggable | Few states, clear transitions (turret, simple guard) |
| **Behavior Tree** | Modular, reusable, designer-friendly | Most action-game enemies/NPCs |
| **Utility AI** | Smooth, emergent priority from scored options | Sims, many competing needs (The Sims-like) |
| **GOAP** | Plans action sequences to reach a goal | Emergent, tool-using agents (F.E.A.R.-style) |
| **HTN** | Authored task decomposition with planning | Squad tactics, structured plans |

**Default:** Behavior Tree + Blackboard, layered over NavMesh pathfinding and steering.

### 2. Implement the behavior tree core

Nodes return **Success / Failure / Running**. Ticking is top-down each frame; `Running` lets actions span frames.

- **Composites**: `Sequence` (AND — fail-fast), `Selector` (OR — succeed-fast), `Parallel`.
- **Decorators**: invert, cooldown, condition guard, repeat, time-limit.
- **Services**: run on a cadence while a subtree is active (e.g. refresh "best target" every 0.5 s).
- **Leaves**: condition checks and actions (MoveTo, Attack, PlayAnim-request).
- **Blackboard**: shared key/value memory (target, lastKnownPos, homePos) — the *only* coupling between nodes.

```csharp
enum Status { Success, Failure, Running }
abstract class Node { public abstract Status Tick(Blackboard bb); }

class Sequence : Node {
    readonly Node[] kids; int i;
    public override Status Tick(Blackboard bb) {
        for (; i < kids.Length; i++) {
            var s = kids[i].Tick(bb);
            if (s != Status.Success) return s;   // Running or Failure short-circuits
        }
        i = 0; return Status.Success;
    }
}

class Selector : Node {
    readonly Node[] kids;
    public override Status Tick(Blackboard bb) {
        foreach (var k in kids) {
            var s = k.Tick(bb);
            if (s != Status.Failure) return s;    // first non-failure wins
        }
        return Status.Failure;
    }
}
```

Typical combat tree: `Selector[ Sequence(CanSeeTarget?, Attack), Sequence(HasLastKnownPos?, Investigate), Patrol ]`.

### 3. Implement GOAP (when action sequencing is needed)

Each **action** declares preconditions and effects (as world-state booleans) plus a cost. The planner runs **A\* over world states** (not space): start = current world state, goal = desired state, neighbors = applicable actions. The resulting plan is an ordered action list the agent executes until the world changes and it replans.

```text
Actions:  Reload {pre: hasAmmoBox; eff: weaponLoaded; cost:2}
          AttackTarget {pre: weaponLoaded, targetVisible; eff: targetDead; cost:1}
Goal:     targetDead
Plan:     A* finds [Reload, AttackTarget] when weapon is empty.
```

### 4. Implement pathfinding: A* then smooth

1. **A\*** on the NavMesh polygon graph (or grid). Heuristic = octile/Euclidean; keep it admissible.
2. **String-pull / funnel** the polygon corridor into a minimal set of waypoints — raw A* output hugs cell corners and looks robotic.
3. **Hierarchical** (portal/region graph) for large maps: plan coarse region-to-region, refine locally.
4. **Flow fields** when *many* agents share one goal (tower defense, RTS swarms): compute a Dijkstra field once, every agent samples the gradient.

```csharp
List<Node> AStar(Node start, Node goal) {
    var open = new PriorityQueue<Node, float>();
    var g = new Dictionary<Node, float> { [start] = 0 };
    var came = new Dictionary<Node, Node>();
    open.Enqueue(start, Heuristic(start, goal));
    while (open.Count > 0) {
        var cur = open.Dequeue();
        if (cur == goal) return Reconstruct(came, cur);
        foreach (var (nbr, cost) in cur.Neighbors) {
            float ng = g[cur] + cost;
            if (ng < g.GetValueOrDefault(nbr, float.MaxValue)) {
                g[nbr] = ng; came[nbr] = cur;
                open.Enqueue(nbr, ng + Heuristic(nbr, goal)); // f = g + h
            }
        }
    }
    return null; // no path
}
```

### 5. Implement steering (Reynolds) — movement, not pathing

Steering produces a desired velocity; combine behaviors by **weighted sum or priority**, then clamp to max force/speed.

```csharp
Vector3 Seek(Vector3 pos, Vector3 target, Vector3 vel, float maxSpeed, float maxForce) {
    Vector3 desired = (target - pos).normalized * maxSpeed;
    return Vector3.ClampMagnitude(desired - vel, maxForce); // steering force
}
// Arrive: scale desired speed down inside a slowing radius to avoid overshoot.
// Flocking = Separation (push apart) + Alignment (match heading) + Cohesion (toward center).
// Obstacle avoidance: feeler rays; steer away from the nearest predicted collision.
```

Drive **path following** by seeking the next funnel waypoint with `Arrive` on the last one. Avoidance (RVO/ORCA or feelers) sits on top to prevent agent–agent overlap.

### 6. Implement perception

- **Sight**: target within view distance AND within FOV half-angle AND an unobstructed LoS raycast.
- **Hearing**: stimuli (gunshots, footsteps) register as events with intensity falloff.
- **Memory**: store `lastKnownPosition` + timestamp; investigate, then forget after a timeout so agents don't become omniscient.

```csharp
bool CanSee(Transform eye, Transform target, float range, float fovDeg) {
    Vector3 to = target.position - eye.position;
    if (to.magnitude > range) return false;
    if (Vector3.Angle(eye.forward, to) > fovDeg * 0.5f) return false;
    return !Physics.Raycast(eye.position, to.normalized, to.magnitude, obstacleMask);
}
```

### 7. Add debug visualization first

Before tuning, add debug draws for: path lines, FOV cones, current BT node, target position, steering force vector, and perception range spheres. AI is nearly impossible to debug blind.

## Examples

### Engine mappings

```text
Unreal:  Behavior Trees + Blackboard (built-in), AIController, NavMesh (Recast),
         EQS for environment queries (cover, flank points), Perception component.
Unity:   NavMeshAgent + NavMesh baking; behavior via Behavior Designer / custom BT;
         A* Pathfinding Project for grids/flow; steering hand-rolled or via add-ons.
Godot 4: NavigationAgent2D/3D + NavigationServer (funnel built in), Area-based
         detection for perception, custom BT/FSM scripts.
```

### Debugging scenarios

```
Input : "Agents jitter / vibrate when they reach the target."
Cause : Seek with no Arrive — they overshoot and snap back each frame.
Output: switch to Arrive (slow inside a radius), add a stop threshold, and stop
        repathing once within acceptance radius.
```

```
Input : "Enemies clump into one spot and overlap."
Cause : no agent avoidance / separation.
Output: add Separation steering or RVO/ORCA; give each a slot/formation offset
        around the target instead of all seeking the exact same point.
```

```
Input : "Agent oscillates between Patrol and Investigate every frame."
Cause : perception flickers on/off at the edge of detection range.
Output: add hysteresis (separate detect/lose thresholds) and a cooldown decorator
        on the transition.
```

## Pitfalls

1. **Never couple BT nodes by direct references.** The blackboard is the *only* shared state. Nodes that reference each other directly create spaghetti that is impossible to reorder or reuse.
2. **Never use raw Seek at the destination.** Seek has no slow-down — agents overshoot and jitter. Always use `Arrive` near goals with a stop threshold.
3. **Never skip funnel smoothing.** Unsmoothed A* paths hug polygon corners and look broken even when "correct."
4. **Never repath every frame.** Repath on a cadence or on significant target movement; stagger across agents (time-slicing) to avoid frame spikes.
5. **Never give perception omniscience.** FOV, range, LoS, and memory timeout make AI feel fair and fool-able. Without a memory timeout, agents never "forget" and feel psychic.
6. **Never let all agents seek the exact same point.** Without separation or formation slots, they clump and overlap. Use RVO/ORCA or slot offsets.
7. **Never use an inadmissible A* heuristic.** An overestimating heuristic produces suboptimal or broken paths. Use octile for grids, Euclidean for open NavMesh.
8. **Never blend decision and steering layers.** Decision sets a goal; pathing finds the route; steering moves the body. If steering feeds back into decision logic, you get circular dependencies and infinite oscillation.
9. **GOAP/HTN: never execute a stale plan.** Replan when the world state invalidates the current plan — otherwise agents act on outdated assumptions.

## Verification

- [ ] Decision, pathfinding, and steering are separate layers with one-way data flow (decision → path → steer).
- [ ] The chosen decision architecture fits the agent complexity (FSM for trivial, BT/utility/GOAP for richer).
- [ ] Behavior tree nodes return Success/Failure/Running and communicate only through the blackboard.
- [ ] A* uses an admissible heuristic and its corridor is funnel-smoothed before following.
- [ ] Large maps use hierarchical pathfinding; shared-goal swarms use flow fields.
- [ ] Steering uses Arrive (not raw Seek) near goals and clamps to max force/speed.
- [ ] Agent–agent avoidance (separation/RVO) prevents clumping and overlap.
- [ ] Perception is bounded by range, FOV, line-of-sight, and a memory timeout.
- [ ] Expensive work (repathing, perception scans) is throttled and staggered across agents.
- [ ] Debug visualization exists for paths, FOV cones, current state/node, and targets.
- [ ] (GOAP/HTN) Planner replans when the world state invalidates the current plan.

## Related skills

- **runtime-animation** — Realizes AI intent as locomotion blend trees, foot IK, and attack animations.
- **multiplayer-netcode** — Replicates AI agent state/decisions and resolves authority in networked play.
- **performance-profiling** — Time-slice perception/pathing and profile A* and steering across many agents.
- **custom-physics-solvers** — Spatial math behind steering, avoidance, and raycast perception.

### External resources

- Craig Reynolds, "Steering Behaviors For Autonomous Characters".
- "Game AI Pro" series (behavior trees, GOAP, utility, influence maps).
- Recast/Detour NavMesh documentation; funnel (string-pulling) algorithm.
