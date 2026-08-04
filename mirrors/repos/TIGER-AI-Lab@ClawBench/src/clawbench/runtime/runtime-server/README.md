# ClawBench Runtime Server

The ClawBench Runtime Server is a Python backend instrumentation server that connects to Chromium over CDP and writes benchmark artifacts. It is responsible for:

- Capturing browser DOM actions through CDP-injected listeners and storing them in jsonl format.
- Capturing screenshots through CDP after browser actions.
- Logging HTTP requests and blocking matching eval-schema requests through CDP's `Fetch` domain.
- Recording the local Xvfb display to `recording.mp4`, or deferring replay to a remote provider such as Browserbase.
- Exposing a credential-free local CDP discovery and WebSocket bridge when the upstream browser is remote.

## Implementation

Single `server.py` — a FastAPI application run with uvicorn.

### Endpoints

| Method | Path                  | Content-Type     | Description                                                                             |
| ------ | --------------------- | ---------------- | --------------------------------------------------------------------------------------- |
| GET    | `/api/status`         | —                | Returns `{"status": "ok"}`                                                              |
| POST   | `/api/action`         | application/json | Compatibility endpoint; CDP capture writes actions directly                             |
| POST   | `/api/screenshot`     | application/json | Compatibility endpoint; CDP capture writes screenshots directly                         |
| POST   | `/api/stop`           | —                | Signals session stop, returns session summary                                           |
| POST   | `/api/stop-recording` | —                | Stops ffmpeg recording, finalizes MP4                                                   |
| GET    | `/json/version`       | —                | Remote-mode Chrome-compatible browser discovery                                         |
| GET    | `/json` or `/json/list` | —              | Remote-mode Chrome-compatible target discovery                                          |
| WS     | `/devtools/browser/{id}` | —             | Credential-free proxy to the provider's browser-level CDP WebSocket                     |

### Screen Recording

In local mode, the server starts an ffmpeg process that records the Xvfb virtual display (`DISPLAY=:99`) to `/data/recording.mp4` using H.264 at 15fps. On `/api/stop-recording`, the ffmpeg process is gracefully terminated with SIGINT to finalize the MP4 file. The `/api/stop` endpoint handles session bookkeeping (eval promotion, watchdog signaling) without stopping the recording, allowing a grace period to capture the final state.

In provider recording mode, ffmpeg and Xvfb recording are skipped. Browserbase
stores the replay, and the runner records its Session Inspector URL in
`browser_runtime.recording_url` in `run-meta.json`. Action screenshots,
browser actions, HTTP requests, interception evidence, and agent messages still
remain local ClawBench artifacts.

### Remote CDP bridge

For a remote browser, the runner mounts the credential-bearing CDP URL as a
read-only secret file. The runtime server uses that endpoint for capture and
interception while harnesses connect only to `http://127.0.0.1:7878`. The
Chrome-compatible discovery endpoints and WebSocket proxy above keep the signed
provider URL out of harness configuration, container arguments, logs, and saved
metadata.

NOTE: Since the actual MP4 is assembled after the session ends, during testings that need manual termination, do `curl -X POST http://localhost:7878/api/stop` instead of stopping the container/process directly to ensure the recording is finalized properly.

### Data Storage

All data is written to the directory specified by `CLAWBENCH_DATA_DIR` (default: `/data`):

```
/data/
  actions.jsonl       # Append-only, one JSON object per line
  requests.jsonl      # Append-only browser request log
  interception.json   # Interception result
  screenshots/        # {timestamp}.png files
  recording.mp4       # Local mode only; remote provider URL is in run-meta.json
```

### Running Locally

The runtime server normally runs only inside the benchmark container. For
debugging the server by itself, use its local uv project:

```bash
cd src/clawbench/runtime/runtime-server
CLAWBENCH_DATA_DIR=./data DISPLAY=:99 uv run --frozen uvicorn server:app --host 0.0.0.0 --port 7878
```

### Dependencies

The runtime server is container-only and has its own uv project in
`src/clawbench/runtime/runtime-server/`:
- `fastapi` — web framework
- `uvicorn` — ASGI server
- `websocket-client` — WebSocket client for CDP communication
- `websockets` — uvicorn WebSocket transport for the local CDP bridge

System dependency: `ffmpeg` (for screen recording and MP4 encoding).
