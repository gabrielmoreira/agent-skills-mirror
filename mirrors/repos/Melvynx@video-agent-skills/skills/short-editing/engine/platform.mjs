// Where the tools live on this machine, macOS or Windows: ffmpeg, ffprobe, Chrome, the face and person-matte helpers.
// The one-command installer puts portable copies in <project>/.runtime (bin/ffmpeg, browsers/, models/, runtime.json).
// Order for each tool: its env var (FFMPEG_PATH, FFPROBE_PATH, CHROME_PATH), then the portable copy, then the PATH.
// Vision: Apple Vision binaries on a Mac (prebuilt universal in bin/darwin/, else compiled once with swiftc), MediaPipe
// in headless Chrome everywhere else (vision-web.mjs). SHORT_EDITING_VISION=web forces MediaPipe, e.g. to test it on a Mac.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const ENGINE = path.dirname(fileURLToPath(import.meta.url));
export const IS_MAC = process.platform === 'darwin', IS_WIN = process.platform === 'win32';
const EXE = IS_WIN ? '.exe' : '';
const exists = f => { try { return fs.existsSync(f); } catch { return false; } };

// <dir>/.runtime with a runtime.json, in the skill's folder or a parent (project install), else the cwd or a parent
function findRuntime() {
  if (process.env.SHORT_EDITING_RUNTIME) return path.resolve(process.env.SHORT_EDITING_RUNTIME);
  for (const start of [ENGINE, process.cwd()])
    for (let d = path.resolve(start); ; d = path.dirname(d)) {
      if (exists(path.join(d, '.runtime', 'runtime.json'))) return path.join(d, '.runtime');
      if (d === path.dirname(d)) break;
    }
  const def = path.join(os.homedir(), 'video-editing', '.runtime');
  return exists(path.join(def, 'runtime.json')) ? def : null;
}
export const RUNTIME = findRuntime();

export function bin(name) {
  const env = process.env[`${name.toUpperCase()}_PATH`];
  if (env) return env;
  const local = RUNTIME && path.join(RUNTIME, 'bin', name + EXE);
  return local && exists(local) ? local : name;
}
export const FFMPEG = bin('ffmpeg'), FFPROBE = bin('ffprobe');

// A Chromium with WebCodecs: Chrome, else Edge (always there on Windows), Brave, Chromium, else the portable headless shell
export function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const H = os.homedir(), L = process.env.LOCALAPPDATA || path.join(H, 'AppData', 'Local');
  const PF = process.env.PROGRAMFILES || 'C:\\Program Files', PF86 = process.env['PROGRAMFILES(X86)'] || 'C:\\Program Files (x86)';
  const mac = app => [`/Applications/${app}.app/Contents/MacOS/${app}`, path.join(H, `Applications/${app}.app/Contents/MacOS/${app}`)];
  const list = IS_MAC ? ['Google Chrome', 'Microsoft Edge', 'Brave Browser', 'Chromium'].flatMap(mac)
    : IS_WIN ? [path.join(PF, 'Google\\Chrome\\Application\\chrome.exe'), path.join(PF86, 'Google\\Chrome\\Application\\chrome.exe'),
      path.join(L, 'Google\\Chrome\\Application\\chrome.exe'), path.join(PF86, 'Microsoft\\Edge\\Application\\msedge.exe'),
      path.join(PF, 'Microsoft\\Edge\\Application\\msedge.exe'), path.join(PF, 'BraveSoftware\\Brave-Browser\\Application\\brave.exe')]
    : ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/microsoft-edge'];
  return list.find(exists) || headlessShell() || list[0];
}
// chrome-headless-shell installed by the installer (playwright layout) in <runtime>/browsers when no browser was found
function headlessShell() {
  const root = RUNTIME && path.join(RUNTIME, 'browsers');
  if (!root || !exists(root)) return null;
  for (const d of fs.readdirSync(root).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse())
    for (const sub of fs.readdirSync(path.join(root, d))) {
      const f = path.join(root, d, sub, 'chrome-headless-shell' + EXE);
      if (exists(f)) return f;
    }
  return null;
}
export const CHROME = findChrome();

// Low priority for one child: `nice` on macOS and Linux, nothing to wrap on Windows (the process priority is inherited)
export const niced = (cmd, args) => IS_WIN ? [cmd, args] : ['nice', ['-n', '10', cmd, ...args]];
// --eco: background QoS on macOS (efficiency cores), lowest priority elsewhere
export function eco() {
  if (IS_MAC) try { execFileSync('taskpolicy', ['-b', '-p', String(process.pid)]); return; } catch {}
  try { os.setPriority(0, os.constants.priority.PRIORITY_LOW); } catch {}
}

