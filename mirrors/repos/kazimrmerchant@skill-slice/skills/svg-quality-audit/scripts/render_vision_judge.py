#!/usr/bin/env python3
"""svg-quality-audit — Phase 2 (render) + Phase 3 (vision judge).
Usage:
  python render_vision_judge.py --render-only <svg-dir> <png-dir> [<file-list.json>]
  python render_vision_judge.py --judge <png-dir> [--model nvidia/...:free]
Renders SVGs to PNG via Chrome headless, then scores with a free VLM (OpenRouter).
Resumable, per-call 60s timeout, 429 backoff, incremental JSON. Run --judge in background.

Env: OPENROUTER_API_KEY (never printed). Model default: nvidia/nemotron-nano-12b-v2-vl:free.
Chrome: C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe (edit CHROME if different).
"""
import os, re, json, base64, time, sys, urllib.request, urllib.error

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"
SYS = ("You are a strict SVG art-quality auditor for a product asset library. Each image is a "
       "render of an SVG (checkerboard = transparent). Score 1-10 where 10 = polished, recognizable "
       "subject, intentional composition, good color; 1 = blank/garbled/broken/unreadable. "
       "Reply EXACTLY:\nSCORE: <1-10>\nFLAGS: <none|broken|text-only|empty|abstract-sludge|off-canvas>\nWHY: <one line>")

def render(svg_dir, png_dir, files):
    import subprocess
    os.makedirs(png_dir, exist_ok=True)
    n = 0
    for f in files:
        outp = os.path.join(png_dir, f.replace(".svg", ".png"))
        if os.path.exists(outp): continue
        svgp = os.path.join(svg_dir, f)
        cmd = [CHROME, "--headless", "--no-sandbox", "--disable-gpu",
               "--force-device-scale-factor=1", "--window-size=400,400", "--hide-scrollbars",
               f"--screenshot={outp}", "--default-background-color=00000000", f"file://{svgp}"]
        subprocess.run(cmd, capture_output=True, timeout=60)
        n += 1
    print(f"rendered {n} new -> {len(files)} total")

def judge(png_dir, model):
    KEY = os.environ.get("OPENROUTER_API_KEY")
    if not KEY: sys.exit("Missing OPENROUTER_API_KEY")
    outp = os.path.join(png_dir, "_vision_scores.json")
    done = {}
    if os.path.exists(outp):
        for r in json.load(open(outp)):
            if not r["out"].startswith("ERR"): done[r["file"]] = r["out"]
    pngs = [f for f in os.listdir(png_dir) if f.endswith(".png")]
    def b64(p):
        return base64.b64encode(open(p, "rb").read()).decode()
    n = 0
    for f in pngs:
        if f in done: continue
        b = b64(os.path.join(png_dir, f))
        out = "ERR: unknown"
        for attempt in range(4):
            try:
                payload = {"model": model,
                    "messages": [{"role":"system","content":SYS},
                                 {"role":"user","content":[
                                     {"type":"text","text":f"File: {f}"},
                                     {"type":"image_url","image_url":{"url":"data:image/png;base64,"+b}}]}],
                    "max_tokens": 120}
                req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                    data=json.dumps(payload).encode(),
                    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    out = json.load(r)["choices"][0]["message"]["content"]
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(6*(attempt+1)); continue
                out = f"ERR HTTP {e.code}"; break
            except Exception as e:
                out = f"ERR: {e}"; time.sleep(3)
        done[f] = out
        json.dump([{"file": k, "out": v} for k, v in done.items()], open(outp, "w"), indent=1)
        n += 1
        if n % 10 == 0: print(f"scored {n}", flush=True)
    print(f"DONE scored {n} new, total {len(done)} -> {outp}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--render-only" in args:
        i = args.index("--render-only")
        svg_dir, png_dir = args[i+1], args[i+2]
        files = json.load(open(args[i+3])) if len(args) > i+3 else \
                [f for f in os.listdir(svg_dir) if f.endswith(".svg")]
        render(svg_dir, png_dir, files)
    elif "--judge" in args:
        i = args.index("--judge")
        judge(args[i+1], MODEL)
    else:
        print(__doc__)
