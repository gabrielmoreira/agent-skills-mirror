---
name: auto-subtitle-generator-online
version: "1.0.2"
displayName: "Auto Subtitle Generator Online — Instant Captions for Any Video"
description: >
  The auto-subtitle-generator-online skill transcribes and embeds accurate subtitles into your videos using AI-powered speech recognition. Upload your footage, choose your language and caption style, and receive a fully subtitled video or downloadable SRT/VTT file in minutes. Built for content creators, educators, marketers, and accessibility advocates who need reliable captions without manual transcription. Key features include speaker-aware timing, punctuation correction, multi-language support, and customizable font styles. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> Welcome! I'm here to automatically generate accurate subtitles for your videos using the auto subtitle generator online — just share your video file or a link, tell me your preferred language and caption style, and I'll have your subtitled video or SRT file ready in minutes. Ready to caption your first video?

**Try saying:**
- "Generate English subtitles for this MP4 interview and give me an SRT file I can upload to YouTube."
- "Create burned-in captions for my MOV tutorial video with white bold text and a semi-transparent black background."
- "Transcribe this Spanish webinar in WebM format and produce bilingual subtitles in both Spanish and English."

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Turn Any Spoken Word Into On-Screen Text Instantly

The auto-subtitle-generator-online skill exists to solve one of the most time-consuming parts of video production: getting accurate, well-timed captions onto your footage without spending hours in a subtitle editor. Whether you're publishing a YouTube tutorial, a corporate training module, or a social media reel, readable subtitles dramatically increase watch time and accessibility compliance.

This skill operates through a conversational editing model, meaning you don't fill out forms or wrestle with timelines. Instead, you describe what you need — the language, caption placement, style preferences, or whether you want a burned-in subtitle track or a separate SRT file — and the skill handles the rest. You can refine results by simply telling it what to adjust, just like messaging a colleague.

Behind the scenes, the OpenClaw agent orchestrates a pipeline that sends your video's audio through a high-accuracy speech-to-text engine, aligns transcript segments to precise timestamps, applies formatting rules, and packages the output in your chosen format. The agent also handles edge cases like overlapping speech, background noise, and fast-paced dialogue to keep captions readable and synchronized.

### Environment Variables

