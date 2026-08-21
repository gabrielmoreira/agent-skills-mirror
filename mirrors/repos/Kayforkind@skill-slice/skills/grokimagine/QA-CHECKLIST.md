# grokimagine — QA checklist

Watch full clip at 1x, then 0.5x for morphing. Read stills with vision.

## Auto-reject

- Identity drift mid-clip or vs hero_lock
- Melting hands/face, plastic AI-slop hero
- Gibberish / fake readable text on plates or screens
- AI-invented website UI sold as live demo
- Wrong mode (Image still claimed as film; sidebar history as “new film”)
- Submitted stills while Generation mode was still **Video** (timeout / wrong media)
- Ken Burns / Image-only picture track when the brief asked for **engaging Video**
- Serial wait-for-MP4 before firing the next Video clip (use parallel fire + harvest)
- Paywall / unsigned session “success”
- DOM-order concat without frame QC
- Hotlink-only (no durable file under pack)
- Extra Imagine tabs opened for one job
- Extra beats on a character series fired via home Video / New Generation (new project → face drift)
- Agent URL without `?conversation=` treated as “this film” (workspace UUID can be reused)

## Avatar accept

- Matches approved hero_lock wardrobe + face
- Mic / formal clothes consistent
- Dialogue: quoted line audible; lips roughly track (re-roll if mush)
- No TMNT IP costumes / logos
- 9:16 framing for Shorts PiP or MCU

## Export accept

- Unique UUID MP4s on disk under `GROK_OUT`
- Frames extracted; story order logged
- Concat without BOM; FINAL plays
- Session keywords match this job (not prior film)

## Technical

- Aspect matches brief (9:16 Shorts / 16:9 long)
- SuperHeavy path preferred; API only if user approved
- GenAI disclosure when shipping AI host
