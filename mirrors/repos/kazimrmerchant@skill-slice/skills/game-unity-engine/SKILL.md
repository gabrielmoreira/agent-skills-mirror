---
name: game-unity-engine
version: 1.0.2
description: "Use when building games in Unity 6.x with C# — MonoBehaviour lifecycle and component architecture, prefabs and ScriptableObjects, the Input System, coroutines vs async/await, object pooling and GC-aware patterns, Addressables asset loading, DOTS/ECS and the Job System + Burst, and URP/HDRP render-pipeline choices. Triggers on Unity, MonoBehaviour, ScriptableObject, prefab, Addressables, Job System, Burst, ECS, DOTS, URP, HDRP, Awake, Start, Update, FixedUpdate, coroutine. Not for AI-prompt-driven Unity project scaffolding (use unity-ai-game-creator), Unreal (use game-unreal-engine), Godot (use game-godot-master), or Blender authoring (use game-blender-asset-pipeline)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Unity Engine

C# architecture, the component/data models, performance patterns, and rendering choices for Unity 6.x (the unified successor to 2022 LTS / 2023).

## When to Use

- Writing **C# gameplay** with the `MonoBehaviour` lifecycle and a component-based architecture.
- Structuring data and config with **prefabs** and **ScriptableObjects**.
- Handling input via the **Input System** package (action maps), not the legacy `Input` manager.
- Choosing **coroutines vs async/await**, and avoiding per-frame allocations / GC spikes.
- Loading assets with **Addressables** (and getting off direct `Resources`/hard references).
- Going data-oriented: **DOTS/ECS**, the **Job System**, and **Burst** for heavy simulation.
- Picking and configuring a render pipeline: **URP** (broad/mobile) vs **HDRP** (high-end).

### Do not use

| If the task is… | Use instead |
|---|---|
| Turning a raw idea into a Unity plan with AI-generated assets/prompts | `unity-ai-game-creator` |
| Unreal Engine C++/Blueprints | `game-unreal-engine` |
| Godot 4.x | `game-godot-master` |
| Authoring/exporting meshes & rigs in Blender | `game-blender-asset-pipeline` |
| FMOD/Wwise middleware | `game-fmod-wwise-integration` |
| App Store/Play IAP, ads, Game Center | `game-mobile-store-integration` |

`unity-ai-game-creator` is an AI-asset **workflow** wrapper (idea → roadmap → generation prompts). This skill is the **engine reference**: how Unity actually executes, and the C#/architecture patterns that hold up in production.

## Prerequisites

- **Unity 6.x** installed (or Unity 2022 LTS / 2023 with compatible APIs). Confirm version in `ProjectSettings/ProjectVersion.txt`.
- **C# 9.0+** support (default in Unity 6). For `Awaitable`, Unity 6 is required; on older versions use UniTask.
- **Input System** package installed: `Window → Package Manager → Input System` (version 1.7+).
- **Addressables** package installed: `Window → Package Manager → Addressables` (version 2.x+ for Unity 6).
- **Burst** and **Collections** packages installed if using Job System / DOTS.
- Render pipeline package installed: `Universal RP` for URP, `High Definition RP` for HDRP.
- Windows host is primary (PowerShell). Paths use backslashes on Windows; forward slashes on macOS/Linux.

## Procedure

### 1. MonoBehaviour lifecycle — know the order

| Callback | When | Use for |
|---|---|---|
| `Awake` | On instantiation, before any `Start` | Self-setup, cache `GetComponent` — **no cross-object refs yet** |
| `OnEnable` | Each time the object enables | Subscribe to events |
| `Start` | Before first frame, after all `Awake`s | Cross-object wiring (others are now awake) |
| `FixedUpdate` | Fixed physics step | **All physics** — forces, `Rigidbody` moves |
| `Update` | Every frame | Input, game logic, non-physics |
| `LateUpdate` | After all `Update`s | Camera follow, post-movement adjustments |
| `OnDisable`/`OnDestroy` | Disable/teardown | Unsubscribe, release |

