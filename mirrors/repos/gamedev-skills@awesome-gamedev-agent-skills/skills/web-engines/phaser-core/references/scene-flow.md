# Phaser 3 scene flow (Phaser 3.90)

The Scene Manager runs every scene through a small state machine. Knowing which
transition verb does what prevents the most common Phaser bugs: hidden scenes,
stale state after a restart, and duplicate event listeners.

## Lifecycle order

A scene is **booted once** (status `INIT`) and can be **started any number of
times**. On each start it runs:

```
start → (loading, if preload queued anything) → create → running
```

- `init(data)` — runs first on every start. **Reset run-specific state here.**
- `preload()` — queue asset downloads. Optional.
- `create(data)` — build game objects; assets queued in `preload` are now ready.
- `update(time, delta)` — called every frame while the scene is `running`.

The same `data` object is passed to `init` and `create`, coming from
`scene.start(key, data)` / `scene.launch(key, data)`.

## Transition verbs

| Method | Effect on target | Effect on caller |
|--------|------------------|------------------|
| `start(key, data)` | start (or restart) | **stop** the caller |
| `launch(key, data)` | start in parallel | caller keeps running |
| `switch(key)` | start or wake | **sleep** the caller |
| `pause(key?)` | stop updating, keep rendering | — |
| `resume(key?)` | resume updating | — |
| `sleep(key?)` | stop updating AND rendering, keep state | — |
| `wake(key?)` | resume a sleeping scene | — |
| `stop(key?)` | shutdown (frees objects) | — |

Rules of thumb:

- **HUD/overlay** → `launch` it once; it renders on top because later scenes draw
  later. Toggle with `setVisible()` or `sleep`/`wake`, not `start`.
- **Modal pause menu** → `pause` the gameplay scene and `launch` the menu; `resume`
  on close.
- **Title ⇄ gameplay you revisit** → prefer `sleep`/`wake` (state preserved, starts
  only once) over `stop`/`start` (fresh each time) when re-initialisation is costly.

## The restart-state bug

A Scene is a long-lived instance. Fields set in the constructor are set **once**,
so they keep their last value after a restart:

```js
// WRONG — gameOver stays true forever after the first game over.
export default class Play extends Phaser.Scene {
  constructor() {
    super('play');
    this.gameOver = false;   // runs once, never again
  }
}

// RIGHT — init() runs on every (re)start.
export default class Play extends Phaser.Scene {
  constructor() { super('play'); }
  init() { this.gameOver = false; }
}
```

The same applies to module-level arrays that collect game objects: clear them on
`shutdown`, or they will hold destroyed objects from the previous run.

```js
create() {
  this.enemies = [];
  // Clean up when the scene stops so the next run starts empty.
  this.events.once('shutdown', () => { this.enemies.length = 0; });
}
```

## Duplicate listeners

Listeners added in `create` on a **global** emitter (the registry, the input
manager, another scene) survive scene restarts and stack up. Either:

- add them with `.once(...)`, or
- remove them on `shutdown`:

```js
create() {
  const onChange = (p, v) => this.refresh(v);
  this.registry.events.on('changedata-coins', onChange);
  this.events.once('shutdown', () => {
    this.registry.events.off('changedata-coins', onChange);
  });
}
```

## Removing or replacing a scene

You cannot reuse a scene key until the original is destroyed. To swap an instance
under the same key, remove it after it finishes shutting down:

```js
this.scene.remove('level'); // remove by key
// then later
this.scene.add('level', NewLevelScene, true); // true = autostart
```

A handy alternative to juggling keys is to store the active level key in the
registry and add/remove by that value.
