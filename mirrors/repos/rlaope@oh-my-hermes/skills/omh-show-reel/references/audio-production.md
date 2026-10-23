# Local score, cue-aligned SFX, stems and honest audio gates

Choose muted/music-only/narration/narration+bed/SFX from the brief, not from the
conversation language. No default voice, provider, STT, download or paid call.
The opt-in `eleven.py`/`narrate.py` (narration, SFX, music, STT) and
`codex_ref_image.sh` run only when the user asks for them with their own
`ELEVENLABS_API_KEY` or signed-in codex; they refuse without it, and the film
falls back to local music and on-screen text.
Audio comes before scenes: music beats and narration words set the picture's
times. Craft depth (voices, music plans, SFX design, mix targets) is in
`references/craft-audio.md`. `music_tools.py analyze` reads tempo, downbeats and
hits from the chosen track; `timeline.py script.json --music-analysis` turns them
into `barN`/`music.hitN` cues and `reel/timeline.js` for `REEL.cue`/`bar`/`level`.
Read `toolkit/README.md` and `scripts/synth_music.py`, `mix.py`, `qa_check.py`
relative to that toolkit. The local seeded score is a modest fallback: section
notes/energy/BPM and tick/boom/whoosh events are parameters, not a musical-quality
promise. Licensed imported local music is equally valid; record its rights/hash.

Timeline cues are explicit IDs with seconds/frame indices or acyclic after+offset,
or script.json scenes/SFX placed on music and narration cues. A narration cue comes
from the provider's character alignment of the approved tts text; never derive a
screen event by guessing where a substring is spoken without that alignment. Audio events use numeric `at` or an exact cue ID and start/peak/end anchor.
Measure the PCM event anchor and A/V cue against decoded frames, not a guessed
hearing result. Unknown cues, missing required tracks, corrupt or wrong-rate audio
must fail closed before a usable final mix. Muted cannot silently discard tracks.

Mix uses explicit stereo 16-bit PCM WAV in one declared sample rate; host decode/
resample is a separate observed action. Retain narration/bed/SFX stems, authored
gain automation, speech-aware bed ducking and recovery outside speech. Compare
speech/non-speech intervals numerically, then listen to the actual final encoded
mix if that capability is observed. A sample limiter is not true-peak certification.
`--ffmpeg` on mix measures loudness, not normalization; master explicitly and
measure post-AAC LUFS/true peak with the chosen policy. No parse/decode/tool failure
becomes zero or a PASS. Silent/nonfinite required-audio metrics are HOLD.

Keep synthesis, mastering, final-AAC measurements, STT, pronunciation review and
listening as different observations. STT only when speech exists and separately
approved tooling is available; it never proves naturalness, consent or listening.
A musical accent must support the shot/cut, not mask every change with a boom.
