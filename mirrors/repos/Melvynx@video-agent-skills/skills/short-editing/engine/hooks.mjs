// Hook explorations: N completely different intros of one short, side by side in the studio as v<n>.1, v<n>.2...
// Each one is <short>/variants/<n>.<i>-<hook>/, a generated engine project = the short's spec with `window.HOOK = '<hook>'`
// prepended, sharing the short's assets, source/style.json and camera frames (same cuts and speed, so no prepare).
// The spec ends with one block that swaps the hook only (scenes from 0, layout keys, captions.hide) when window.HOOK is set:
//   if (window.HOOK) { const H = { 'terminal'() {...}, 'noir'() {...} }; H[window.HOOK](); }
// The edit itself never sets HOOK. Fixes go into the short's spec, then run this again and render the variants. Render the
// short itself first: the variants are named after the studio's current version, an older one shows them as stale.
//   node hooks.mjs <short> <hook> [<hook>...]       (re)writes the variant folders, prints their paths
//   then per variant: node short.mjs render <dir> --workers 2 && node short.mjs audio <dir> && node short.mjs final <dir>
import fs from 'node:fs';
import path from 'node:path';
import { currentReview } from '../review/build-review.mjs';

const [src, ...hooks] = process.argv.slice(2);
if (!src || !hooks.length) { console.error('usage: node hooks.mjs <short> <hook> [<hook>...]'); process.exit(1); }
const SRC = path.resolve(src), from = currentReview(SRC).cur.version;   // the studio's current version: hooks are v<n>.1...
const link = (to, target) => { try { fs.lstatSync(to); } catch { fs.symlinkSync(target, to); } };
hooks.forEach((h, i) => {
  const id = `${from?.slice(1) || 'x'}.${i + 1}-${h}`, DST = path.join(SRC, 'variants', id);
  for (const d of ['assets', 'source', 'files', 'output', 'frames']) fs.mkdirSync(path.join(DST, d), { recursive: true });
  for (const f of fs.readdirSync(path.join(SRC, 'assets'))) {
    if (['mix.wav', 'fx.wav', 'timeline.json', 'frames.json'].includes(f)) continue;   // written by audio / copied below
    link(path.join(DST, 'assets', f), path.join('../../../assets', f));
  }
  // a variant with its own prepare (a longer timeline: real frames/cam) keeps its frames.json, or its prepare would
  // trust the short's camKey and skip re-extracting its stale frames after a cut change
  const own = (() => { try { return !fs.lstatSync(path.join(DST, 'frames/cam')).isSymbolicLink(); } catch { return false; } })();
  for (const f of ['timeline.json', ...(own ? [] : ['frames.json'])]) fs.copyFileSync(path.join(SRC, 'assets', f), path.join(DST, 'assets', f));
  for (const f of fs.readdirSync(path.join(SRC, 'source'))) if (f !== 'spec.js') link(path.join(DST, 'source', f), path.join('../../../source', f));
  link(path.join(DST, 'frames/cam'), '../../../frames/cam');
  fs.writeFileSync(path.join(DST, 'source/spec.js'), `window.HOOK = '${h}';\n` + fs.readFileSync(path.join(SRC, 'source/spec.js'), 'utf8'));
  fs.writeFileSync(path.join(DST, 'variant.json'), JSON.stringify({ platform: id, hook: h, from, generatedAt: new Date().toISOString() }, null, 2) + '\n');
  console.log(DST);
});
