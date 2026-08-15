# Free vision endpoints

Many agents cannot judge binary PNGs by reading pixels. To score rendered SVGs, call a vision-language model over a real API.

## Working

### OpenRouter free vision (primary)

- Endpoint: `https://openrouter.ai/api/v1/chat/completions` (OpenAI-compatible).
- Key: live OpenRouter key via env `OPENROUTER_API_KEY` (never print it). Do not treat a redacted local-config placeholder as a usable key.
- List free vision models live via `GET /api/v1/models` and filter `:free` plus `image` in `input_modalities`.
- Image: send as `data:image/png;base64,<b64>` in the `image_url` content block.
- Rate limit: free tier is throttled; loop with 429 backoff and run large passes in the background.

### Local Ollama (free, slower)

- Endpoint: `http://localhost:11434/api/chat` (native) or `/v1` (OpenAI-compat).
- Use a vision-capable local tag the user already has installed.
- Cold load of large models can exceed a 120s timeout; use 180–300s and small batches.

## Render step (before any judge)

Chrome headless is reliable:

```
chrome --headless --no-sandbox --disable-gpu --force-device-scale-factor=1 --window-size=400,400 --hide-scrollbars --screenshot=<out.png> --default-background-color=00000000 file://<in.svg>
```

On Windows the binary is typically `C:\Program Files\Google\Chrome\Application\chrome.exe`.
