# Mayz / Seedance 2.0 world-route FPV case note

Source pattern: an X thread by @Mayz1169 about Seedance 2.0 path control, using a Lord-of-the-Rings-style aerial terrain map with one red route line to generate a 15-second cinematic FPV flight.

## What the post demonstrates

The reusable trick is different from close-range character-stop FPV:

1. Create a top-down or high aerial world map / terrain route image.
2. Draw one clear red line showing the entire camera path and direction.
3. Feed the map into Seedance 2.0 as a route-planning control image.
4. In the video prompt, tell the model the red line is only the intended flight route and must be completely removed from the final video.
5. Convert the route into a timed world progression: peaceful zone → transition zone → city/fortress → hostile zone → destination reveal.
6. Use camera-language constraints: invisible first-person drone, no map view, no cuts, no teleporting, strict route geometry, natural banking, altitude changes, progressive acceleration, foreground parallax.
7. Use environment progression as the story engine, not character dialogue.

## When to use this mode

Use red-line path control when the scene is large-scale and route-shaped:

- fantasy continent journey
- game trailer / open-world flythrough
- city-to-landmark FPV
- map-to-world transformation
- racing path / canyon flight / aerial drone route
- theme-park ride style journey
- product/world showcase with clear geography

Do not use this as the default for indoor scenes, close character interactions, or crowded social scenes. For those, numbered stop markers are usually safer because red route lines can cross people/furniture or leak into the output.

## Prompt ingredients that matter

### Route image prompt

Ask for:

- high-resolution 16:9 aerial terrain map or world map
- clear start and destination regions
- one continuous red route line, optionally with a subtle arrow
- route drawn through physically plausible corridors: roads, valleys, rivers, city gates, bridges, canyons, coastlines, rooftops, airspace
- distinct visual zones along the path so the video has progression

### Video prompt pattern

```text
Use the uploaded image as a route-planning terrain map. The red line indicates the intended camera flight path and direction only. The red line, arrow, and all annotations must be completely removed from the final video.

Create a [duration]-second single continuous [aspect ratio] cinematic FPV flight through the exact world shown in the image. No cuts, no transitions, no teleporting, no map view. The camera is an invisible first-person drone camera and must strictly follow the drawn route geometry from [start] to [destination].

Timeline:
0-[t1]s: [zone 1, low close passes, parallax]
[t1]-[t2]s: [zone 2, route-following transition]
[t2]-[t3]s: [major landmark / city / obstacle]
[t3]-[t4]s: [dramatic terrain change]
[t4]-[end]s: [destination reveal / climb / final scale shot]

Camera motion: fast cinematic FPV, continuous forward flight, natural banking, close passes, dynamic altitude changes, strong foreground parallax, progressive acceleration, smooth horizon control.

Avoid: visible red line, visible arrows, annotations, text, subtitles, logos, watermarks, map appearance, jump cuts, teleportation, reverse movement, visible drone, guide characters, modern/sci-fi objects unless requested, blurry terrain, deformed buildings, flickering structures, flat environments.
```

## New gameplay patterns enabled by this case

1. World-transition ride
   - The route itself is the story: safe village → capital city → ruins → volcano / boss arena.
   - Best for trailers, lore intros, game-world showcases.

2. Mission-route briefing becomes gameplay footage
   - First image looks like a tactical map, final video becomes the actual FPV route.
   - Good for spy infiltration, fantasy quest, heist, battlefield flythrough.

3. Biome progression
   - Each route segment changes weather, lighting, architecture, and danger level.
   - Useful for showing model control over long visual transitions.

4. Landmark chain
   - The route links 4-6 large landmarks rather than 4-6 people.
   - Works better with drone/bird/spirit POV than human walking POV.

5. Map-to-world transformation
   - The control image can be a stylized map, but the prompt must say final output is not a map view; it becomes real cinematic terrain.

6. Speed-run / race-line mode
   - Use the red path as a racing line through canyon, city rooftops, tunnel, bridge, forest, or sci-fi trench.
   - Add speed cues, banking, near misses, motion blur, and checkpoint reveals.

7. Theme-park dark ride
   - A continuous guided ride through a designed world: entrance → story zones → threat reveal → finale.
   - Better if the route has curves, gates, tunnels, and reveal moments.

## Practical boundary

This case weakens the old rule “avoid red lines by default” only for world-scale route control. Keep both modes:

- Numbered stops: close interaction, characters, indoor scenes, social scenes, exact target count.
- Red-line path control: large terrain, aerial route, long-distance journey, continuous geography, environment progression.

If the user asks for Seedance 2.0 path control, drawn route, game-map flight, or world traversal, choose red-line path mode by default.
