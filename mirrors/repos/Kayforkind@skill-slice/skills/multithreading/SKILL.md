---
name: multithreading
version: 1.1.1
description: "Offloads CPU-heavy Godot work via WorkerThreadPool, Thread/Mutex/Semaphore, call_deferred, and threaded resource load so the main thread keeps the ~16 ms frame. Use when Godot pathfinding, procedural generation, or background loads hitch rendering. Not for Python/C++/JS threading, profiling-first optimization (godot-optimization), or mutating the live scene tree from a worker. Never skip wait_for_task_completion (slot leak) or do GPU work off the main thread."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Multithreading

Run expensive work off the main thread without corrupting the scene tree. The main thread has a fixed budget per frame (~16 ms at 60 FPS); any single computation that overruns it stalls input, rendering, and physics. Threading buys back that budget — but only when the work is genuinely CPU-bound and touches no live engine state. Prefer `WorkerThreadPool` for short parallel jobs because it reuses a pre-allocated pool and hides thread lifetime management; reach for `Thread`/`Mutex`/`Semaphore` only when you need a long-lived worker that parks between bursts of work.

> **Related skills:** **godot-optimization** for profiling before threading, **assets-pipeline** for asset import, **csharp-godot** for C# specifics, **gdscript-advanced** for async/await pitfalls.

## When to Use

- **Off-load CPU-heavy calculations** (pathfinding cost maps, procedural generation, large simulations) so one expensive frame doesn't blow the 16 ms budget and cause a visible hitch.
- **Load resources or build scene chunks in the background** so the game keeps rendering a loading indicator instead of freezing on a synchronous `load()`.
- **Parallel iteration over many independent elements** with `WorkerThreadPool.add_group_task` — the win comes from spreading the per-element cost across cores, so it only pays off when each element does real work.
- **Long-lived workers** with `Thread`/`Mutex`/`Semaphore` when a job must survive across many frames and you want explicit control over when it sleeps, wakes, and shuts down.

## Prerequisites

- **Profile first.** Before adding threads, confirm the target code is genuinely CPU-bound using the Godot profiler or `Time.get_ticks_usec()`. Threading a cheap loop runs *slower* because scheduling and synchronization overhead dominate. See **godot-optimization**.
- **Engine threading model opt-in.** Servers (`RenderingServer`, `PhysicsServer2D/3D`) are thread-safe **only after you opt in** via Project Settings: `Rendering > Driver > Thread Model = Separate`, `Physics > {2D,3D} > Run on Separate Thread`. Left at default, concurrent calls race.
- **Windows host (primary).** Creating a thread is slow especially on Windows; pre-create long-lived workers before the heavy phase rather than spinning one up just-in-time. Use PowerShell for any host-side scripting.

## Procedure

### 1. Threading model & safety rules

The main thread owns the scene tree — **interacting with the active scene tree is not thread-safe.** Each rule below exists because the alternative is a silent data race:

- **Servers** (`RenderingServer`, `PhysicsServer2D/3D`) become thread-safe **only after opt-in** via Project Settings (`Rendering > Driver > Thread Model = Separate`, `Physics > {2D,3D} > Run on Separate Thread`). Once enabled they marshal commands through an internal queue. Left at default, concurrent calls race.
- **`NavigationServer2D/3D` are thread-safe and thread-friendly** — they run genuinely parallel queries. Tune `Navigation > Pathfinding > Max Threads` to match your core count.
- **`AStar2D/3D` and `AStarGrid2D` are NOT thread-safe.** One dedicated thread per object is the limit; sharing an instance corrupts internal caches.
- **GDScript `Array`/`Dictionary`:** reading and overwriting *existing* elements across threads is fine, but **adding, removing, or resizing needs a `Mutex`** — a resize can reallocate backing storage out from under a concurrent reader.
- **No GPU work off the main thread.** Texture creation and image read/modify trigger a RenderingServer sync stall, defeating the point of threading.
- **Build scene chunks off-tree, attach on the main thread.** Construct nodes in the worker, then add them via `add_child.call_deferred()` — and only from a *single* loader thread, because multiple loaders can mutate the same cached resource and crash.

> **Golden rule:** Mutate the scene tree only on the main thread. From a worker, hand results back with `call_deferred` / `set_deferred`.

### 2. WorkerThreadPool (preferred for short parallel jobs)

