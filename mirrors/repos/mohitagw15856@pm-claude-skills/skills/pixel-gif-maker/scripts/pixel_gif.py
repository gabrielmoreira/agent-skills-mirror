#!/usr/bin/env python3
"""Pixel GIF maker — animated retro pixel-text GIFs for Slack/Teams, in pure
stdlib. No PIL, no dependencies: this file IS the GIF89a encoder (fixed-width
LZW with periodic clear codes), a 5x7 pixel font, and four animation modes.
Deterministic: same args + --seed -> byte-identical output.

  python3 pixel_gif.py --text "SHIP IT" --mode party --out shipit.gif
  python3 pixel_gif.py --text "776 SKILLS" --mode scroll --fg mint --bg night
  python3 pixel_gif.py --self-test

Modes: scroll (marquee), pulse (heartbeat zoom), party (hue-cycling confetti),
sparkle (twinkling stars). Colors: night, plum, teal, mint, gold, coral, white, ink.
"""
import argparse
import random
import struct
import sys

# ── 5x7 pixel font (each glyph: 7 rows, 5 bits per row, MSB left) ────────────
FONT = {
    'A': [0x0E,0x11,0x11,0x1F,0x11,0x11,0x11], 'B': [0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E],
    'C': [0x0E,0x11,0x10,0x10,0x10,0x11,0x0E], 'D': [0x1E,0x11,0x11,0x11,0x11,0x11,0x1E],
    'E': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F], 'F': [0x1F,0x10,0x10,0x1E,0x10,0x10,0x10],
    'G': [0x0E,0x11,0x10,0x17,0x11,0x11,0x0F], 'H': [0x11,0x11,0x11,0x1F,0x11,0x11,0x11],
    'I': [0x0E,0x04,0x04,0x04,0x04,0x04,0x0E], 'J': [0x07,0x02,0x02,0x02,0x02,0x12,0x0C],
    'K': [0x11,0x12,0x14,0x18,0x14,0x12,0x11], 'L': [0x10,0x10,0x10,0x10,0x10,0x10,0x1F],
    'M': [0x11,0x1B,0x15,0x15,0x11,0x11,0x11], 'N': [0x11,0x19,0x15,0x13,0x11,0x11,0x11],
    'O': [0x0E,0x11,0x11,0x11,0x11,0x11,0x0E], 'P': [0x1E,0x11,0x11,0x1E,0x10,0x10,0x10],
    'Q': [0x0E,0x11,0x11,0x11,0x15,0x12,0x0D], 'R': [0x1E,0x11,0x11,0x1E,0x14,0x12,0x11],
    'S': [0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E], 'T': [0x1F,0x04,0x04,0x04,0x04,0x04,0x04],
    'U': [0x11,0x11,0x11,0x11,0x11,0x11,0x0E], 'V': [0x11,0x11,0x11,0x11,0x11,0x0A,0x04],
    'W': [0x11,0x11,0x11,0x15,0x15,0x1B,0x11], 'X': [0x11,0x11,0x0A,0x04,0x0A,0x11,0x11],
    'Y': [0x11,0x11,0x0A,0x04,0x04,0x04,0x04], 'Z': [0x1F,0x01,0x02,0x04,0x08,0x10,0x1F],
    '0': [0x0E,0x11,0x13,0x15,0x19,0x11,0x0E], '1': [0x04,0x0C,0x04,0x04,0x04,0x04,0x0E],
    '2': [0x0E,0x11,0x01,0x06,0x08,0x10,0x1F], '3': [0x0E,0x11,0x01,0x06,0x01,0x11,0x0E],
    '4': [0x02,0x06,0x0A,0x12,0x1F,0x02,0x02], '5': [0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E],
    '6': [0x06,0x08,0x10,0x1E,0x11,0x11,0x0E], '7': [0x1F,0x01,0x02,0x04,0x08,0x08,0x08],
    '8': [0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E], '9': [0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C],
    ' ': [0,0,0,0,0,0,0], '!': [0x04,0x04,0x04,0x04,0x04,0,0x04],
    '?': [0x0E,0x11,0x01,0x06,0x04,0,0x04], '.': [0,0,0,0,0,0x0C,0x0C],
    ',': [0,0,0,0,0x0C,0x04,0x08], "'": [0x0C,0x04,0x08,0,0,0,0],
    '-': [0,0,0,0x1F,0,0,0], '+': [0,0x04,0x04,0x1F,0x04,0x04,0],
    ':': [0,0x0C,0x0C,0,0x0C,0x0C,0], '#': [0x0A,0x1F,0x0A,0x0A,0x0A,0x1F,0x0A],
    '&': [0x0C,0x12,0x14,0x08,0x15,0x12,0x0D], '%': [0x19,0x1A,0x02,0x04,0x08,0x0B,0x13],
    '@': [0x0E,0x11,0x17,0x15,0x17,0x10,0x0E], '3>': [0,0x0A,0x1F,0x1F,0x0E,0x04,0],  # '3>' unused
    '<': [0x02,0x04,0x08,0x10,0x08,0x04,0x02], '>': [0x08,0x04,0x02,0x01,0x02,0x04,0x08],
    '/': [0x01,0x02,0x02,0x04,0x08,0x08,0x10],
}
HEART = [0x0A,0x1F,0x1F,0x1F,0x0E,0x04,0x00]  # ♥ via '<' + '3'? no: use '*' below
FONT['*'] = HEART  # type "*" to get a heart

