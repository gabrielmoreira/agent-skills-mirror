# Composition Architecture

Use this reference when designing or refactoring gameplay entities around composition.

## Principle

Composition means building entities from small capabilities they have, rather than forcing them into rigid inheritance categories they are. Prefer "has health", "has movement", "has attack", "has inventory", and "has interaction" over large `Player`, `Enemy`, or `Character` base classes that accumulate every possible behavior.

## Use Composition When

- A player, enemy, prop, item, projectile, vehicle, or environmental actor needs a behavior that another object may also need.
- A script is growing because every new ability, lockout, animation, input rule, or damage rule is added to the same file.
- A base class is gaining optional behavior that many subclasses disable or ignore.
- UI, debugging, save/load, or AI needs direct access to a specific slice of state such as health, velocity, inventory, cooldowns, or status effects.
- A behavior should be testable in a tiny scene or harness without the full character or level.

## Component Responsibilities

- `HealthComponent`: max/current health, damage, healing, death state, invulnerability windows, damage events.
- `InputComponent`: sampled player or AI input intent, not movement physics.
- `MovementComponent`: velocity, acceleration, grounded state, movement constraints, and collision movement calls.
- `AttackComponent`: attack state, cooldowns, hit timing, stamina/resource checks, and emitted attack events.
- `HurtboxComponent`: receives hit queries and forwards damage payloads.
- `HitboxComponent`: detects targets and emits hit payloads.
- `InteractionComponent`: exposes affordances, prompts, and interaction events.
- `CameraComponent`: target follow behavior, look offsets, shake, and camera constraints.

Adjust names to the engine and project conventions.

## Communication Rules

- Prefer signals, events, message buses, delegates, interfaces, or narrow typed references over broad owner lookups.
- Components should not assume their owner is a player unless that is their explicit job.
- Components may expose state and commands, but should avoid reaching across siblings to mutate hidden state.
- Entity-level scripts should orchestrate cross-component rules such as "attack locks movement", "blocking slows movement", or "death disables input".
- Keep dependency direction readable. If two components constantly know about each other, merge them or introduce an orchestrator.

## Engine Mapping

- Godot: use child nodes as components, `class_name` for reusable types, exported typed references for explicit wiring, signals for notifications, and isolated scenes for component tests.
- Unity: use focused `MonoBehaviour` components, serialized fields, UnityEvents/C# events, interfaces, and prefab variants only when they reduce duplication.
- Unreal: use Actor Components, Blueprint interfaces, event dispatchers, gameplay tags, and data assets for configuration.
- ECS engines: composition may already be native; focus on data ownership, system boundaries, and avoiding accidental god systems.
- Custom engines: keep component lifecycle, update order, event routing, serialization, and ownership explicit.

## Refactor Heuristic

When a feature request touches a large script, first list the responsibilities in that script. Extract a component only when the responsibility has a clear owner, can be named simply, and can be tested or reused independently. Leave tightly coupled behavior together until a real split appears.

## Review Questions

- Can this component work on a neutral object, such as a chest or rock, if the required data exists?
- Can another object reuse it without copying player-specific logic?
- Does the orchestrator remain short and readable?
- Are component references explicit enough to survive scene or prefab reorganization?
- Is the component easier to test after the split?
