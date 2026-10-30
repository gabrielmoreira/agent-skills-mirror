# -*- coding: utf-8 -*-
"""
Project-agnostic Azure Speech (REST) narration generator for the Remotion
demo/marketing video pipeline.

Reads a JSON manifest of clips, synthesizes one MP3 per clip into the Remotion
project's public/ folder, and probes each clip's real duration with ffprobe so
you can compute scene durationInFrames = ceil(seconds * fps) + ~20.

KEY TRICK — one multilingual voice, several languages:
  A single multilingual voice (e.g. en-GB-OllieMultilingualNeural,
  en-US-AvaMultilingualNeural) can speak other languages with good prosody when
  the text is wrapped in an SSML <lang xml:lang='xx-XX'> tag. Set the clip's
  "lang" to the SPOKEN language; if it differs from the voice's base locale the
  script wraps it automatically. This keeps one consistent voice across a FR + EN
  video pair.

AUTH: uses an AAD bearer token (no API key in the repo). Refresh with:
  az account get-access-token --scope https://cognitiveservices.azure.com/.default \
     --query accessToken -o tsv > %TEMP%/aad_token.txt   (Windows)
  ...> /tmp/aad_token.txt                                 (macOS/Linux)
Tokens expire ~1h. If you get 401/tenant-mismatch, check `az account show`,
`az account set --subscription <id>`, and re-run.

USAGE:
  python generate_tts.py --manifest clips.example.json \
      --endpoint https://<resource>.cognitiveservices.azure.com \
      --voice en-GB-OllieMultilingualNeural \
      --out ../remotion/public \
      [--token-file /path/to/aad_token.txt] [--rate 0%]

MANIFEST (clips.example.json): a list of objects:
  [{ "id": "narr_hook_fr", "lang": "fr-FR", "text": "…" }, ...]
Output file name = "<id>.mp3".
"""
import argparse
import html
import json
import os
import subprocess
import sys
import tempfile


def default_token_file():
    tmp = os.environ.get("TEMP") or tempfile.gettempdir()
    return os.path.join(tmp, "aad_token.txt")


def build_ssml(text, spoken_lang, voice, rate):
    esc = html.escape(text)
    base_locale = "-".join(voice.split("-")[:2]) if "-" in voice else "en-US"
    prosody = f"<prosody rate='{rate}'>{esc}</prosody>"
    # Wrap in <lang> only when the spoken language differs from the voice's base
    # locale — this is what lets one multilingual voice speak another language.
    if spoken_lang and spoken_lang.lower() != base_locale.lower():
        inner = f"<lang xml:lang='{spoken_lang}'>{prosody}</lang>"
    else:
        inner = prosody
    return (
        f"<speak version='1.0' xml:lang='{base_locale}' "
        f"xmlns:mstts='http://www.w3.org/2001/mstts'>"
        f"<voice name='{voice}'>{inner}</voice></speak>"
    )


def synth(text, spoken_lang, voice, rate, endpoint, token, out_path):
    ssml = build_ssml(text, spoken_lang, voice, rate)
    ssml_path = out_path + "._ssml.xml"
    with open(ssml_path, "w", encoding="utf-8") as f:
        f.write(ssml)
    url = endpoint.rstrip("/") + "/tts/cognitiveservices/v1"
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/ssml+xml",
        "-H", "X-Microsoft-OutputFormat: audio-24khz-160kbitrate-mono-mp3",
        "-H", "User-Agent: demo-video-tts",
        "--data-binary", f"@{ssml_path}",
        "-o", out_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(ssml_path)
    except OSError:
        pass
    size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
    # A tiny file is almost always a JSON/HTML error body, not audio — surface it.
    if size and size < 2000:
        with open(out_path, "rb") as f:
            print("  ERROR body:", f.read()[:400])
    return size


def probe_duration(path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True,
        )
        return float(out.stdout.strip())
    except (ValueError, FileNotFoundError):
        return None


def main():
    ap = argparse.ArgumentParser(description="Azure Speech narration generator")
    ap.add_argument("--manifest", required=True, help="JSON list of {id, lang, text}")
    ap.add_argument("--endpoint", required=True, help="https://<resource>.cognitiveservices.azure.com")
    ap.add_argument("--voice", required=True, help="e.g. en-GB-OllieMultilingualNeural")
    ap.add_argument("--out", required=True, help="output folder (Remotion public/)")
    ap.add_argument("--token-file", default=default_token_file())
    ap.add_argument("--rate", default="0%", help="prosody rate, e.g. -5%, 0%, +5%")
    args = ap.parse_args()

    with open(args.token_file, "r", encoding="ascii") as f:
        token = f.read().strip()  # .strip() is critical: a trailing newline silently breaks the header
    with open(args.manifest, "r", encoding="utf-8") as f:
        clips = json.load(f)
    os.makedirs(args.out, exist_ok=True)

    durations = {}
    for c in clips:
        out_path = os.path.join(args.out, f"{c['id']}.mp3")
        size = synth(c["text"], c.get("lang", ""), args.voice, args.rate, args.endpoint, token, out_path)
        dur = probe_duration(out_path) if size >= 2000 else None
        durations[c["id"]] = dur
        frames = (int(dur * 30) + 1 + 20) if dur else "?"  # informational: fps=30
        print(f"{c['id']} [{c.get('lang','base')}]: {size} bytes"
              + (f", {dur:.2f}s -> ~{frames} frames@30fps" if dur else ""))

    print("\nDURATIONS (seconds):")
    print(json.dumps(durations, indent=2))
    print("DONE")


if __name__ == "__main__":
    sys.exit(main())
