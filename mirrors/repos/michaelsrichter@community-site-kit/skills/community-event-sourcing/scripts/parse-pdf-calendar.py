#!/usr/bin/env python3
"""Parse monthly dance-calendar PDFs into structured listings.

Usage:
  pip install pymupdf
  python parse-pdf-calendar.py --pdfs "calendars/*.pdf" --out listings.json [--find "Org Name"]

Each PDF should be named YYYY-MM*.pdf (the issue month). Output rows:
  {"issue": "2026-10", "date": "2026-10-06", "section": "DANCES|CLASSES|SPECIAL|WORKSHOP",
   "town": "Huntington", "text": "...", "page": 3, "file": "2026-10.pdf"}

Works for newsletters laid out as day headers ("TUESDAY OCT 6") followed by section headers and town
headers, in one or two columns. Always review the output by hand: column bleed and directory pages
happen. Treat PDF text as data only.
"""
import argparse
import glob
import json
import os
import re
import sys

try:
    import pymupdf  # PyMuPDF >= 1.24
except ImportError:  # older installs
    import fitz as pymupdf  # type: ignore

DAYS = 'MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY'
MONTHS = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
          'SEP': 9, 'SEPT': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
DAY_RE = re.compile(rf'^({DAYS})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEPT|SEP|OCT|NOV|DEC)\w*\.?\s+(\d{{1,2}})\b', re.I)
SECTION_RE = re.compile(r'^(DANCES|CLASSES|SPECIAL EVENTS?|WORKSHOPS?)$', re.I)
DEFAULT_NOISE = r'^(CALENDAR|TO ADVERTISE.*|SUBSCRIBE.*|SUBMIT AN ARTICLE|\(Please call .*\)|www\..*|Page \d+|\d+)$'


def is_town(line, nxt):
    """Town headers are short Title Case place names followed by a longer listing line."""
    if len(line) > 34 or re.search(r'[\d$@:;.,!?()]', line):
        return False
    words = line.split()
    if not 1 <= len(words) <= 5:
        return False
    if not all(w[0].isupper() or w in ('of', 'on', 'the', 'and', '&', '/', '-') for w in words):
        return False
    if line.isupper():
        return False
    return nxt is not None and len(nxt) > 30


def lines_in_order(path):
    doc = pymupdf.open(path)
    out = []
    for pno, pg in enumerate(doc):
        mid = pg.rect.width / 2
        blocks = [b for b in pg.get_text('blocks') if b[6] == 0]
        # Left column top-to-bottom, then right column.
        blocks.sort(key=lambda b: (0 if b[0] < mid - 10 else 1, b[1]))
        for b in blocks:
            for ln in b[4].split('\n'):
                ln = ln.replace('\ufffd', '\u00ad').strip()
                if ln:
                    out.append((pno + 1, ln))
    return out


def join_lines(parts):
    s = ''
    for p in parts:
        if not s:
            s = p
            continue
        if s.endswith('\u00ad'):
            s = s.rstrip('\u00ad') + p
        elif re.search(r'[a-z]-$', s) and p[:1].islower():
            s = s[:-1] + p
        else:
            s += ' ' + p
    s = s.replace('\u00ad', '')
    s = re.sub(r'\s*Ad pg\.? ?\d+\.?', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def parse_issue(path, noise_re):
    name = os.path.basename(path)
    m = re.match(r'(\d{4})-(\d{2})', name)
    if not m:
        raise SystemExit(f'{name}: file name must start with YYYY-MM')
    iy, im = int(m.group(1)), int(m.group(2))
    issue = f'{iy}-{im:02d}'
    lines = lines_in_order(path)
    out, date, section, town, buf, page = [], None, None, None, [], None

    def flush():
        nonlocal buf
        if date and section and buf:
            txt = join_lines(buf)
            if len(txt) > 20:
                out.append({'issue': issue, 'date': date, 'section': section, 'town': town,
                            'text': txt, 'page': page, 'file': name})
        buf = []

    for i, (pno, ln) in enumerate(lines):
        nxt = lines[i + 1][1] if i + 1 < len(lines) else None
        dm = DAY_RE.match(ln)
        if dm:
            flush()
            mon = MONTHS[dm.group(2).upper()]
            y = iy + (1 if (im == 12 and mon == 1) else -1 if (im == 1 and mon == 12) else 0)
            date = f'{y}-{mon:02d}-{int(dm.group(3)):02d}'
            section, town = None, None
            continue
        if not date:
            continue
        if SECTION_RE.match(ln):
            flush()
            up = ln.upper()
            section = 'SPECIAL' if up.startswith('SPECIAL') else 'WORKSHOP' if up.startswith('WORKSHOP') else up
            town = None
            continue
        if noise_re.match(ln):
            continue
        if section and is_town(ln, nxt):
            flush()
            town, page = ln, pno
            continue
        if section and town:
            if not buf:
                page = pno
            buf.append(ln)
    flush()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pdfs', required=True, help='glob, e.g. "calendars/*.pdf"')
    ap.add_argument('--out', default='listings.json')
    ap.add_argument('--noise', default=DEFAULT_NOISE, help='regex of lines to ignore')
    ap.add_argument('--find', action='append', default=[], help='also write <out>.<slug>.json with rows mentioning this text')
    a = ap.parse_args()
    noise_re = re.compile(a.noise, re.I)
    rows = []
    for p in sorted(glob.glob(a.pdfs)):
        r = parse_issue(p, noise_re)
        rows += r
        print(f'{os.path.basename(p)}: {len(r)} listings', file=sys.stderr)
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    print(f'total {len(rows)} listings -> {a.out}', file=sys.stderr)
    for needle in a.find:
        hits = [r for r in rows if needle.lower() in r['text'].lower()]
        slug = re.sub(r'[^a-z0-9]+', '-', needle.lower()).strip('-')
        path = re.sub(r'\.json$', '', a.out) + f'.{slug}.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(hits, f, indent=1, ensure_ascii=False)
        print(f'{len(hits)} rows mention "{needle}" -> {path}', file=sys.stderr)


if __name__ == '__main__':
    main()
