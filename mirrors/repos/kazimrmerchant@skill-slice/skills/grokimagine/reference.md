# grokimagine — reference

## CDP / accounts

| Item | Value |
|------|--------|
| User Data | `$env:CHROME_USER_DATA` or `~/Chrome/UserData` |
| CDP | `http://127.0.0.1:9222` |
| Grok Google | the account already signed into that Chrome profile |
| Hub start | `$env:BROWSER_HUB\scripts\start.ps1` |
| Banned | Cursor IDE browser; second `--user-data-dir`; mixing unrelated SSO accounts into the Grok profile |

### Signed-in signals

Good: cookies `sso`, `sso-rw`, `x-userid`; UI shows Search / New Generation / Projects.  
Bad: primary Sign in; only `x-anonuserid`.  
Paywall: `#subscribe`, Upgrade modal → exit 6.

## Product matrix (2026-08-10 live UI)

| Mode | URL | Composer controls | Best for |
|------|-----|-------------------|----------|
| Image | `/imagine` | Speed/Quality; Image Count; Aspect | Locks / refs only |
| **Video** | `/imagine` (often default) | 480p/720p/1080p; 6s/10s/15s; Video audio; Upload; Aspect | **Engaging clips** (T2V or I2V) |
| Agent start | `/imagine` → New Generation → Agent | Agent + Short Film | Brand-new multi-panel film only |
| Agent continue | `/imagine/agent/{uuid}?conversation=` | Nudge on existing canvas | Extra beats; **character lock** |
| Post | `/imagine/post/{uuid}` | Make video · Extend · Upscale · Regenerate · Download · Expand · HD | Improve / animate a result |

Deep guide: [`VIDEO.md`](VIDEO.md)

**Ship video defaults:** 1080p · 10s (15s heroes) · I2V when possible · `GROK_VIDEO_AUDIO=0` if Remotion VO.

**API (ask first):** `grok-imagine-image-quality`, `grok-imagine-video-1.5` — prepaid.

## Env vars

`GROK_CDP`, `GROK_OUT`, `GROK_PROMPT`, `GROK_COUNT`, `GROK_BRIEF`, `GROK_BRIEF_MAX`, `GROK_KEYWORDS`, `GROK_EXPECT_PANELS`, `GROK_ORDER`, `GROK_FINAL`, `GROK_WAIT_MS`, `GROK_NUDGE`, `GROK_NUDGE_FILE`, `GROK_AGENT_URL`, `GROK_ALLOW_HOME_VIDEO`, `GROK_IMAGE`, `GROK_VIDEO_RES`, `GROK_VIDEO_DUR`, `GROK_VIDEO_AUDIO`, `GROK_FIRE_ONLY`, `GROK_CLOSE_TAB`

## Selectors (Aug 2026 — fragile, re-probe if broken)

```
[aria-label="Generation mode"]          // radiogroup
[role="radio"][aria-label="Image"]
[role="radio"][aria-label="Video"]
[role="radio"][aria-label="Agent"]
button[aria-label="Submit"]             // primary send
button[aria-label="Upload"]             // I2V attach
[aria-label="New Generation"]
[aria-label="Aspect Ratio"]
[aria-label="Image Count"]
[aria-label="Video resolution"]         // 480p|720p|1080p radios inside
[aria-label="Video duration"]           // 6s|10s|15s
[aria-label="Image generation speed"]   // Speed|Quality
[role="textbox"][aria-label*="Ask Grok"]
.tiptap.ProseMirror
```

**Anti-pattern:** `button:has-text("Image")` / text-only clicks — unselected mode radios have empty text; sidebar project titles can steal `has-text`.

Use `scripts/ui-mode.mjs` instead of re-implementing.

## Detection / export

- Stills: Generated alt OR display ≥180; nw/nh ≥512; `data:` or host GET
- Video URL: `https://assets.grok.com/users/{uid}/generated/{uuid}/generated_video.mp4`
- Dedupe UUID; download even if videoWidth/duration 0
- Concat list UTF-8 **without BOM**
- Never trust DOM order — QC `frames/`
- Agent wait: require `newUuidsSinceStart > 0` on current agent URL

## Scripts

| Script | Role |
|--------|------|
| `ui-mode.mjs` | Shared mode/aspect/submit/tab/audio/upload helpers |
| `check-and-generate.mjs` | status / generate (Image) |
| `generate-stills-clean.mjs` | Image stills (locks) |
| `generate-video.mjs` | **Video T2V or I2V** (preferred for engagement) |
| `agent-short-film.mjs` | start (new film only) \| wait \| nudge \| status |
| `agent-continue.mjs` | **Continue existing Agent conversation** (character lock) |
| `export-agent-film.mjs` | scroll + UUID download + frames |
| `download-agent-media.mjs` | media helper |
| `stitch-story-order.mjs` | GROK_ORDER → FINAL |
| `_dedupe-tabs.mjs` | Keep one Imagine tab |
| `probe-imagine-modes.mjs` | Mode map |
| `probe-imagine-video.mjs` | Video composer probe |
| `probe-imagine-video-history.mjs` | Post page / Make video / Extend probe |
| `probe-imagine-ui*.mjs` / `probe-submit-btn.mjs` | Debug probes |
| `start-chrome.ps1` | delegates to browser-hub |
| `VIDEO.md` | Video workflow contract |

## Official docs

- https://docs.x.ai/developers/model-capabilities/imagine
- https://docs.x.ai/developers/model-capabilities/video/generation
- https://x.ai/news/grok-imagine-video-1-5
- https://x.ai/news/grok-imagine-video-1-5-references