**Rule:** read input in `Update`, move rigidbodies in `FixedUpdate`, follow with the camera in `LateUpdate`. Mixing these causes jitter and missed input.

```csharp
public class PlayerController : MonoBehaviour
{
    private Rigidbody _rb;
    private Vector2 _moveInput;

    void Awake()
    {
        _rb = GetComponent<Rigidbody>(); // cache once
    }

    void OnEnable()  => InputManager.OnMove += HandleMove;
    void OnDisable() => InputManager.OnMove -= HandleMove;

    void HandleMove(Vector2 dir) => _moveInput = dir;

    void FixedUpdate()
    {
        // Physics moves belong here — fixed timestep, deterministic.
        _rb.linearVelocity = new Vector3(_moveInput.x, 0f, _moveInput.y) * 5f;
    }
}
```

### 2. Component & data architecture

```csharp
// ScriptableObject: shared, designer-tunable data — one asset, referenced by many.
[CreateAssetMenu(menuName = "Game/EnemyDef")]
public class EnemyDef : ScriptableObject
{
    public float maxHealth = 100f;
    public float moveSpeed = 3f;
    public GameObject prefab;
}
```

- Prefer **composition** (small components) over deep `MonoBehaviour` inheritance.
- Put **shared config in ScriptableObjects**, not duplicated across prefab instances — one source of truth, no per-instance drift, and they're editable without touching scenes.
- ScriptableObjects also make clean **event channels** and runtime sets, decoupling systems that shouldn't reference each other directly.

```csharp
// Event channel pattern — decoupled raise/listen.
[CreateAssetMenu(menuName = "Game/FloatEvent")]
public class FloatEventChannel : ScriptableObject
{
    private System.Action<float> _onRaised;
    public void Raise(float value) => _onRaised?.Invoke(value);
    public void Register(System.Action<float> handler) => _onRaised += handler;
    public void Deregister(System.Action<float> handler) => _onRaised -= handler;
}
```

### 3. Performance: allocations & GC

```csharp
// BAD: allocates every frame -> GC spikes -> frame hitches.
void Update() {
    var hits = Physics.OverlapSphere(transform.position, 5f); // new array each call
    foreach (var go in FindObjectsOfType<Enemy>()) { /* ... */ } // very expensive
}

// GOOD: non-alloc API + cached refs + pooling.
readonly Collider[] _buf = new Collider[16];
void Update() {
    int n = Physics.OverlapSphereNonAlloc(transform.position, 5f, _buf);
    for (int i = 0; i < n; i++) { /* ... */ }
}
```

- **Never** call `Find`/`GetComponent`/`FindObjectsOfType` in `Update` — cache references in `Awake`/`Start`.
- **Pool** bullets, enemies, VFX with the built-in `ObjectPool<T>` (or your own) instead of `Instantiate`/`Destroy` churn.
- Prefer **NonAlloc** physics queries and `struct`s/cached buffers in hot paths; boxing and per-frame `new` feed the GC and cause stutter.
- Avoid `string` concatenation and LINQ in hot loops.

```csharp
// Object pooling with UnityEngine.Pool.
using UnityEngine.Pool;

public class BulletPool : MonoBehaviour
{
    [SerializeField] private GameObject _bulletPrefab;
    private ObjectPool<GameObject> _pool;

    void Awake()
    {
        _pool = new ObjectPool<GameObject>(
            createFunc: () => Instantiate(_bulletPrefab, transform),
            actionOnGet: go => go.SetActive(true),
            actionOnRelease: go => go.SetActive(false),
            collectionCheck: true,
            defaultCapacity: 32,
            maxSize: 256);
    }

    public GameObject Spawn(Vector3 pos, Quaternion rot)
    {
        var go = _pool.Get();
        go.transform.SetPositionAndRotation(pos, rot);
        return go;
    }

    public void Despawn(GameObject go) => _pool.Release(go);
}
```

