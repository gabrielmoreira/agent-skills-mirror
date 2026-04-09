# Prompt-Based Music Search

Search for music tracks using natural language prompts.

## API Endpoint

```
POST https://api.harmix.ai/search
```

## Authentication

Include the API key in the request header:

```
api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e
```

## Request Format

Send a JSON body with the `prompt` field:

```json
{
  "prompt": "upbeat electronic music for a workout"
}
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Number of tracks to return |

## Response Format

The response contains an array of tracks. Extract `track_title`, `artists`, and the streaming URL from `extra_parameters.url`:

```json
{
  "tracks_number": 10,
  "tracks": [
    {
      "metadata": {
        "track_title": "Energy Boost",
        "artists": ["Artist Name"],
        "extra_parameters": {
          "url": "https://open.spotify.com/track/abc123"
        }
      }
    }
  ]
}
```

## Example: Search with curl

```bash
curl -X POST "https://api.harmix.ai/search?limit=5" \
  -H "api_key: v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "calm piano music for studying"}'
```

## Example: Search with Python

```python
import requests

response = requests.post(
    "https://api.harmix.ai/search",
    headers={
        "api_key": "v8mWxAGAFTEFcU9NYGGhDWWbzYXS5e",
        "Content-Type": "application/json"
    },
    params={"limit": 5},
    json={"prompt": "energetic rock music for a road trip"}
)

data = response.json()
for track in data["tracks"]:
    title = track["metadata"]["track_title"]
    artists = ", ".join(track["metadata"]["artists"])
    url = track["metadata"].get("extra_parameters", {}).get("url", "N/A")
    print(f"{title} by {artists}")
    print(f"  {url}")
```

## Example Prompts

- "relaxing acoustic guitar for meditation"
- "upbeat pop music for a party"
- "cinematic orchestral music for a trailer"
- "lo-fi hip hop beats for studying"
- "energetic electronic music 120 bpm"
- "sad piano ballad"
- "happy ukulele music for a commercial"
