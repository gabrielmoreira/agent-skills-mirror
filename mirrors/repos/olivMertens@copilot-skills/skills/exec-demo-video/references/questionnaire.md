# Initial questionnaire (ask BEFORE generating anything)

Ask these in one or a few grouped prompts, in order, to avoid round-trips. Do not
assume defaults for language/voice — that is the whole point of asking first.
Every answer maps to a concrete Remotion/audio setting — see the preset table at
the bottom and `app-demo-video/references/animation-and-sound.md`.

1. **Voice language** — French, English (UK/US), or a multilingual pair?
2. **Voice** — propose 2–3 options for the chosen language (see
   `voice-catalog.md`) with a recommendation. Offer to generate 2–3 short audio
   samples (with a tricky articulation word) before committing, unless the user
   says to skip.
3. **Audience** — C-level execs, sellers, end customers, general public? (drives
   tone and jargon level)
4. **Tone** — measured corporate, dynamic/energetic corporate, casual?
5. **Target duration** — e.g. 30s, 45s, 60s+ (drives scene count).
6. **Demo link** — the app URL to capture (+ credentials if needed).
7. **GitHub repo** — to understand real features and avoid inventing
   screenshots/numbers.
8. **Optional persona** — e.g. "a field agent who receives this exact case".
   Use a generic role name; never a real third-party/competitor brand as a
   persona without explicit confirmation.
9. **Priority "wow" element** — an interactive map, a real-time score, etc. that
   should get the most screen time.
10. **Background music** — will the user provide a track (get the file path), or
    pick a mood to source (corporate/ambient/energetic), or none? Reminder: never
    ship copyrighted audio; the user supplies `public/bgm.mp3`. Music stays ducked
    under the voice; ask if they want it at all.
11. **Animation & zoom intensity** — subtle, moderate (default), or dynamic?
    (drives Ken-Burns zoom strength, entrance snappiness, music flare). Also ask:
    should on-screen numbers count up (`useCountUp`), should a highlight ring
    point at a specific figure (`SpotlightRing`), and does any screen have real
    compute time to stage with a processing bar (`LoadingBar`)?
12. **On-screen emphasis (optional)** — any exact figure/label the narration will
    call out that should be spotlighted or badged (e.g. a "+10%" corner badge on
    the relevant screenshot).
13. **Burned-in captions/subtitles (optional)** — does the user want on-screen
    captions (for silent/social viewing or accessibility)? If yes, **ask the
    caption language** — it is independent of the voice, so you can narrate in
    French and caption in English (or vice versa) for international social feeds.
    Captions render as one short line per scene via the `caption` prop.

Recommended defaults when the user is unsure: **standard exec profile** ≈ 6–7
scenes / 45–55s, dynamic corporate tone, moderate animation, ducked corporate
music.

## Map answers → settings (contextualize the build)
Use the answers above to set concrete knobs before building scenes. Full detail
and code references in `app-demo-video/references/animation-and-sound.md`.

| Answer | Effect on the video |
| --- | --- |
| Tone = measured | subtle preset: `useKenBurns` to ~1.03, entrance calm, `BGM_FLARE` ~0.07, minimal spotlights |
| Tone = dynamic (default) | moderate preset: Ken-Burns ~1.045, staggered entrance, `BGM_FLARE` ~0.09, spotlight the key number |
| Tone = energetic | dynamic preset: Ken-Burns ~1.07, snappier entrance, `BGM_FLARE` ~0.11, count-ups + spotlights on KPIs |
| Audience = C-level | fewer words, bigger headlines, name concrete Azure services in pills |
| Audience = end users / general | plainer language, more literal screen tours, lighter jargon |
| Music = none | remove the `<Audio bgm>` from the assembly; keep narration only |
| Music = provided/mood | keep the ducked envelope; match `BGM_BASE`/`BGM_FLARE` to intensity |
| Wow element named | give it its own scene, more screen time, and a spotlight/badge |
| Real compute step | stage it with `LoadingBar` synced to narration, not a cut to the result |
| Captions = yes | pass a short `caption` per scene; caption language may differ from the voice |
