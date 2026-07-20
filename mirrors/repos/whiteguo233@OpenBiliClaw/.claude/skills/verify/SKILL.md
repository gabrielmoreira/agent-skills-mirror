---
name: verify
description: Drive a real serve-api process against isolated project roots to verify backend/web changes end-to-end
---

# Verifying OpenBiliClaw backend changes end-to-end

Port 8420 is the user's production backend — never restart or reuse it. Spin up
throwaway serve-api instances on spare ports (846x) against isolated project
roots instead, and always kill them when done.

## Recipe

1. **Isolated project root**: `mktemp -d /tmp/obc-verify.XXXXXX`, put a minimal
   `config.toml` + empty `data/` inside, point `OPENBILICLAW_PROJECT_ROOT` at it.
   `data_dir = "data"` resolves against that root.

2. **Craft the backend state you need via config/data, not mocks**:
   - *Configured but uninitialized*: any provider section with a dummy
     `api_key` (registry build does not call the network at startup).
   - *Degraded (`llm_registry_unavailable`)*: all provider keys empty **and**
     launch with `env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u GOOGLE_API_KEY
     -u GEMINI_API_KEY` — ambient keys silently un-degrade it.
   - *Initialized (profile ready)*: copy the real `data/memory/soul.json` into
     the tmp root's `data/memory/` before launch. `is_profile_ready()` ==
     "soul memory layer has data", loaded at startup (don't hot-drop the file
     into a running instance and expect it to flip).

3. **Launch** (background, stdin must be closed or it hangs):
   ```bash
   OPENBILICLAW_PROJECT_ROOT=/tmp/obc-verify.XXX/a \
     nohup .venv/bin/openbiliclaw serve-api --host 127.0.0.1 --port 8461 \
     > /tmp/obc-verify.XXX/a/server.log 2>&1 < /dev/null &
   ```
   Ready in ~5-8s. Use the main repo's `.venv/bin/openbiliclaw`.

4. **Probe with `curl --noproxy '*'`** — the local proxy/TUN hijacks loopback
   otherwise. `curl -D -` for redirect headers, `/api/health` to confirm the
   state you crafted (`status`, `profile_ready`), `server.log` for the
   "started in degraded mode" line.

5. **Clean up**: kill the PIDs, confirm nothing listens on the ports
   (`lsof -nP -iTCP:846x -sTCP:LISTEN`), `rm -rf` the tmp roots. Zombie temp
   serve-api instances have corrupted real user data before — never skip this.