COLORS = {
    'night': (18, 16, 43), 'plum': (42, 26, 94), 'teal': (14, 116, 144),
    'mint': (78, 205, 196), 'gold': (251, 191, 36), 'coral': (255, 107, 107),
    'white': (245, 245, 250), 'ink': (27, 32, 39), 'violet': (138, 92, 245),
}
PARTY_CYCLE = ['coral', 'gold', 'mint', 'violet', 'teal']

# ── GIF89a writer: fixed-width codes + periodic CLEAR (valid LZW, no tables) ──
def _lzw(indices, min_code):
    clear, end = 1 << min_code, (1 << min_code) + 1
    width = min_code + 1
    room = (1 << min_code) - 2          # literals emitted per clear block
    out, cur, bits = bytearray(), 0, 0
    def emit(code):
        nonlocal cur, bits
        cur |= code << bits
        bits += width
        while bits >= 8:
            out.append(cur & 0xFF)
            cur >>= 8
            bits -= 8
    emit(clear)
    n = 0
    for px in indices:
        if n == room:
            emit(clear)
            n = 0
        emit(px)
        n += 1
    emit(end)
    if bits:
        out.append(cur & 0xFF)
    return bytes(out)

def write_gif(path, frames, palette, w, h, delay_cs, loop=0):
    bits = max(2, (len(palette) - 1).bit_length())
    pal = list(palette) + [(0, 0, 0)] * ((1 << bits) - len(palette))
    with open(path, 'wb') as f:
        f.write(b'GIF89a')
        f.write(struct.pack('<HHBBB', w, h, 0xF0 | (bits - 1), 0, 0))
        for r, g, b in pal:
            f.write(bytes((r, g, b)))
        f.write(b'\x21\xFF\x0BNETSCAPE2.0\x03\x01' + struct.pack('<H', loop) + b'\x00')
        for fr in frames:
            f.write(b'\x21\xF9\x04\x04' + struct.pack('<H', delay_cs) + b'\x00\x00')
            f.write(b'\x2C' + struct.pack('<HHHHB', 0, 0, w, h, 0))
            f.write(bytes([bits]))
            data = _lzw(fr, bits)
            for i in range(0, len(data), 255):
                chunk = data[i:i + 255]
                f.write(bytes([len(chunk)]) + chunk)
            f.write(b'\x00')
        f.write(b'\x3B')

# ── raster helpers (logical grid of palette indices) ─────────────────────────
def blank(w, h, idx=0):
    return [idx] * (w * h)

def stamp_text(grid, w, h, text, x0, y0, idx, scale=1):
    x = x0
    for ch in text.upper():
        glyph = FONT.get(ch, FONT['?'])
        for gy, row in enumerate(glyph):
            for gx in range(5):
                if row & (1 << (4 - gx)):
                    for sy in range(scale):
                        for sx in range(scale):
                            px, py = x + gx * scale + sx, y0 + gy * scale + sy
                            if 0 <= px < w and 0 <= py < h:
                                grid[py * w + px] = idx
        x += 6 * scale
    return x - x0 - scale  # text pixel width

def text_width(text, scale=1):
    return (len(text) * 6 - 1) * scale