`WorkerThreadPool` is a global singleton whose threads are allocated once at startup — no per-job thread-creation cost. A regular task (`add_task`) runs once on one worker; a **group task** (`add_group_task`) is distributed across workers, invoking the `Callable` once per element index `0 .. elements-1`. **Every task must be waited on** (`wait_for_task_completion` / `wait_for_group_task_completion`), otherwise its allocated slot leaks.

**Safe pattern:** snapshot data into plain containers on the main thread, compute on that copy in workers, then apply results back on the main thread.

#### GDScript — Group task for per-enemy velocity

```gdscript
extends Node2D

const MAX_SPEED: float = 220.0

var _enemy_nodes: Array[Node2D] = []
var _positions: PackedVector2Array = PackedVector2Array()
var _desired_velocities: PackedVector2Array = PackedVector2Array()
var _player_position: Vector2 = Vector2.ZERO
var _spawn_cooldown: float = 0.0

func _ready() -> void:
    for child in get_tree().get_nodes_in_group("enemies"):
        if child is Node2D:
            _enemy_nodes.append(child)
    _positions.resize(_enemy_nodes.size())
    _desired_velocities.resize(_enemy_nodes.size())

func _compute_enemy_velocity(enemy_index: int) -> void:
    if enemy_index < 0 or enemy_index >= _positions.size():
        push_error("_compute_enemy_velocity: index %d out of range (0..%d)"
            % [enemy_index, _positions.size() - 1])
        return
    var to_player: Vector2 = _player_position - _positions[enemy_index]
    var distance: float = to_player.length()
    if distance < 0.001:
        _desired_velocities[enemy_index] = Vector2.ZERO
    else:
        _desired_velocities[enemy_index] = (to_player / distance) * MAX_SPEED

func _process(delta: float) -> void:
    var count: int = _enemy_nodes.size()
    if count == 0:
        return
    _player_position = get_global_mouse_position()
    for i in count:
        _positions[i] = _enemy_nodes[i].global_position
    var task_id: int = WorkerThreadPool.add_group_task(_compute_enemy_velocity, count)
    _spawn_cooldown = maxf(0.0, _spawn_cooldown - delta)
    WorkerThreadPool.wait_for_group_task_completion(task_id)
    for i in count:
        _enemy_nodes[i].position += _desired_velocities[i] * delta
```

#### C# — Group task equivalent

```csharp
using Godot;
using System.Collections.Generic;

public partial class EnemySwarm : Node2D
{
    private const float MaxSpeed = 220.0f;
    private readonly List<Node2D> _enemyNodes = new();
    private Vector2[] _positions = System.Array.Empty<Vector2>();
    private Vector2[] _desiredVelocities = System.Array.Empty<Vector2>();
    private Vector2 _playerPosition;
    private float _spawnCooldown;

    public override void _Ready()
    {
        foreach (Node child in GetTree().GetNodesInGroup("enemies"))
        {
            if (child is Node2D enemy)
                _enemyNodes.Add(enemy);
        }
        _positions = new Vector2[_enemyNodes.Count];
        _desiredVelocities = new Vector2[_enemyNodes.Count];
    }

    private void ComputeEnemyVelocity(int enemyIndex)
    {
        if (enemyIndex < 0 || enemyIndex >= _positions.Length)
        {
            GD.PushError($"ComputeEnemyVelocity: index {enemyIndex} out of range " +
                         $"(0..{_positions.Length - 1}).");
            return;
        }
        Vector2 toPlayer = _playerPosition - _positions[enemyIndex];
        float distance = toPlayer.Length();
        _desiredVelocities[enemyIndex] = distance < 0.001f
            ? Vector2.Zero
            : (toPlayer / distance) * MaxSpeed;
    }

    public override void _Process(double delta)
    {
        int count = _enemyNodes.Count;
        if (count == 0)
            return;
        _playerPosition = GetGlobalMousePosition();
        for (int i = 0; i < count; i++)
            _positions[i] = _enemyNodes[i].GlobalPosition;
        long taskId = WorkerThreadPool.AddGroupTask(
            Callable.From<int>(ComputeEnemyVelocity), count);
        _spawnCooldown = Mathf.Max(0.0f, _spawnCooldown - (float)delta);
        WorkerThreadPool.WaitForGroupTaskCompletion(taskId);
        for (int i = 0; i < count; i++)
            _enemyNodes[i].Position += _desiredVelocities[i] * (float)delta;
    }
}
```

