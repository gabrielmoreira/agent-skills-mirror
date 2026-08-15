# grokimagine — examples

## Image — lock still only (not the final picture track)

```
Photoreal Spider-Man classic red blue suit white lenses, FULL BODY crouch on Manhattan
rooftop golden hour, city canyon below, cinematic 16:9, ultra detailed fabric, no text
no logos no watermarks.
```

## Video I2V — engaging action B-roll (preferred)

Still = full-body lock. Motion prompt only (one action + one camera):

```
Preserve the Spider-Man suit from the reference. He leaps forward off the rooftop edge;
dust kicks up; fabric and capelets catch wind. Camera tracking beside him, continuous
move, golden rim light, photoreal, no text, no logos.
```

Settings: Video · 1080p · 10s · audio off if Remotion VO · Upload lock.

## Video T2V — when no lock yet

```
Photoreal Spider-Man classic red blue suit white lenses web-swings through a street
canyon at golden hour. One continuous side-tracking camera. Fabric motion, motion blur
on background, no text no logos.
```

## Video I2V — dialogue micro-beat (host)

Still = approved hero_lock. Prompt motion + quote only:

```
Same woman as the reference image, medium close-up, locked tripod. She leans in slightly
and says in a clear confident tone, "Four GitHub URL hacks most developers never try."
Small studio room tone, soft HVAC hum. Natural mouth motion matching the line. No on-screen text.
```

## Video I2V — bridge line

```
Same woman, medium close-up, subtle nod. She says brightly, "Watch the address bar — this
one opens VS Code in your browser." Soft studio ambience. No captions burned in.
```

## Agent Short Film brief (when multi-panel needed)

Keep under `GROK_BRIEF_MAX` if TipTap chokes; set `GROK_KEYWORDS`.

```
SHORT FILM — vertical 9:16 tech news host. One consistent redhead woman in navy blazer
with handheld mic. No cartoons. No readable fake UI text. Panels: (1) hook to camera
(2–7) she points toward off-screen browser while speaking short English lines about
GitHub URL swaps (8) CTA smile. Animate panel-by-panel. Character consistency critical.
```

## Agent continue — extra beats on an existing project

Do **not** fire home Video I2V. Nudge the same conversation:

```
Stay in THIS same Imagine Agent project / conversation. Do NOT start a New Generation.
Keep [Lily] and [Daisy] exactly as already in this canvas.
Generate TWO new 10s 16:9 clips with native audio ON. Lily says exactly: "…"
```

Env: `GROK_AGENT_URL` (must include `?conversation=`), `GROK_NUDGE_FILE`, `GROK_EXPECT_PANELS=2`, `node agent-continue.mjs`.

## Anti-patterns

| Bad | Why |
|-----|-----|
| Image stills + Ken Burns sold as “video” | Not engaging; use Video I2V |
| Macro chest lock → I2V | More macros; use full-body seed |
| “Make a cool GitHub tutorial video” | No shot grammar; Agent wanders |
| Asking Grok to render github.com UI with labels | Fake/melted text |
| Stacking 3 camera moves in one clip | Morphing |
| Implied speech without quotes | Lip sync mush |
| Animating all Agent panels at once | Jumbled stitch |
| Home Video I2V for extra beats on an Agent film | New project; faces drift |