### 4. Coroutines vs async/await

- **Coroutines** are frame-tied (`yield return null`, `WaitForSeconds`) and auto-stop with the GameObject — good for timed gameplay sequences.
- **async/await** (with `Awaitable` in Unity 6 or UniTask) suits I/O, Addressables loads, and work that shouldn't be tied to a single object's lifetime — but **you** must cancel it (CancellationToken) when the scene/object goes away, or you touch destroyed objects.

```csharp
// Coroutine — frame-tied, auto-stops with GameObject.
IEnumerator ReloadRoutine(float delay)
{
    yield return new WaitForSeconds(delay);
    // resume reload
}

// async/await with Awaitable (Unity 6) — must cancel on teardown.
private CancellationTokenSource _cts;
void OnEnable() => _cts = new CancellationTokenSource();
void OnDisable() => _cts?.Cancel();

async Awaitable LoadAssetAsync(string key)
{
    try
    {
        var handle = Addressables.LoadAssetAsync<GameObject>(key);
        await handle.Task.WaitAsync(_cts.Token);
        // use handle.Result
    }
    catch (OperationCanceledException) { /* expected on teardown */ }
}
```

### 5. Addressables

- Move off hard prefab references and `Resources/` (which forces everything into the build and memory). **Addressables** load by address, support remote content, and let you **release** memory explicitly.
- Track handles and call `Addressables.Release` / release the handle when done — leaked handles keep assets resident.
- `InstantiateAsync` for spawnables; group and label assets to control what ships and downloads.

```csharp
// Load, instantiate, and release correctly.
private GameObject _instance;
private AsyncOperationHandle<GameObject> _handle;

async Awaitable SpawnEnemyAsync(string address, Vector3 pos)
{
    _handle = Addressables.InstantiateAsync(address, pos, Quaternion.identity);
    await _handle.Task.WaitAsync(_cts.Token);
    _instance = _handle.Result;
}

void DespawnEnemy()
{
    if (_instance != null)
    {
        Addressables.ReleaseInstance(_instance);
        _instance = null;
    }
}
```

### 6. DOTS / ECS, Jobs, Burst

- Reach for **ECS** when you have thousands of similar entities (bullets, units, boids) where cache-friendly data layout and parallelism dominate. It's a different paradigm (data in components, logic in systems) — don't rewrite a small game in it for novelty.
- The **C# Job System** + **Burst** compiler parallelize and SIMD-optimize tight numeric work even **without** full ECS — great for procedural gen, pathfinding grids, mesh deformation.
- Don't touch `UnityEngine` objects (Transforms, GameObjects) from jobs; jobs operate on `NativeArray`/blittable data. Use the Transform access jobs / ECS for transforms.

```csharp
using Unity.Burst;
using Unity.Collections;
using Unity.Jobs;
using Unity.Mathematics;

[BurstCompile]
struct VelocityJob : IJobParallelFor
{
    public NativeArray<float3> positions;
    [ReadOnly] public NativeArray<float3> velocities;
    public float dt;

    public void Execute(int i)
    {
        positions[i] += velocities[i] * dt; // blittable data only
    }
}

// Schedule from main thread, complete before reading.
var job = new VelocityJob
{
    positions = _positions,
    velocities = _velocities,
    dt = Time.deltaTime
};
JobHandle handle = job.Schedule(_positions.Length, 64);
handle.Complete();
```

### 7. Render pipeline choice

| | URP | HDRP | Built-in (legacy) |
|---|---|---|---|
| Target | Mobile, Switch, broad PC, VR | High-end PC/console | Avoid for new projects |
| Look | Scalable, lighter | Film-grade, physical lights | — |
| Cost | Lower | Heavy | — |

Pick the pipeline **at project start** — switching later means re-authoring every material. URP is the default for most games; HDRP only when you need its high-end lighting and can afford the hardware target.