> The element count must stay constant between snapshot and wait. If enemies spawn or die mid-frame, do that bookkeeping *outside* the dispatch/wait window.

### 3. Thread / Mutex / Semaphore (long-lived workers)

Use a raw `Thread` when a worker must outlive a single frame and park between bursts of work. Signatures: `Thread.start(callable: Callable, priority := PRIORITY_NORMAL) -> int`, `wait_to_finish()` (blocks until thread returns — call before the object is freed), `is_started()`. `Mutex` is reentrant (`lock`/`unlock`/`try_lock`); `Semaphore` exposes `wait()` (block) and `post(count := 1)` (release).

#### GDScript — Long-lived job queue

```gdscript
extends Node

var _mutex: Mutex
var _semaphore: Semaphore
var _thread: Thread
var _exit_thread: bool = false
var _job_queue: Array[Callable] = []

func _ready() -> void:
    _mutex = Mutex.new()
    _semaphore = Semaphore.new()
    _thread = Thread.new()
    var err: int = _thread.start(_thread_function)
    if err != OK:
        push_error("Failed to start worker thread: error %d" % err)

func _thread_function() -> void:
    while true:
        _semaphore.wait()
        _mutex.lock()
        var should_exit: bool = _exit_thread
        _mutex.unlock()
        if should_exit:
            break
        _mutex.lock()
        var job: Callable = Callable()
        if not _job_queue.is_empty():
            job = _job_queue.pop_front()
        _mutex.unlock()
        if job.is_valid():
            job.call()

func enqueue_job(job: Callable) -> void:
    assert(job.is_valid(), "enqueue_job requires a valid Callable")
    _mutex.lock()
    _job_queue.push_back(job)
    _mutex.unlock()
    _semaphore.post()

func _exit_tree() -> void:
    if _thread == null or not _thread.is_started():
        return
    _mutex.lock()
    _exit_thread = true
    _mutex.unlock()
    _semaphore.post()
    _thread.wait_to_finish()
```

#### C# — Long-lived job queue with System.Threading

In C#, `System.Threading` primitives are idiomatic. Note the `volatile` flag, the `lock` guarding the queue resize, and `try`/`catch` so one bad job doesn't tear down the worker:

```csharp
using Godot;
using System;
using System.Collections.Generic;
using System.Threading;

public partial class Worker : Node
{
    private readonly object _lock = new();
    private readonly SemaphoreSlim _semaphore = new(0);
    private readonly Queue<Action> _jobQueue = new();
    private Thread _thread;
    private volatile bool _exitThread;

    public override void _Ready()
    {
        _thread = new Thread(ThreadFunction) { IsBackground = true, Name = "GameWorker" };
        _thread.Start();
    }

    private void ThreadFunction()
    {
        while (true)
        {
            _semaphore.Wait();
            if (_exitThread)
                break;
            Action job = null;
            lock (_lock)
            {
                if (_jobQueue.Count > 0)
                    job = _jobQueue.Dequeue();
            }
            try
            {
                job?.Invoke();
            }
            catch (Exception ex)
            {
                GD.PushError($"Worker job threw and was skipped: {ex}");
            }
        }
    }

    public void EnqueueJob(Action job)
    {
        ArgumentNullException.ThrowIfNull(job);
        lock (_lock)
        {
            _jobQueue.Enqueue(job);
        }
        _semaphore.Release();
    }

    public override void _ExitTree()
    {
        if (_thread is null || !_thread.IsAlive)
            return;
        _exitThread = true;
        _semaphore.Release();
        _thread.Join();
        _semaphore.Dispose();
    }
}
```

### 4. Handing results back: `call_deferred` / `set_deferred`

Constructing a node off-tree is safe in a worker; *attaching* it to the live tree is not. `call_deferred` queues the call so it runs on the main thread during idle time.

#### GDScript

```gdscript
func _spawn_from_worker(world: Node) -> void:
    var enemy: Node2D = preload("res://enemy.tscn").instantiate()
    # Unsafe from a worker — mutates the live scene tree right now:
    # world.add_child(enemy)
    # Safe — queued and executed on the main thread during idle time:
    world.add_child.call_deferred(enemy)
```

#### C#

