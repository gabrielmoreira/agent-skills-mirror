# Geometry

All geometry is built once in Node by the build script. The browser only moves groups, toggles their visibility and rebuilds a few paths.

## World units and axes

- x runs left to right along the bench, y runs from back to the viewer, z runs up.
- One world unit is one unit of the design, not one pixel. The reference bench plate is 398 by 292 units. The starter bench is 144 by 68.
- Keep the bench top at z = 0. Stations stand on it. The plate and its feet go below zero.

## Camera

```js
const P = k.fitProjection(points, W, H, { pad: 26, azimuth: 60 });
```

- Elevation is 30 degrees, the kit default. Do not change it per part.
- The azimuth sets which faces show. At 60 degrees, faces toward +y carry 0.87 of the view and faces toward +x carry 0.5. Put working faces and nameplates on +y faces.
- `points` must include the plate corners and the highest points of the exploded pose. If you leave out the exploded pose, exploded parts leave the stage.
- The reference page uses a 960 by 640 viewBox. The starter uses 720 by 440.

## Parts list

Write the list before any code. One row per part:

| id | assembly | plan (x, y, w, d) | z0 to z1 | tone | moves |
|---|---|---|---|---|---|
| `cache` | cache | -26, -30, 20, 18 | 0 to 10 | mid | no |
| `probe` | cache | -19, -3, 6, 6 | 18 to 25 | hi | z, -2.5 on lookup |
| `bin0` | cache | -21, -27, 10, 0.8 | 10 to 17 | hi | shown when stored |

The assembly decides the explode vector and the nameplate that lights with the part.

## Kit functions you will use

From `kit/iso-kit.mjs`:

| Function | Makes |
|---|---|
| `fitProjection(points, W, H, opts)` | The projection `P` |
| `iso(p, P)`, `depthOf(p, P)` | Screen point and depth of a world point |
| `slabOf(plan, z, h, P, steps, bevel)` | A rounded box. `plan` is `{ x, y, w, d, r }` |
| `cylinder(cx, cy, r, z, h, P, steps)` | An upright cylinder |
| `extrude(ring, z, h, P, opts)` | Any plan polygon pushed up |
| `solidSvg(paths, { tone, crease, lit, inner })` | Fill, four shade bands, top, crease and outline |
| `lineSvg(d, { tone, free, dotted, dashed })` | A line with a tone |
| `lineOnTop(a, b, z, P)`, `segment(a, b, P)`, `ring(cx, cy, r, z, P)` | Line paths on a top face or in space |
| `radialTicks`, `topTicks`, `knurl`, `sideSeam`, `dotGrid` | Dial ticks, ruler ticks, grip texture, seams, perforation |
| `topMatrix(at, z, P)`, `sideMatrix(at, z, P, face)`, `faceTextSvg(m, text, opts)` | Text engraved on a face |
| `haloOf(plan, z, h, P)` | A soft shadow under a station |
| `translateAlong(P, [dx, dy, dz])` | The SVG `translate` for a world offset |
| `figureSvg`, `plateHtml`, `ISO_CSS` | The SVG root, the corner plate frame and the base styles |

From `kit/lathe.mjs`: `frameAlong`, `disc`, `ribsOf`, `dotsOf`, `circleOf`, `spokesOf` and `viewOf` build drums, rollers, rods and ports on any axis. From `kit/tube.mjs`: `tubePieces` and `tubeSvg` build bent pipes that split into depth-sorted pieces.

## Shading and tones

- `solidSvg` paints a paper fill, up to four shade bands, a lit top, a crease and an outline.
- An extruded side face gets band `floor(4 * (n . l + 1) / 2)`. Here `n` is the face normal in plan and `l` is `(-sin A, cos A)`.
- Lathe bodies use a raised light and band limits of 0, 0.2, 0.42 and 0.62.
- Outline tones are `hi`, `mid`, `lo` and `faint`. Use `hi` for moving and important parts, `mid` for station bodies, `lo` for bases and recesses, `faint` for seams.
- Grey tokens come from CSS variables, so both themes work. The course light theme uses `--anatomy-shade-0` `#dcdace` to `--anatomy-shade-3` `#f5f3ea`. The dark theme uses `#0b0e1b` to `#14192e`.
- The accent is `--anatomy-lit`. The course uses `#3553ff` in light and `#6b8eff` in dark. Nothing else on the stage uses a hue.

## Items and depth keys

Each part becomes one item: `{ id, asm, key, svg }`. The key is the depth of a reference point plus a bias.

```js
const depth = (p) => k.depthOf(p, P);   // (x cosA + y sinA) cosE + z sinE
put("probe", "cache", [-16, 0, 20], svg, 6);
```

- Pick the reference point at the visible centre of the part.
- Larger keys paint later, so they appear in front.
- Give the base plate a bias of about -1000 and the track about -500, so they always paint first.
- A part that rests on top of another part needs a positive bias. In the starter, a card on the cache top had a smaller key than the cache body. It stayed hidden until it got a bias of 3.
- A head that hangs over a carriage gets a bias of 6 to 20, so it paints over the cards below it.

## Nameplates

Every station gets an engraved plate with its concept word in capitals.

```js
const w = text.length * size * 0.62 + size * 1.8;   // plate width
const baseline = (z0 + z1) / 2 - size * 0.36;       // text on a vertical face
```

- Put plates where no mover passes in front of them. In the starter, plates on station faces were hidden each time the carriage parked. Plates on the bench top in front of the track fixed it.
- Use 4.4 to 7 world units of text on a hero bench. Check the size in the phone screenshot.
- Plates do not move when the machine explodes. They stay on the bench as a key to the parts.
- Each plate is an item with id `tag-<assembly>`, so it lights with its station.

## Lines

- Every line ends on a solid, on another line or on a hub.
- A pointer that starts on a hub and ends in free space carries `data-free="end"`. A pointer drawn from its tip uses `data-free="start"`.
- Rods between a fixed arm and a moving head are lines that the live script rebuilds each frame. Both ends sit on solids at every pose.

## Explode

Give each assembly one offset vector in world units. The reference vectors run from `[0, 6, 44]` for the controller to `[-50, -14, 16]` for the memory drum. Base, track and core stay at zero. Parts hidden inside a housing, such as a drum, fade in as the housing lifts.
