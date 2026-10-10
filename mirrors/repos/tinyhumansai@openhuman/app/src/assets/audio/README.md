# Audio assets

Short UI chimes for the push-to-talk feature, driven by [`usePttHotkey.ts`](../../hooks/usePttHotkey.ts) and the [`tauri-plugin-ptt`](../../../../packages/tauri-plugin-ptt/README.md) plugin.

| File                               | Purpose                                                     | Source                                                                        | License              |
| ---------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------- |
| [`ptt-open.wav`](./ptt-open.wav)   | Mic opened (PTT key pressed).                               | Generated locally with Python `wave` + sine generator (800 to 1200 Hz sweep). | CC0 / Public Domain. |
| [`ptt-close.wav`](./ptt-close.wav) | Mic closed (PTT key released).                              | Generated locally with Python `wave` + sine generator (1200 to 800 Hz sweep). | CC0 / Public Domain. |
| [`ptt-error.wav`](./ptt-error.wav) | Session aborted (empty audio, mic permission denied, etc.). | Generated locally with Python `wave` + sine generator (250 Hz tone).          | CC0 / Public Domain. |

All clips are 80 to 120 ms long and LUFS-normalized to roughly match the in-app notification sound (about -16 LUFS). Replace freely with better-sounding equivalents. Just keep them under 200ms and CC0/MIT-equivalent.