```csharp
private void SpawnFromWorker(Node world)
{
    PackedScene enemyScene = GD.Load<PackedScene>("res://enemy.tscn");
    Node2D enemy = enemyScene.Instantiate<Node2D>();
    // Unsafe from a worker:
    // world.AddChild(enemy);
    // Safe — use the MethodName StringName constant, NOT the literal "AddChild":
    world.CallDeferred(Node.MethodName.AddChild, enemy);
}
```

> **C# pitfall:** `CallDeferred("AddChild")` fails — the deferred/`Call`/`Connect` APIs resolve Godot's snake_case names, not C# PascalCase. Use `Node.MethodName.*` constants.

### 5. Threaded resource loading

`ResourceLoader.load_threaded_request(path)` kicks off a background load and returns an `Error` — check it. Then poll `load_threaded_get_status(path, progress)` each frame (`progress[0]` is 0–1). Only call `load_threaded_get(path)` once status reads `THREAD_LOAD_LOADED`. **`load_threaded_get` blocks exactly like a synchronous `load()` if the load is not finished.** Statuses: `THREAD_LOAD_INVALID_RESOURCE`, `THREAD_LOAD_IN_PROGRESS`, `THREAD_LOAD_FAILED`, `THREAD_LOAD_LOADED`.

#### GDScript

```gdscript
extends Control

const SCENE_PATH: String = "res://enemy.tscn"

@onready var _progress_bar: ProgressBar = $ProgressBar
var _progress: Array = []

func _ready() -> void:
    var err: int = ResourceLoader.load_threaded_request(SCENE_PATH)
    if err != OK:
        push_error("Could not start threaded load of %s: error %d" % [SCENE_PATH, err])
        set_process(false)

func _process(_delta: float) -> void:
    var status := ResourceLoader.load_threaded_get_status(SCENE_PATH, _progress)
    match status:
        ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            if not _progress.is_empty():
                _progress_bar.value = float(_progress[0]) * 100.0
        ResourceLoader.THREAD_LOAD_LOADED:
            var scene := ResourceLoader.load_threaded_get(SCENE_PATH) as PackedScene
            if scene == null:
                push_error("Loaded resource is not a PackedScene: %s" % SCENE_PATH)
                set_process(false)
                return
            add_child(scene.instantiate())
            set_process(false)
        ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
            push_error("Threaded load failed: %s" % SCENE_PATH)
            set_process(false)
        _:
            pass
```

#### C#

```csharp
using Godot;

public partial class ThreadedLoader : Control
{
    private const string ScenePath = "res://enemy.tscn";
    private ProgressBar _progressBar;
    private Godot.Collections.Array _progress = new();

    public override void _Ready()
    {
        _progressBar = GetNode<ProgressBar>("ProgressBar");
        Error err = ResourceLoader.LoadThreadedRequest(ScenePath);
        if (err != Error.Ok)
        {
            GD.PushError($"Could not start threaded load of {ScenePath}: error {err}");
            SetProcess(false);
        }
    }

    public override void _Process(double delta)
    {
        ResourceLoader.ThreadLoadStatus status =
            ResourceLoader.LoadThreadedGetStatus(ScenePath, _progress);
        switch (status)
        {
            case ResourceLoader.ThreadLoadStatus.InProgress:
                if (_progress.Count > 0)
                    _progressBar.Value = (float)_progress[0] * 100.0f;
                break;
            case ResourceLoader.ThreadLoadStatus.Loaded:
                var scene = ResourceLoader.LoadThreadedGet(ScenePath) as PackedScene;
                if (scene == null)
                {
                    GD.PushError($"Loaded resource is not a PackedScene: {ScenePath}");
                    SetProcess(false);
                    return;
                }
                AddChild(scene.Instantiate());
                SetProcess(false);
                break;
            case ResourceLoader.ThreadLoadStatus.Failed:
            case ResourceLoader.ThreadLoadStatus.InvalidResource:
                GD.PushError($"Threaded load failed: {ScenePath}");
                SetProcess(false);
                break;
        }
    }
}
```

### 6. C# `Task.Run` for fire-and-forget CPU work

For one-off CPU work in C#, `System.Threading.Tasks.Task.Run` is simpler than spinning a raw `Thread`. The work must be pure CPU — no Godot objects. Marshal results back with `CallDeferred`.