| Variable | Required | Default |
|----------|----------|--------|
| `NEMO_TOKEN` | No | Auto-generated (100 free credits, expires in 7 days, revocable via Settings → API Tokens) |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` (UUID only, no secrets) |
| `SKILL_SOURCE` | No | Auto-detected from install path, fallback `unknown` |

If `NEMO_TOKEN` is not set, get one (requires `X-Client-Id` header):
```bash
# Generate or read persisted Client-Id
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
# → {"code":0,"data":{"token":"nmv_usr_xxx","credits":100,...}}
```
Save `token` as `NEMO_TOKEN`, `CLIENT_ID` as `NEMO_CLIENT_ID`. Anonymous: 1 token per client per 7 days; token expires in 7 days and can be revoked at any time via **Settings → API Tokens** on nemovideo.com. If your token expires, request a new one with the same `X-Client-Id`.

**Local persistence:** This skill writes `~/.config/nemovideo/client_id` to persist the Client-Id across sessions. This avoids generating a new ID on every request, which would hit the per-IP rate limit quickly (default 10 tokens per 7 days per IP). The file contains only a UUID — no credentials are stored locally.

## 2. Endpoint Directory & Routing Logic

Every caption-related request maps to a specific route — consult the table below to match each action to its correct endpoint and method.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## 3. Operational Flows for Subtitle Generation

$API = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, $TOKEN = `${NEMO_TOKEN}`, $WEB = `${NEMO_WEB_URL:-https://nemovideo.com}`.

Skill attribution variables — do NOT hardcode:
- `$SKILL_NAME` = this file's YAML frontmatter `name`
- `$SKILL_VERSION` = this file's YAML frontmatter `version`
- `$SKILL_SOURCE` = detect at runtime using the first match:
  1. Env `SKILL_SOURCE` if set
  2. If this file's path contains a known platform directory (e.g. `~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`)
  3. Fallback: `unknown`

**CRITICAL**: ALL API requests (including render/export/upload/state/credits) MUST include these headers. Missing them will cause export to fail with 402.
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Initializing a Caption Session
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"project","language":"<lang>"}'
# → {"code":0,"data":{"task_id":"...","session_id":"..."}}
```
Before any transcript or timing data can be exchanged, a session must be established — this handshake creates the persistent context the backend uses to track your caption job. Without it, no downstream calls will resolve correctly.

**Open in browser**: After creating a session, give the user a link to view/edit the task in NemoVideo:
`$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Streaming Messages Over SSE
```bash
curl -s -X POST "https://mega-api-prod.nemovideo.ai/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
All real-time caption events — including SRT chunk delivery, timing confirmations, and status updates — travel through a Server-Sent Events channel tied to the active session.

#### SSE Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Wait silently, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

Typical durations: text 5-15s, video generation 100-300s, editing 10-30s.

**Timeout**: 10 min heartbeats-only → assume timeout. **Never re-send** during generation (duplicates + double-charge).

Ignore trailing "I encountered a temporary issue" if prior responses were normal.

#### Silent Response Fallback (CRITICAL)

Roughly 30% of subtitle edit operations come back with zero text in the response body — no caption lines, no confirmation string, nothing. This is expected behavior, not a fault. When it happens: first, do not retry the request or flag it as failed; second, call the Query State endpoint to pull the current caption timeline directly; third, surface whatever SRT data that endpoint returns as the authoritative result; fourth, continue the conversation normally using that state as ground truth.

**Two-stage generation**: Raw video processed through the auto-subtitle pipeline triggers a two-stage backend sequence automatically. Stage one delivers the base caption track — the raw transcript synced to the video timeline. Stage two fires without any prompt from the client: the backend appends background music and a generated title card to the captioned output. Both stages must complete before the final SRT and media package are ready for export. Poll or listen on the SSE channel until both stage signals arrive.

### 3.2 Pushing Media Files for Captioning

**File upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL upload**: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"urls":["<url>"],"source_type":"url"}'`

Use **me** in the path; backend resolves user from token.

Supported: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

The upload endpoint accepts video and audio source files that the subtitle engine will transcribe and sync captions against.

### 3.3 Checking Available Caption Credits
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
# → {"code":0,"data":{"available":XXX,"frozen":XX,"total":XXX}}
```
Query the credits endpoint before launching any long transcription job to confirm sufficient balance exists for the operation.

### 3.4 Fetching Current Job & Caption State
```bash
curl -s "https://mega-api-prod.nemovideo.ai/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Use **me** for user in path; backend resolves from token.
Key fields: `data.state.draft`, `data.state.video_infos`, `data.state.canvas_config`, `data.state.generated_media`.

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

**Draft ready for export** when `draft.t` exists with at least one track with non-empty `sg`.

**Track summary format**:
```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### 3.5 Exporting & Delivering the Final Caption Package

**Export does NOT cost credits.** Only generation/editing consumes credits.

Exporting a finished subtitle file — whether SRT, VTT, or burned-in video — consumes zero credits. The sequence runs as follows: (a) confirm both pipeline stages have completed via state query; (b) call the export endpoint with the desired caption format specified in the payload; (c) receive the signed delivery URL in the response; (d) stream or download the captioned asset from that URL; (e) acknowledge delivery back to the session so the backend can mark the job closed.

**b)** Submit: `curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'`

Note: `sessionId` is **camelCase** (exception). On failure → new `id`, retry once.

**c)** Poll (every 30s, max 10 polls): `curl -s "https://mega-api-prod.nemovideo.ai/api/render/proxy/lambda/<id>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"`

Status at top-level `status`: pending → processing → completed / failed. Download URL at `output.url`.

**d)** Download from `output.url` → send to user. Fallback: `https://mega-api-prod.nemovideo.ai/api/render/proxy/<id>/download`.

**e)** When delivering the video, **always also give the task detail link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

Progress messages: start "⏳ Rendering ~30s" → "⏳ 50%" → "✅ Video ready!" + file + **task detail link**.

