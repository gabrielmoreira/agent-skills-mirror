#!/usr/bin/env node
// Make a short, silent, small web video + poster image for a slideshow.
//
//   node prepare-video.mjs --in clip.mp4 --out public/media/videos/name.mp4 [--start 0] [--seconds 16] [--width 480] [--crf 28]
//
// Output: H.264 (yuv420p, +faststart), no audio, <width> px wide, and <name>.jpg poster from 1 s in.
// Uses ffmpeg on PATH, or ffmpeg-static if installed in the current folder (npm i --no-save ffmpeg-static).
import { execFileSync } from 'node:child_process';
import { statSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { createRequire } from 'node:module';

const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const input = get('in');
const out = get('out');
if (!input || !out) {
  console.error('Usage: node prepare-video.mjs --in clip.mp4 --out out.mp4 [--start 0] [--seconds 16] [--width 480]');
  process.exit(1);
}
let ffmpeg = 'ffmpeg';
try {
  ffmpeg = createRequire(join(process.cwd(), 'package.json'))('ffmpeg-static') || 'ffmpeg';
} catch {
  // fall back to ffmpeg on PATH
}
const start = get('start', '0');
const seconds = get('seconds', '16');
const width = get('width', '480');
const crf = get('crf', '28');
mkdirSync(dirname(out), { recursive: true });
const run = (a) => execFileSync(ffmpeg, a, { stdio: ['ignore', 'ignore', 'pipe'] });
run(['-y', '-ss', start, '-i', input, '-t', seconds, '-an', '-vf', `scale=${width}:-2`, '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
const poster = out.replace(/\.mp4$/i, '.jpg');
run(['-y', '-ss', '1', '-i', out, '-frames:v', '1', '-q:v', '3', poster]);
const kb = Math.round(statSync(out).size / 1024);
console.log(`${out}  ${kb} KB${kb > 1100 ? '  (over ~1 MB: raise --crf or shorten --seconds)' : ''}\n${poster}`);