# ── modes ────────────────────────────────────────────────────────────────────
def build(mode, text, fg, bg, seed, scale):
    rng = random.Random(seed)
    s = scale
    th, tw = 7 * s, text_width(text, s)
    if mode == 'scroll':
        w, h = min(max(tw // 2, 40 * s), 120 * s), th + 10 * s
        palette = [COLORS[bg], COLORS[fg], COLORS['gold']]
        frames = []
        span, steps = w + tw, 40
        for i in range(steps):
            g = blank(w, h)
            x = w - (span * i) // steps
            stamp_text(g, w, h, text, x, 5 * s, 1, s)
            for k in range(4):  # fixed twinkles
                g[((k * 7 + i) % (h // s)) * s * w + ((k * 31 + i * 3) % (w // s)) * s] = 2
            frames.append(g)
        return frames, palette, w, h, 6
    if mode == 'pulse':
        big = s + 1
        w, h = text_width(text, big) + 8 * s, 7 * big + 8 * s
        palette = [COLORS[bg], COLORS[fg]]
        frames = []
        for sc in [s, s, big, big, big, s, s, s]:
            g = blank(w, h)
            stamp_text(g, w, h, text, (w - text_width(text, sc)) // 2, (h - 7 * sc) // 2, 1, sc)
            frames.append(g)
        return frames, palette, w, h, 12
    if mode == 'party':
        w, h = tw + 12 * s, th + 12 * s
        palette = [COLORS['night']] + [COLORS[c] for c in PARTY_CYCLE] + [COLORS['white']]
        frames = []
        confetti = [(rng.randrange(w), rng.randrange(h), rng.randrange(1, 6)) for _ in range(w * h // (60 * s))]
        for i in range(10):
            g = blank(w, h)
            for (cx, cy, cc) in confetti:
                g[((cy + i * 2) % h) * w + cx] = 1 + (cc + i) % 5
            stamp_text(g, w, h, text, 6 * s, 6 * s, 1 + i % 5, s)
            frames.append(g)
        return frames, palette, w, h, 10
    # sparkle
    w, h = tw + 12 * s, th + 12 * s
    palette = [COLORS[bg], COLORS[fg], COLORS['gold'], COLORS['white']]
    stars = [(rng.randrange(w), rng.randrange(h), rng.randrange(3)) for _ in range(w * h // (40 * s))]
    frames = []
    for i in range(8):
        g = blank(w, h)
        for (sx, sy, ph) in stars:
            tw_idx = [0, 2, 3, 2][(ph + i) % 4]
            if tw_idx:
                g[sy * w + sx] = tw_idx
        stamp_text(g, w, h, text, 6 * s, 6 * s, 1, s)
        frames.append(g)
    return frames, palette, w, h, 12

def main():
    ap = argparse.ArgumentParser(description='Retro pixel-text animated GIFs, pure stdlib.')
    ap.add_argument('--text', default='SHIP IT')
    ap.add_argument('--mode', choices=['scroll', 'pulse', 'party', 'sparkle'], default='party')
    ap.add_argument('--fg', default='mint', choices=sorted(COLORS))
    ap.add_argument('--bg', default='night', choices=sorted(COLORS))
    ap.add_argument('--scale', type=int, default=3, choices=[1, 2, 3, 4])
    ap.add_argument('--seed', type=int, default=7, help='same seed = byte-identical gif')
    ap.add_argument('--out', default='pixel.gif')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if a.self_test:
        import hashlib, io, os, tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 't.gif')
            for mode in ['scroll', 'pulse', 'party', 'sparkle']:
                fr, pal, w, h, dl = build(mode, 'OK!', 'mint', 'night', 7, 2)
                write_gif(p, fr, pal, w, h, dl)
                head = open(p, 'rb').read(6)
                assert head == b'GIF89a', mode
                print(f'  {mode}: {w}x{h}, {len(fr)} frames, {os.path.getsize(p)} bytes, '
                      f'sha256 {hashlib.sha256(open(p,"rb").read()).hexdigest()[:12]}')
        print('self-test OK — all four modes produce valid GIF89a headers, deterministic.')
        return
    if len(a.text) > 24:
        sys.exit('Keep it under 24 characters — pixel fonts are for punchlines, not paragraphs.')
    frames, palette, w, h, delay = build(a.mode, a.text, a.fg, a.bg, a.seed, a.scale)
    write_gif(a.out, frames, palette, w, h, delay)
    print(f'{a.out}: {w}x{h}, {len(frames)} frames ({a.mode}). Drag it into Slack.')

if __name__ == '__main__':
    main()