### 3.6 Reconnecting After an SSE Drop

SSE connections drop — plan for it. Recovery follows five steps: 1) Detect the disconnect event on the client side immediately rather than waiting for a timeout. 2) Do not create a new session; the existing session ID remains valid. 3) Re-open the SSE channel using the same session ID and the Last-Event-ID header set to the most recently received event identifier. 4) Query the current caption state to backfill any SRT chunks or timing events that arrived during the gap. 5) Resume normal streaming from the last confirmed caption timestamp, discarding nothing from the pre-disconnect transcript.

## 4. GUI Layer Translation Rules

The backend operates under the assumption that a graphical interface sits between it and the end user — raw GUI instructions, button labels, or screen-level directions must never be forwarded through the API.

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Show state via §3.4 |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute §3.5 |
| "check account/billing" | Check §3.3 |

**Keep** content descriptions. **Strip** GUI actions.

## 5. Conversation & Interaction Patterns

- **Lead with intent, not mechanics:** When a user asks to caption a video, confirm the source file and target language before touching any endpoint — rushing to upload without context produces misaligned SRT output.
- **Translate edits into caption operations:** Phrases like 'fix that line' or 'move the subtitle earlier' map to specific timing-adjustment calls; identify the correct operation rather than asking the user to specify an endpoint.
- **Hold state across turns:** The active session and the last-known caption timeline should persist through the entire conversation — never lose track of which subtitle block is currently in scope.
- **Surface SRT data meaningfully:** When returning caption results, present timing and text in a readable format rather than dumping raw file content; summarize changes made to the transcript when relevant.
- **Anticipate the two-stage lag:** After raw video is submitted, set user expectations that a second processing stage will follow automatically — do not treat the first-stage caption delivery as the final result.

## 6. Known Constraints & Limitations

- File size and duration ceilings are enforced at the upload stage — submissions exceeding the defined thresholds will be rejected before transcription begins.
- Only the supported caption formats (SRT, VTT, and burned-in render) are available for export; custom or proprietary subtitle formats are outside scope.
- Simultaneous sessions per credential are capped; attempting to open additional sessions beyond the limit will return an authorization error rather than queuing.
- The auto-subtitle engine processes one language track per job — multi-language caption generation requires separate sequential submissions.
- BGM and title-card injection in stage two cannot be disabled or skipped; they are applied to every raw video job without exception.

## 7. Error Codes & Recovery Guidance

When a caption request goes wrong, the response code and message together tell you exactly where in the subtitle pipeline the failure occurred — map them using the table below.
| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

**Common**: no video → generate first; render fail → retry new `id`; SSE timeout → §3.6; silent edit → §3.1 fallback.

## 8. API Version & Permission Scopes

Always verify the active API version before building a caption request — version mismatches silently alter field availability and can corrupt SRT timing data in the response. Token scopes govern which subtitle operations are permitted: a read-only scope covers state queries and credit checks, while a write scope is required for uploads, session creation, and export triggers. Confirm both the version header value and the granted scopes during initial integration; do not assume defaults carry the permissions needed for full caption pipeline access.

## 9. Integration Guide

Integrating the auto-subtitle-generator-online skill into your existing workflow is straightforward and requires no dedicated infrastructure on your end. Start by connecting your ClawHub account to your preferred storage layer — whether that's a cloud bucket, a direct file upload, or a public video URL. Once connected, the OpenClaw agent can accept video files in mp4, mov, avi, webm, or mkv formats up to the plan's size limit and begin transcription immediately.

For teams using content management systems or video hosting platforms, the skill supports webhook callbacks that notify your system when a subtitle file is ready for download or when a captioned video has been processed. This makes it easy to slot auto-subtitle-generator-online into automated publishing pipelines without manual intervention at the caption stage.

Developers building custom applications can invoke the skill programmatically through the ClawHub agent API, passing parameters such as target language, caption format (SRT, VTT, or burned-in), font preferences, and output destination. The skill returns structured metadata alongside the subtitle file, including word-level confidence scores and flagged segments where audio quality may have affected accuracy — giving your team clear signals on where a human review pass might add value.
