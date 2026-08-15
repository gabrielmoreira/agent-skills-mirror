#!/usr/bin/env python3
"""svg-quality-audit — Phase 1 structural scan (stdlib only, no deps).
Usage: python structure_scan.py <dir-containing-svgs> [--json out.json]
Scans 100% of *.svg. Reports validity, drawable-shape stats, and the defect taxonomy.
Safe / read-only. Mirrors the verified logic from the 2026-07-15 vault audit.
"""
import os, re, sys, json
from collections import Counter
from xml.etree import ElementTree as ET

DRAW = {"path","rect","circle","ellipse","line","polyline","polygon"}

def metrics(raw):
    try:
        ET.fromstring(raw); valid = True
    except ET.ParseError:
        valid = False
    draw = sum(len(re.findall(r"<"+t+r"\b", raw)) for t in DRAW)
    has_escape = ("\\n" in raw) or ("\\t" in raw) or ('\\"' in raw)
    js = bool(re.search(r'<script[^>]*type\s*=\s*["\'](?:text/javascript|application/javascript|application/ecmascript)["\']', raw, re.I))
    jsonld = len(re.findall(r'<script[^>]*type\s*=\s*["\']application/ld\+json["\']', raw, re.I))
    junk = False
    m = re.search(r"</svg>\s*", raw)
    if m and raw[m.end():].strip():
        junk = True
    dup = False
    for tm in re.finditer(r"<(\w+)([^>]*)>", raw):
        names = re.findall(r"([\w:-]+)\s*=", tm.group(2))
        if len(names) != len(set(names)):
            dup = True; break
    ent = False
    if "&" in raw:
        tmp = re.sub(r"&(amp|lt|gt|quot|apos|#\d+;|#x[0-9a-fA-F]+;);", "", raw)
        if re.search(r"&[A-Za-z][A-Za-z0-9]*;", tmp) and not re.search(r"<!ENTITY", raw):
            ent = True
    vb = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', raw)
    return dict(valid=valid, draw=draw, has_escape=has_escape, js=js, jsonld=jsonld,
                junk=junk, dup=dup, ent=ent, vb=bool(vb))

def main():
    d = sys.argv[1]
    out = None
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json")+1]
    files = [f for f in os.listdir(d) if f.lower().endswith(".svg")]
    agg = Counter()
    draws = []
    for f in files:
        raw = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
        m = metrics(raw)
        agg["n"] += 1
        for k in ("valid","has_escape","js","jsonld","junk","dup","ent","vb"):
            if m[k]: agg[k] += 1
        draws.append(m["draw"])
    draws.sort()
    pct = lambda a,p: a[min(int(len(a)*p), len(a)-1)]
    print(f"files: {agg['n']}")
    print(f"valid XML: {agg['valid']}  invalid: {agg['n']-agg['valid']}")
    print(f"escape-bug: {agg['has_escape']}")
    print(f"executable JS <script>: {agg['js']}  JSON-LD <script>: {agg['jsonld']}")
    print(f"LLM-junk-after-</svg>: {agg['junk']}  duplicate-attr: {agg['dup']}  undefined-entity: {agg['ent']}")
    print(f"no viewBox: {agg['n']-agg['vb']}")
    print(f"drawable: median {pct(draws,.5)} p25 {pct(draws,.25)} p75 {pct(draws,.75)} p95 {pct(draws,.95)}")
    if out:
        json.dump({"agg": dict(agg), "drawable_p95": pct(draws,.95)}, open(out,"w"), indent=1)
        print("wrote", out)

if __name__ == "__main__":
    main()
