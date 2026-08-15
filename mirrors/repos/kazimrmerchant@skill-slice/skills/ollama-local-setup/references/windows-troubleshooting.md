# Windows Ollama: local models troubleshooting recipes

Substitute:
- `YOUR_MODELS_DIR` = your custom models location (set `$env:OLLAMA_MODELS` to it; backslashes on Windows)
- `<USER>` = Windows user, e.g. `ExampleUser`
- Default fallback if the env var is missing: `C:\Users\<user>\.ollama\models`

## Symptom → cause quick map
| Symptom | Likely cause |
|---|---|
| `/api/tags` = `{}`, `/v1/models` data = `null` | `OLLAMA_MODELS` set with forward slashes, OR app ignoring the var, OR wrong disk empty |
| `/v1/models` = `null` but `/api/tags` has models | two servers on 11434 (kill extras) |
| models reappear after manual `ollama serve` but vanish under the tray app | app ignores `OLLAMA_MODELS` → need junction |
| empty after reboot | relied on env var only; junction is reboot-safe |

## 1. Set OLLAMA_MODELS (backslashes — required on Windows)
```powershell
$env:OLLAMA_MODELS = "YOUR_MODELS_DIR"
# User scope (applies to new shells / after re-logon)
setx OLLAMA_MODELS $env:OLLAMA_MODELS
# Machine scope (all users)
setx OLLAMA_MODELS $env:OLLAMA_MODELS /M
```

## 2. Redirect the default path with a junction (app ignores the env var)
The Windows Ollama app always serves from `C:\Users\<USER>\.ollama\models`.
Point that path at your real models dir with a junction:
```powershell
$default = "C:\Users\<USER>\.ollama\models"
$target  = $env:OLLAMA_MODELS
# Remove the empty default dir if present (move contents first if any)
cmd /c rmdir "$default"
# Create junction (reboot-safe; filesystem-level)
cmd /c mklink /J "$default" "$target"
# Confirm
cmd /c fsutil reparsepoint query "$default"
```

## 3. Kill stale servers, then start exactly ONE
```powershell
taskkill /F /IM "ollama app.exe" /T
taskkill /F /IM ollama.exe /T
# Wait a moment, then launch the normal app (tray + supervised server):
start "" "$env:LOCALAPPDATA\Programs\Ollama\ollama app.exe"
# Do NOT also run `ollama serve` manually.
```

## 4. Verify
```powershell
ollama list
curl -s http://localhost:11434/api/tags
curl -s http://localhost:11434/v1/models
```
Or run the bundled probe: `powershell -NoProfile -File scripts/verify-ollama.ps1`.

## 5. Hermes provider wiring (local-only)
Set in Hermes config:
- `provider=ollama`
- `base_url=http://localhost:11434/v1`
- `api_key=ollama`
- `context_length=131072` (must be >= 64000 or Hermes refuses to init)
- default model e.g. `qwen3.6:27b` (must be present in `ollama list`)

## Notes
- Forward slashes in `OLLAMA_MODELS` on Windows are silently dropped → empty default path. Always backslashes.
- The junction is the robust fix because the app ignores the env var; an env var alone will not move the app's models.
- A second listener on 11434 corrupts `/v1/models` (returns `null`). One server only.
