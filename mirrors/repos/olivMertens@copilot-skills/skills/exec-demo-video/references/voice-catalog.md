# Voice catalog (Azure Speech)

Voices below are Azure Neural / HD voices. Availability depends on your Speech
resource and region — confirm before committing. Always offer to generate 2–3
short samples first.

## One multilingual voice, several languages (recommended for FR+EN pairs)
A single **multilingual** voice keeps a consistent identity across languages. Set
each clip's spoken language and let `scripts/generate_tts.py` wrap non-base-locale
text in SSML `<lang xml:lang='xx-XX'>` automatically.

- `en-GB-OllieMultilingualNeural` — British male, speaks French cleanly too.
- `en-US-AvaMultilingualNeural` — US, professional/dynamic; strong French prosody.
- `en-US-AndrewMultilingualNeural` — US male, warm.

## Native single-language options
French:
- `fr-FR-VivienneMultilingualNeural` / `fr-FR-Vivienne:DragonHDLatestNeural` — female, measured/corporate.
- `fr-FR-RemyMultilingualNeural` — male.
- `fr-FR-Marc:MAI-Voice-2`, `fr-FR-Soleil:MAI-Voice-2` — HD voices (energetic styles available) where enabled.

English:
- `en-US-Ava:DragonHDLatestNeural` / `en-US-Andrew:DragonHDLatestNeural` — HD, corporate.
- `en-GB-RyanNeural`, `en-GB-SoniaNeural` — British.

## Prosody / articulation tips
- Pass `--rate` (e.g. `-5%`, `0%`, `+5%`) to `generate_tts.py` for pacing.
- Test a "trap" word (a product name, an acronym, a number read aloud) in the
  sample before committing to a voice.
- Spell tricky numbers/percentages as words in the narration text when a voice
  mis-reads them (e.g. "dix pour cent" rather than "10 %").
