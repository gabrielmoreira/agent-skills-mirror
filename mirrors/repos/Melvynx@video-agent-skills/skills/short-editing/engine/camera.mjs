#!/usr/bin/env node
// Camera framing from a take: samples a few frames, finds the face (Apple Vision on a Mac, MediaPipe elsewhere) and returns the spec
// `cam` for it: crop = the full-height slice around the face (10:9, like the default 1200x1080 on a 1080p take),
// eyes = the eye point inside that crop. Used by `short.mjs init --source` and the studio-setup skill.
//   node camera.mjs <video> [--samples 9]      prints {"w","h","crop","eyes","faces"}
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { FFMPEG, FFPROBE, niced, visionTool } from './platform.mjs';

const even = x => Math.round(x / 2) * 2;
const median = a => { const s = [...a].sort((x, y) => x - y); return s.length ? s[s.length >> 1] : 0; };

export function size(f) {
  const r = spawnSync(FFPROBE, ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'format=duration:stream=width,height:stream_tags=rotate:stream_side_data=rotation', '-of', 'json', f], { encoding: 'utf8' });
  if (r.status) throw new Error(`ffprobe failed on ${f}`);
  const j = JSON.parse(r.stdout), v = j.streams?.[0] || {};
  const rot = Math.abs(+(v.tags?.rotate ?? v.side_data_list?.find(d => d.rotation != null)?.rotation ?? 0)) % 180 === 90;
  return { w: rot ? v.height : v.width, h: rot ? v.width : v.height, dur: +(j.format?.duration || 0) };
}

// crop + eyes from a face box [cx, cy, fw, fh] (source px)
export function framing(w, h, face) {
  const cw = Math.min(w, even(h * 10 / 9)), ch = h;
  const [cx, cy, , fh] = face || [w / 2, h * .42, 0, h * .3];
  const x = even(Math.min(Math.max(0, cx - cw / 2), w - cw));
  return { crop: [x, 0, cw, ch], eyes: [Math.round(cx - x), Math.round(cy - fh * .22)] };
}

export function detectCamera(video, { samples = 9 } = {}) {
  const { w, h, dur } = size(video);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'short-cam-'));
  try {
    for (let i = 0; i < samples; i++) {
      const t = dur * (i + .5) / samples;
      spawnSync(...niced(FFMPEG, ['-y', '-loglevel', 'error', '-ss', t.toFixed(2), '-i', video, '-frames:v', '1', '-q:v', '3', path.join(dir, `${String(i).padStart(5, '0')}.jpg`)]));
    }
    const out = path.join(dir, 'faces.json');
    const tool = visionTool('faces'), r = spawnSync(...niced(tool.cmd, [...tool.args, dir, out]), { encoding: 'utf8' });
    if (r.status || !fs.existsSync(out)) throw new Error(`face detection failed: ${(r.stderr || r.stdout || '').slice(-300)}`);
    const found = JSON.parse(fs.readFileSync(out, 'utf8')).filter(f => f[2] > 0);
    const det = +(r.stdout.match(/(\d+) detected/)?.[1] ?? found.length);
    const face = det ? [0, 1, 2, 3].map(k => median(found.map(f => f[k]))) : null;
    return { w, h, ...framing(w, h, face), faces: det };
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  const a = process.argv.slice(2), v = a.find(x => !x.startsWith('--'));
  if (!v) { console.log('usage: node camera.mjs <video> [--samples 9]'); process.exit(1); }
  const i = a.indexOf('--samples');
  console.log(JSON.stringify(detectCamera(path.resolve(v.replace(/^~/, os.homedir())), { samples: i < 0 ? 9 : +a[i + 1] })));
}