## Pitfalls

1. **`GetComponent`/`Find` in `Update`**: cache in `Awake`/`Start`; per-frame lookups are a classic hotspot.
2. **Physics in `Update`**: rigidbody moves belong in `FixedUpdate`, or motion is framerate-dependent and jittery.
3. **`Instantiate`/`Destroy` churn**: pool instead; `Destroy` feeds the GC and fragments memory.
4. **Per-frame allocations**: NonAlloc APIs, no LINQ/string-building in hot loops.
5. **Everything in `Resources/`**: bloats build + memory; use Addressables and release handles.
6. **Async work not cancelled**: awaited tasks touching destroyed objects → null refs. Use CancellationToken tied to lifetime.
7. **Touching Unity objects from jobs**: not thread-safe; jobs use NativeArrays only.
8. **Switching render pipeline mid-project**: re-authors all materials. Decide URP vs HDRP up front.
9. **Deep MonoBehaviour inheritance**: prefer composition + ScriptableObject data.
10. **Coroutines surviving scene loads**: coroutines stop with their GameObject, but a `DontDestroyOnLoad` host keeps them running — verify the host is cleaned up.
11. **ScriptableObject runtime mutation**: changes to a ScriptableObject at runtime persist in the editor but not in builds. Never rely on runtime mutation for save data.

## Verification

- [ ] Input in `Update`, rigidbody motion in `FixedUpdate`, camera in `LateUpdate`.
- [ ] No `Find`/`GetComponent`/`FindObjectsOfType` in per-frame code; references cached.
- [ ] Spawned objects are pooled; hot paths use NonAlloc APIs and avoid LINQ/string alloc.
- [ ] Shared config lives in ScriptableObjects, not duplicated per instance.
- [ ] Assets load via Addressables with handles released; not dumped in `Resources/`.
- [ ] async/await work is cancelled on scene/object teardown.
- [ ] Jobs/Burst operate on NativeArrays only; no engine-object access inside jobs.
- [ ] Render pipeline (URP/HDRP) chosen at project start and matches the hardware target.

### Checkable commands

```powershell
# Confirm Unity project version (Windows / PowerShell).
Get-Content .\ProjectSettings\ProjectVersion.txt

# List installed packages to verify Input System, Addressables, Burst, Collections, URP/HDRP.
Get-Content .\Packages\manifest.json | Select-String "inputsystem|addressables|burst|collections|urp|hdrp"

# Check for Resources folder bloat (should be minimal or empty).
Get-ChildItem -Recurse -Directory -Filter "Resources" | Select-Object FullName

# Search codebase for per-frame anti-patterns (should return zero hits in hot paths).
Select-String -Path .\Assets\**\*.cs -Pattern "FindObjectsOfType|Find\(|GetComponent" | Where-Object { $_.Line -match "Update|FixedUpdate|LateUpdate" }
```

## Related skills

- `unity-ai-game-creator` — AI-driven idea→project scaffolding and asset-prompt workflow that sits on top of this engine reference.
- `game-unreal-engine` — Cross-engine counterpart for C++/Blueprint projects.
- `game-blender-asset-pipeline` — Authoring/exporting the meshes and rigs Unity imports.
- `game-fmod-wwise-integration` — Middleware audio that plugs into a Unity build.
- `game-mobile-store-integration` — IAP, ads, Game Center for Unity mobile builds.
- `game-steamworks-sdk` — Steam integration for Unity PC builds.

## References

- **Unity 6 Scripting API and Manual** — MonoBehaviour execution order, Input System, Addressables. Load when verifying lifecycle callbacks or Input System action map setup.
- **Unity DOTS/Entities, C# Job System, and Burst documentation** — Load when implementing ECS systems, scheduling jobs, or writing `[BurstCompile]` code.
- **Universal RP (URP) and High Definition RP (HDRP) documentation** — Load when configuring render pipeline assets, volume overrides, or shader graph.
