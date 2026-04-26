# Layered Map Contract

## Layer Types

Use these layers for hand-painted or generated 2D RPG scenes:

1. `base`: one raster image containing only terrain and ground-level details.
2. `props`: transparent sprites anchored in map coordinates.
3. `actors`: player, NPCs, monsters, pickups, and moving objects.
4. `foreground`: optional transparent sprites that must cover actors.
5. `collision`: structured metadata, not pixels.
6. `zones`: structured metadata for encounters, rest, triggers, exits, and dialogue.
7. `preview`: flattened QA artifact only.

## Base Map Prompt Pattern

Use this shape when generating a base map:

```text
Create a ground-only top-down 2D pixel-art RPG map.
This is a BASE GROUND MAP ONLY.
Include terrain, paths, grass, water, cliffs, ground markings, and flat anchor pads.
Do not include tall collidable objects: no buildings, gates, fences, lanterns, trees, signs, barrels, NPCs, monsters, UI, or text.
Leave clear empty spaces where props will be placed later.
Make walkable paths and zone boundaries easy to trace.
```

## Prop Prompt Pattern

Use `$generate2dsprite` for each prop when the map strategy needs separate transparent objects. Keep prompts direct:

```text
Create a single <prop> prop for a top-down 2D pixel-art RPG map.
3/4 view from slightly above, full object visible, centered, crisp dark pixel outlines.
Background must be 100% solid flat #FF00FF magenta, no gradients, no texture, no shadows, no floor plane.
No text, labels, UI, or watermark.
Entire prop must fit fully inside the image with generous magenta margin on all sides; no part may touch or cross the image edge.
```

Recommended processing:

```bash
python /path/to/generate2dsprite.py process \
  --input <raw.png> \
  --target asset \
  --mode single \
  --rows 1 \
  --cols 1 \
  --cell-size 256 \
  --output-dir assets/props/<prop> \
  --fit-scale 0.9 \
  --align feet \
  --component-mode largest \
  --component-padding 8 \
  --min-component-area 200 \
  --threshold 100 \
  --edge-threshold 150 \
  --edge-clean-depth 2
```

Use a larger `--cell-size` for buildings or large gates.

## Prop Metadata

Use explicit map-space dimensions:

```js
const MAP_PROPS = [
  {
    id: "torii",
    imageKey: "propTorii",
    x: 836,
    y: 850,
    w: 380,
    h: 306,
    sortY: 850
  }
];
```

Anchor conventions:

- `x`: center of the prop's base/feet.
- `y`: bottom of the prop in map coordinates.
- `w`, `h`: rendered size in map units.
- `sortY`: y-depth used for render ordering. Use the base y for normal props. Use a lower or higher value intentionally for special foreground behavior.

## Render Order

Recommended order:

```text
base map
ground effects / zone glimmers
renderables sorted by sortY:
  props
  player
  NPCs
  monsters
foreground overlays, only when needed
debug collision
HUD/UI
```

If an NPC must always appear above the player, draw that NPC after the y-sorted pass or set a high `sortY`.

## Collision Metadata

Keep collision readable and hand-editable:

```json
{
  "mapSize": { "width": 1672, "height": 941 },
  "spawn": { "x": 836, "y": 782 },
  "npc": { "x": 836, "y": 390, "collisionRadius": 32, "interactRadius": 112 },
  "rest": { "x": 760, "y": 548, "radius": 122 },
  "zones": {
    "grass": { "x": 180, "y": 306, "w": 382, "h": 302 },
    "training": { "x": 1120, "y": 324, "w": 382, "h": 282 }
  },
  "walkBounds": [
    { "id": "main-courtyard", "type": "ellipse", "x": 838, "y": 548, "rx": 604, "ry": 304 }
  ],
  "blockers": [
    { "id": "torii-left-pillar", "type": "rect", "x": 704, "y": 668, "w": 52, "h": 176 }
  ]
}
```

Guidelines:

- Use blockers for prop bases, not full sprite silhouettes.
- Keep entrances open by testing path centers.
- Use ellipses for lanterns, rocks, trees, and basins.
- Use rectangles for fences, walls, buildings, gates, bridges, and posts.
- Use polygons only when rects/ellipses produce poor walkability.

## QA Checklist

Run or simulate checks:

- Spawn point is walkable.
- Main path centers are walkable.
- Gate centers are walkable if the player should pass through.
- Gate pillars block.
- Fences block but entrances remain open.
- Interactables block at their base but can be approached.
- Encounter/rest zones are reachable.
- Actors sort correctly when walking in front of and behind tall props.
- The flattened preview matches the in-game layered render closely enough for visual review.

## Anti-Patterns

Avoid:

- Cutting props out of a fully baked generated map.
- Using a complete flattened map as the only source when collision/occlusion matters.
- Baking text, signs, UI, NPCs, or monsters into the base.
- Letting prop sprites touch image edges.
- Treating transparent PNG bounding boxes as collision automatically.
- Updating art without updating collision and critical point tests.