```csharp
using Godot;
using System;

public partial class PrimeCounter : Node
{
    public override void _Ready()
    {
        _ = System.Threading.Tasks.Task.Run(() =>
        {
            try
            {
                int result = ExpensiveComputation(2_000_000);
                CallDeferred(MethodName.OnComputed, result);
            }
            catch (Exception ex)
            {
                GD.PushError($"Background computation failed: {ex}");
            }
        });
    }

    private static int ExpensiveComputation(int iterations)
    {
        if (iterations <= 0)
            throw new ArgumentOutOfRangeException(
                nameof(iterations), iterations, "iterations must be positive.");
        int primeCount = 0;
        for (int n = 2; n < iterations; n++)
        {
            if (IsPrime(n))
                primeCount++;
        }
        return primeCount;
    }

    private static bool IsPrime(int n)
    {
        if (n < 2)
            return false;
        for (int d = 2; (long)d * d <= n; d++)
        {
            if (n % d == 0)
                return false;
        }
        return true;
    }

    private void OnComputed(int result) => GD.Print($"Done: found {result} primes.");
}
```

> **Deeper reference:** Load `references/pitfalls.md` when you encounter data races, the `ERR_BUSY` nested-wait deadlock, or need to decide whether threading actually helps. Load `references/` directory contents as needed for extended patterns.

## Pitfalls

- **Trivial work threaded is slower.** Dispatching and synchronizing costs real time; for a cheap loop the overhead dominates. Profile first.
- **GPU operations from a worker.** Texture creation, image read/modify force RenderingServer synchronization — a stall usually worse than doing the work inline.
- **`AStar2D`/`AStar3D`/`AStarGrid2D` are NOT thread-safe.** One dedicated thread per instance; sharing corrupts internal caches.
- **Mutating the live scene tree from a background thread.** Node attach/detach and most property writes assume single-threaded access — a data race that crashes intermittently and is nearly impossible to reproduce.
- **Raw `Thread` for short fire-and-forget jobs.** `wait_to_finish()` is the *correct* way to join — the deadlock people blame on it comes from calling it while the worker is still parked on `Semaphore.wait()`. Signal the worker to exit first, *then* join. For short parallel jobs, `WorkerThreadPool` (or .NET `Task`) is simpler.
- **`Mutex`/`Semaphore` without discipline.** A lock acquired in inconsistent order across threads deadlocks; a forgotten `unlock()` freezes every thread waiting on it. Keep critical sections tiny, always pair `lock()`/`unlock()`, acquire multiple mutexes in one fixed global order.
- **`Array`/`Dictionary` resize without `Mutex`.** Reading/overwriting existing elements is fine; adding, removing, or resizing needs a `Mutex` — a resize can reallocate backing storage out from under a concurrent reader.
- **C# `CallDeferred("AddChild")` fails.** The deferred/`Call`/`Connect` APIs resolve Godot's snake_case names, not C# PascalCase. Use `Node.MethodName.*` constants.
- **`load_threaded_get` called before `THREAD_LOAD_LOADED`.** It blocks exactly like a synchronous `load()`. Always poll status first.
- **Un-waited `WorkerThreadPool` tasks.** Each `add_task`/`add_group_task` must have exactly one matching `wait_for_*_completion`. An un-waited task leaks its slot; a double wait returns `ERR_INVALID_PARAMETER`.
- **Multiple loader threads attaching to the tree.** Multiple loaders can mutate the same cached resource and crash. Use a single loader thread.
- **Thread creation on Windows is slow.** Pre-create long-lived workers before the heavy phase rather than spinning one up just-in-time.

## Verification

- [ ] **Profile first.** Time the section (Godot profiler, or `Time.get_ticks_usec()` around it) and confirm it is genuinely CPU-bound.
- [ ] **Balance every task with one wait.** Each `add_task`/`add_group_task` must have exactly one matching `wait_for_*_completion`: un-waited task leaks its slot, double wait returns `ERR_INVALID_PARAMETER`.
- [ ] **No scene-tree access off-thread.** Audit worker bodies for `add_child`, `get_node`, or property writes on live nodes; route all through `call_deferred`/`set_deferred`.
- [ ] **Exercise the threaded path under load** (run with `--verbose`) to surface data races and the `ERR_BUSY` nested-wait deadlock described in `references/pitfalls.md`.
- [ ] **Poll before fetching loads.** Confirm threaded loads reach `THREAD_LOAD_LOADED` and that `load_threaded_get` is never called earlier — calling it early blocks the main thread exactly like a synchronous `load()`.
- [ ] **Balance every lock.** Confirm each `Mutex.lock()` has a matching `unlock()` on every path (including early `return`/`break`), and that multiple mutexes are always acquired in one fixed global order.
- [ ] **Shut workers down cleanly.** Confirm long-lived `Thread`s are signalled to exit and joined (`wait_to_finish()` / `Join()`) in `_exit_tree`, so quitting the game doesn't hang on a parked worker.

