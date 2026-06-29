---
name: phaser-core
description: >
  Set up and debug a Phaser 3 game: the Game config, the Scene lifecycle
  (init/preload/create/update), the asset loader, cameras, and cross-scene
  communication. Use when building or debugging a Phaser 3 game — when the user
  mentions Phaser, Phaser.Game, Phaser.Scene, preload/create/update, this.load,
  this.add, or scene transitions. For Arcade Physics movement/collisions use
  phaser-arcade-physics.
license: Apache-2.0
compatibility: Phaser 3.90 (JavaScript/TypeScript, ES modules or script tag)
metadata:
  engine: phaser
  category: web-engines
  difficulty: beginner
---

# Phaser 3 Core

Set up the foundation of a Phaser 3 game: the `Game` config, the `Scene`
lifecycle, asset loading, cameras, and passing data between scenes. Targets
**Phaser 3.90**.

## When to use

- Use when starting a Phaser 3 game, wiring the `Phaser.Game` config, structuring
  `Scene`s, loading assets in `preload`, or fixing scene transitions and shared
  state.
- Use when the project has `phaser` in `package.json` or `import Phaser from 'phaser'`,
  and code uses `preload()`/`create()`/`update()`.

**When *not* to use:** movement, velocity, colliders, gravity, or overlap → use
`phaser-arcade-physics`. Complex rigid-body simulation uses Matter physics (a
separate concern). For cross-engine save/load patterns use `save-systems`.

## Core workflow

1. **Create the game from a config.** `new Phaser.Game(config)` with `type:
   Phaser.AUTO` (WebGL with Canvas fallback), a `width`/`height`, and a `scene`
   array. The first scene (and any with `active: true`) starts automatically.
2. **Model each screen as a `Scene`.** Subclass `Phaser.Scene`, pass a unique
   `key` to `super`, and implement the lifecycle: `init(data)` → `preload()` →
   `create(data)` → `update(time, delta)`.
3. **Load assets in `preload`, use them in `create`.** Queued assets are not
   available until `create`. The loader is per-scene; the cache it fills is global.
4. **Reset per-run state in `init()`, not the constructor.** A scene instance is
   reused across restarts, so constructor-set fields keep stale values.
5. **Move between screens** with `this.scene.start/launch/switch/sleep/wake`.
   Share data through `this.registry` (global) or a sibling scene's event emitter.
6. **Run and observe.** Serve the page, open it, and confirm assets load (watch the
   Network tab and console) and scenes switch as expected before assuming success.

## Patterns

### 1. Game config + boot (ES module)

```js
// main.js — one Game owns the renderer, loop, cache, and Scene Manager.
import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import PlayScene from './scenes/PlayScene.js';

const config = {
  type: Phaser.AUTO,            // WebGL if available, else Canvas
  width: 800,
  height: 600,
  backgroundColor: '#1d1d28',
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, PlayScene] // BootScene starts first
};

new Phaser.Game(config);
```

### 2. A Scene with the full lifecycle

```js
// scenes/PlayScene.js
import Phaser from 'phaser';

export default class PlayScene extends Phaser.Scene {
  constructor() {
    super('play');                  // unique scene key
  }

  init(data) {
    // Reset run-specific state HERE so restarts start clean.
    this.score = 0;
    this.level = data.level ?? 1;
  }

  preload() {
    // Queue downloads. Not usable until create().
    this.load.image('player', 'assets/player.png');
    this.load.spritesheet('coin', 'assets/coin.png', { frameWidth: 16, frameHeight: 16 });
  }

  create() {
    this.player = this.add.sprite(400, 300, 'player');
    this.scoreText = this.add.text(10, 10, 'Score: 0', { fontSize: '20px', color: '#fff' });
    this.cursors = this.input.keyboard.createCursorKeys();
  }

  update(time, delta) {
    // delta is milliseconds since last frame; divide by 1000 for seconds.
    const speed = 200 * (delta / 1000);
    if (this.cursors.left.isDown)  this.player.x -= speed;
    if (this.cursors.right.isDown) this.player.x += speed;
  }
}
```

### 3. Cross-scene data + events

```js
// The registry is a global DataManager shared by every scene.
this.registry.set('coins', 0);                 // in any scene
const coins = this.registry.get('coins');      // read anywhere

// React to registry changes (e.g. a HUD scene listening to gameplay):
this.registry.events.on('changedata-coins', (parent, value) => {
  this.coinText.setText(`Coins: ${value}`);
});

// Talk directly to another running scene via its event emitter:
const ui = this.scene.get('hud');
ui.events.emit('show-message', 'Level cleared!');
```

### 4. Scene transitions (pick the right verb)

```js
this.scene.start('gameover', { score: this.score }); // stop this scene, start target
this.scene.launch('hud');        // run a second scene in parallel (overlay HUD)
this.scene.switch('menu');       // sleep this scene, start/wake target
this.scene.pause();              // freeze updates but keep rendering (modal)
this.scene.sleep();              // stop updating AND rendering, keep state for wake
```

### 5. A camera that follows the player

```js
this.cameras.main.setBounds(0, 0, 1600, 1200);  // world size
this.cameras.main.startFollow(this.player, true, 0.1, 0.1); // smooth lerp follow
this.cameras.main.setZoom(1.5);
```

## Pitfalls

- **Assets are `undefined` in `create`/`update`** → you forgot to queue them in
  `preload`, or used the wrong key. The loader runs between `preload` and `create`.
- **State leaks across a restart** → you set fields in the constructor. The Scene
  instance is reused; reset run state in `init()` and clear arrays on `shutdown`.
- **`this.scene.start` vs `this.scene.launch`** → `start` stops the calling scene;
  `launch` runs the target alongside it. Using `start` for a HUD hides the game.
- **`this` is wrong in a callback** → arrow functions keep the Scene's `this`; plain
  `function` callbacks need a context argument or `.bind(this)`.
- **Phaser 2 tutorials don't work** → "States" were renamed to "Scenes" in Phaser 3,
  and each Scene owns its own systems (input, cameras, tweens) rather than a global
  Game World.
- **Nothing renders / black screen** → confirm the canvas mounted, `width`/`height`
  are set, and a scene actually started (check `game.scene.dump()` output).

## References

- For the full scene state machine (pause/resume vs sleep/wake vs stop/start, the
  restart-state bug, and removing/replacing scenes), read
  `references/scene-flow.md`.

## Related skills

- `phaser-arcade-physics` — velocity, gravity, colliders, overlap, and groups.
- `input-systems` — rebindable, multi-device input architecture (engine-agnostic).
- `pixijs-rendering` / `threejs-scene-setup` — other browser rendering stacks.
- `platformer` / `puzzle` — genre templates that compose Phaser skills.