let encoders;
export const hasEncoder = name => new RegExp(`\\b${name}\\b`).test(encoders ??= (() => {
  try { return execFileSync(FFMPEG, ['-hide_banner', '-encoders'], { stdio: ['ignore', 'pipe', 'ignore'] }).toString(); } catch { return ''; }
})());
// H.264 output args: the Apple hardware encoder at the given bitrate when ffmpeg has it, else x264 at a matching quality
export function h264(bitrate, maxrate) {
  if (hasEncoder('h264_videotoolbox')) return ['-c:v', 'h264_videotoolbox', '-b:v', bitrate, ...(maxrate ? ['-maxrate', maxrate] : [])];
  return ['-c:v', 'libx264', '-preset', 'fast', '-crf', parseFloat(bitrate) <= 6 ? '23' : '18'];
}

export const CACHE = IS_MAC ? path.join(os.homedir(), 'Library/Caches/short-editing')
  : IS_WIN ? path.join(process.env.LOCALAPPDATA || os.tmpdir(), 'short-editing') : path.join(os.homedir(), '.cache/short-editing');
const hash = f => crypto.createHash('md5').update(fs.readFileSync(f)).digest('hex').slice(0, 12);
// xcode-select -p first: a bare xcrun on a Mac without the Command Line Tools opens an install dialog
const hasSwiftc = () => IS_MAC && spawnSync('xcode-select', ['-p'], { stdio: 'ignore' }).status === 0 && spawnSync('xcrun', ['--find', 'swiftc'], { stdio: 'ignore' }).status === 0;

// A Swift helper as a native binary: the prebuilt universal one shipped next to it (bin/darwin/<name>, with
// <name>.hash = the source it was built from), else compiled once into the cache, else the prebuilt one even if older.
export function swiftTool(src) {
  if (!IS_MAC) return null;
  const name = path.basename(src, '.swift'), h = hash(src), pre = path.join(path.dirname(src), 'bin', 'darwin', name);
  const preHash = exists(pre + '.hash') ? fs.readFileSync(pre + '.hash', 'utf8').trim() : null;
  if (exists(pre) && preHash === h) return { cmd: pre, id: h };
  const out = path.join(CACHE, `${name}-${h}`);
  if (exists(out)) return { cmd: out, id: h };
  if (hasSwiftc()) {
    fs.mkdirSync(CACHE, { recursive: true }); console.error(`compiling ${name}.swift (once)`);
    execFileSync('xcrun', ['swiftc', '-O', src, '-o', out + '.tmp'], { stdio: ['ignore', 'ignore', 'inherit'] }); fs.renameSync(out + '.tmp', out);
    return { cmd: out, id: h };
  }
  return exists(pre) ? { cmd: pre, id: preHash || h } : null;
}

// faces: `<cmd> <camDir> <out.json>`, matte: `<cmd> <camDir> <outDir> <jobFile>` (same contract on both paths)
export function visionTool(name) {
  const force = process.env.SHORT_EDITING_VISION === 'web';
  const apple = !force && swiftTool(path.join(ENGINE, `${name}.swift`));
  if (apple) return { cmd: apple.cmd, args: [], id: apple.id, web: false };
  return { cmd: process.execPath, args: [path.join(ENGINE, 'vision-web.mjs'), name], id: 'web1', web: true };
}

// The codex CLI as a spawnable command: on Windows npm installs a .cmd shim that spawn() cannot run without a shell,
// so run its JS entry with this node instead (no shell, no quoting of the prompt)
export function codexCmd() {
  if (!IS_WIN) return ['codex', []];
  const roots = [process.env.APPDATA && path.join(process.env.APPDATA, 'npm'), path.dirname(process.execPath)].filter(Boolean);
  try { roots.push(...execFileSync('where', ['codex'], { stdio: ['ignore', 'pipe', 'ignore'] }).toString().split(/\r?\n/).filter(Boolean).map(f => path.dirname(f))); } catch {}
  for (const r of roots) {
    const js = path.join(r, 'node_modules', '@openai', 'codex', 'bin', 'codex.js');
    if (exists(js)) return [process.execPath, [js]];
  }
  return ['codex', []];
}