## Examples

### Example 1 — Parallel element processing (GDScript)

```gdscript
extends Node

var _values: PackedFloat64Array = PackedFloat64Array()
var _results: PackedFloat64Array = PackedFloat64Array()

func _ready() -> void:
    _values.resize(10000)
    _results.resize(10000)
    for i in _values.size():
        _values[i] = float(i)
    recompute()

func _square(index: int) -> void:
    if index < 0 or index >= _values.size():
        push_error("_square: index %d out of range" % index)
        return
    _results[index] = _values[index] * _values[index]

func recompute() -> void:
    var task_id: int = WorkerThreadPool.add_group_task(_square, _values.size())
    WorkerThreadPool.wait_for_group_task_completion(task_id)
    print("results[9999] = %f" % _results[9999])
```

### Example 2 — Producer/consumer with Semaphore (C#)

```csharp
using Godot;
using System;
using System.Collections.Generic;
using System.Threading;

public partial class HashWorker : Node
{
    [Signal]
    public delegate void HashReadyEventHandler(long checksum);

    private readonly object _lock = new();
    private readonly SemaphoreSlim _semaphore = new(0);
    private readonly Queue<byte[]> _inbox = new();
    private Thread _thread;
    private volatile bool _exit;

    public override void _Ready()
    {
        _thread = new Thread(Run) { IsBackground = true, Name = "HashWorker" };
        _thread.Start();
    }

    public void Submit(byte[] data)
    {
        ArgumentNullException.ThrowIfNull(data);
        lock (_lock)
        {
            _inbox.Enqueue(data);
        }
        _semaphore.Release();
    }

    private void Run()
    {
        while (true)
        {
            _semaphore.Wait();
            if (_exit)
                break;
            byte[] job = null;
            lock (_lock)
            {
                if (_inbox.Count > 0)
                    job = _inbox.Dequeue();
            }
            if (job is null)
                continue;
            long checksum = unchecked((long)1469598103934665603UL);
            foreach (byte b in job)
            {
                checksum ^= b;
                checksum *= 1099511628211;
            }
            CallDeferred(MethodName.PublishHash, checksum);
        }
    }

    private void PublishHash(long checksum) => EmitSignal(SignalName.HashReady, checksum);

    public override void _ExitTree()
    {
        if (_thread is null || !_thread.IsAlive)
            return;
        _exit = true;
        _semaphore.Release();
        _thread.Join();
        _semaphore.Dispose();
    }
}
```

### Example 3 — Threaded scene loading (GDScript)

```gdscript
extends Node

signal scene_ready(instance: Node)

const TARGET: String = "res://levels/level_2.tscn"

var _progress: Array = []
var _loading: bool = false

func begin_load() -> void:
    var err: int = ResourceLoader.load_threaded_request(TARGET)
    if err != OK:
        push_error("Load request failed for %s (error %d)" % [TARGET, err])
        return
    _loading = true
    set_process(true)

func _process(_delta: float) -> void:
    if not _loading:
        return
    var status := ResourceLoader.load_threaded_get_status(TARGET, _progress)
    match status:
        ResourceLoader.THREAD_LOAD_IN_PROGRESS:
            var ratio: float = float(_progress[0]) if not _progress.is_empty() else 0.0
            print("Loading %s: %d%%" % [TARGET, int(ratio * 100.0)])
        ResourceLoader.THREAD_LOAD_LOADED:
            _loading = false
            set_process(false)
            var packed := ResourceLoader.load_threaded_get(TARGET) as PackedScene
            if packed != null:
                scene_ready.emit(packed.instantiate())
            else:
                push_error("%s did not load as a PackedScene" % TARGET)
        ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
            _loading = false
            set_process(false)
            push_error("Threaded load failed for %s" % TARGET)
```

## Related skills

- **godot-optimization** — profile *before* adding threads; threading a non-bottleneck only adds overhead.
- **assets-pipeline** — prepare and import assets so background loading has something efficient to stream.
- **csharp-godot** — C#-specific threading and marshalling considerations.
- **gdscript-advanced** — `await`, coroutines, and deferred-call pitfalls.
