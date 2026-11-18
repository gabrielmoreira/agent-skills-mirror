#!/usr/bin/env node
/**
 * The `open-artifact` command the skill runs. It is the daemon's own command line (vendor/open-artifact.mjs), started
 * with the pieces this skill folder carries, so every artifact, whatever its type, is served by the one local
 * Open Artifact daemon and opens in the same Shell (`/a/<id>`): the type's own page in a frame, with the Shell's
 * title bar, share and export panels, and the type's own comments coming back to the agent.
 *
 *   node scripts/open-artifact.mjs artifact '<json>'           the Artifact tool (also: data '<json>', comments '<json>')
 *   node scripts/open-artifact.mjs open <url|id> [--panel share|export] [--browser]
 *                                                              the page's view_url; --browser opens it in the system browser
 *   node scripts/open-artifact.mjs wait [--timeout <ms>]       wait for comments and requests sent from the pages
 *   node scripts/open-artifact.mjs daemon status | stop
 *   node scripts/open-artifact.mjs help                        the daemon CLI's other commands
 *
 * Who is calling: `OPEN_ARTIFACT_HARNESS` and `OPEN_ARTIFACT_SESSION` when set; in Claude Code the harness is
 * `claude-code` and the session `CLAUDE_CODE_SESSION_ID`; in Codex `codex` and `CODEX_THREAD_ID`; otherwise `cli` and
 * no session (the workspace, the current folder, still owns what is made). A plugin's MCP server and hooks pass
 * `--harness` themselves.
 *
 * In a repository checkout without vendor/ (before `node scripts/build-skill.mjs`), the daemon runs from source.
 */
import { spawn, spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const skillDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const vendor = join(skillDir, 'vendor');
const vendoredBin = join(vendor, 'open-artifact.mjs');
const sourceBin = resolve(skillDir, '..', '..', 'packages', 'daemon', 'src', 'bin', 'open-artifact.ts');
const bin = existsSync(vendoredBin) ? vendoredBin : sourceBin;

if (!existsSync(bin)) {
  process.stderr.write(`open-artifact: ${vendoredBin} is missing; build the skill with node scripts/build-skill.mjs.\n`);
  process.exit(1);
}

// ---------------------------------------------------------------- the daemon's environment

const env = process.env;
/** Points a daemon variable at a vendored folder, unless the environment already names one. */
const folder = (name, dir) => {
  if (!env[name] && existsSync(dir)) env[name] = dir;
};
// The daemon this command starts when none runs (one per computer: if a harness started it first, that one is used).
if (!env.OPEN_ARTIFACT_DAEMON_BIN) env.OPEN_ARTIFACT_DAEMON_BIN = bin;
if (bin === vendoredBin) {
  folder('OPEN_ARTIFACT_SHELL_DIR', join(vendor, 'shell'));
  folder('OPEN_ARTIFACT_HOME_DIR', join(vendor, 'home'));
  folder('OPEN_ARTIFACT_BUILTIN_TYPES', join(vendor, 'artifact-types'));
  folder('OPEN_ARTIFACT_HARNESS_PROFILES', join(vendor, 'harnesses'));
}

// The plugin this skill came in (`<plugin>/skills/open-artifact`): an agent app may start the plugin's MCP server and
// hooks in that folder, which is never where the person works.
const pluginDir = resolve(skillDir, '..', '..');
const PLUGIN_FILES = ['plugin.json', '.claude-plugin', '.cursor-plugin', '.mcp.json', 'mcp.json', 'mcp_config.json'];
if (!env.OPEN_ARTIFACT_PLUGIN_DIR && basename(dirname(skillDir)) === 'skills' && PLUGIN_FILES.some((name) => existsSync(join(pluginDir, name)))) {
  env.OPEN_ARTIFACT_PLUGIN_DIR = pluginDir;
}

// ---------------------------------------------------------------- who is calling

// The harness, from the variables each sets in the commands its agent runs, and its session id from the same.
const harnesses = [
  ['claude-code', 'CLAUDECODE', 'CLAUDE_CODE_SESSION_ID'],
  ['codex', 'CODEX_THREAD_ID', 'CODEX_THREAD_ID'],
];
// A plugin's MCP server and hooks name their harness with `--harness`: that wins over the variables, so an app started
// from inside another agent's session (and holding its variables) does not take that session for its own.
const named = process.argv.indexOf('--harness');
if (named > 1 && process.argv[named + 1] && !env.OPEN_ARTIFACT_HARNESS) env.OPEN_ARTIFACT_HARNESS = process.argv[named + 1];
for (const [name, marker, sessionVariable] of harnesses) {
  if (env.OPEN_ARTIFACT_HARNESS ? env.OPEN_ARTIFACT_HARNESS !== name : !env[marker]) continue;
  env.OPEN_ARTIFACT_HARNESS = name;
  if (!env.OPEN_ARTIFACT_SESSION && env[sessionVariable]) env.OPEN_ARTIFACT_SESSION = env[sessionVariable];
  break;
}

// ---------------------------------------------------------------- commands

const args = process.argv.slice(2);

/** Takes `--name <value>` (or a bare `--name`, as `true`) out of the arguments. */
function take(name, hasValue) {
  const i = args.indexOf(`--${name}`);
  if (i < 0) return undefined;
  const value = hasValue ? args[i + 1] : true;
  args.splice(i, hasValue ? 2 : 1);
  return value;
}

/** Opens a link in the system browser. */
function browse(url) {
  const [command, argv] =
    process.platform === 'darwin' ? ['open', [url]] : process.platform === 'win32' ? ['cmd', ['/c', 'start', '""', url]] : ['xdg-open', [url]];
  try {
    const child = spawn(command, argv, { detached: true, stdio: 'ignore', windowsHide: true });
    child.on('error', () => undefined);
    child.unref();
    return true;
  } catch {
    return false;
  }
}

/** `open <url|id> [--panel share|export] [--browser]`: the Artifact tool's open, then the system browser if asked. */
function open() {
  const panel = take('panel', true);
  const browser = take('browser', false);
  const target = args[1];
  if (!target) {
    process.stderr.write('open-artifact: open <open-artifact://artifact/… | art_…> [--panel share|export] [--browser]\n');
    process.exit(1);
  }
  const url = target.startsWith('open-artifact://') ? target : `open-artifact://artifact/${target}`;
  const call = JSON.stringify({ action: 'open', url, ...(panel ? { panel } : {}) });
  const run = spawnSync(process.execPath, [bin, 'artifact', call], { env, encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] });
  let result;
  try {
    result = JSON.parse(run.stdout);
  } catch {
    process.stdout.write(run.stdout ?? '');
    process.exit(run.status ?? 1);
  }
  if (browser && result && !result.error && !result.opened && result.view_url && browse(result.view_url)) {
    result = { ...result, opened: true, opened_in: 'system browser' };
    delete result.next;
  }
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  process.exit(result?.error ? 1 : 0);
}

if (args[0] === 'open') open();
else await import(pathToFileURL(bin).href);
