#!/usr/bin/env node
/**
 * fleet-inventory.cjs
 *
 * Discover ACT-Edition heirs by scanning for the self-identification marker
 * `.github/.act-heir.json` under a given root (default: parent of this repo).
 * Optionally also reports non-ACT Alex-family repos (have
 * `.github/copilot-instructions.md` but no ACT marker) as migration candidates.
 *
 * Usage:
 *   node scripts/fleet-inventory.cjs                    # ACT heirs only
 *   node scripts/fleet-inventory.cjs --root <path>      # custom scan root
 *   node scripts/fleet-inventory.cjs --json             # emit JSON
 *   node scripts/fleet-inventory.cjs --depth 3          # max scan depth (default 2)
 *   node scripts/fleet-inventory.cjs --include-private  # include heirs that opted out
 *   node scripts/fleet-inventory.cjs --include-non-act  # also list non-ACT Alex repos
 *
 * Read-only. Never modifies a heir's marker.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const args = new Set(process.argv.slice(2));
function argValue(name, fallback) {
    const i = process.argv.indexOf(name);
    return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const REPO_ROOT = path.resolve(__dirname, '..');
const DEFAULT_SCAN_ROOT = path.resolve(REPO_ROOT, '..');
const SCAN_ROOT = path.resolve(argValue('--root', DEFAULT_SCAN_ROOT));
const MAX_DEPTH = parseInt(argValue('--depth', '2'), 10);
const EMIT_JSON = args.has('--json');
const INCLUDE_PRIVATE = args.has('--include-private');
const INCLUDE_NON_ACT = args.has('--include-non-act');

const MARKER_REL = path.join('.github', '.act-heir.json');
const COPILOT_REL = path.join('.github', 'copilot-instructions.md');
const SCHEMA_REQUIRED = ['spec_version', 'edition', 'edition_version', 'heir_id', 'deployed_at'];

// Exclusion list (master / template / mall / self / alpha / backups)
let EXCLUSIONS = { names: [], suffix_patterns: [] };
try {
    const cfg = require('./repos.config.json');
    if (cfg && cfg.inventory_exclusions) {
        EXCLUSIONS.names = (cfg.inventory_exclusions.names || []).map((s) => s.toLowerCase());
        EXCLUSIONS.suffix_patterns = cfg.inventory_exclusions.suffix_patterns || [];
    }
} catch { /* config optional */ }

function isExcluded(folderName) {
    const lower = folderName.toLowerCase();
    if (EXCLUSIONS.names.includes(lower)) return true;
    for (const sfx of EXCLUSIONS.suffix_patterns) {
        if (folderName.endsWith(sfx)) return true;
    }
    return false;
}

function findMarkers(root, depth) {
    const out = [];
    if (!fs.existsSync(root) || depth < 0) return out;
    let entries;
    try {
        entries = fs.readdirSync(root, { withFileTypes: true });
    } catch {
        return out;
    }
    for (const entry of entries) {
        if (!entry.isDirectory()) continue;
        if (entry.name.startsWith('.') && entry.name !== '.') continue;
        if (entry.name === 'node_modules') continue;
        const dir = path.join(root, entry.name);
        const marker = path.join(dir, MARKER_REL);
        if (fs.existsSync(marker)) {
            out.push({ dir, marker });
            continue; // don't recurse into a heir
        }
        if (depth > 0) {
            out.push(...findMarkers(dir, depth - 1));
        }
    }
    return out;
}

/**
 * Find directories with `.github/copilot-instructions.md` but no ACT marker
 * and not in the exclusion list. Only scans the immediate root (depth 0).
 */
function findNonActRepos(root) {
    const out = [];
    if (!fs.existsSync(root)) return out;
    let entries;
    try { entries = fs.readdirSync(root, { withFileTypes: true }); } catch { return out; }
    for (const entry of entries) {
        if (!entry.isDirectory()) continue;
        if (entry.name.startsWith('.')) continue;
        if (entry.name === 'node_modules') continue;
        if (isExcluded(entry.name)) continue;
        const dir = path.join(root, entry.name);
        const hasCopilot = fs.existsSync(path.join(dir, COPILOT_REL));
        const hasMarker = fs.existsSync(path.join(dir, MARKER_REL));
        if (hasCopilot && !hasMarker) out.push({ dir, name: entry.name });
    }
    return out;
}

function gitInfo(dir) {
    const info = { last_commit_at: null, repo_url: '' };
    if (!fs.existsSync(path.join(dir, '.git'))) return info;
    try {
        info.last_commit_at = execSync('git log -1 --format=%cI', { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim() || null;
    } catch { /* not a repo or no commits */ }
    try {
        info.repo_url = execSync('git remote get-url origin', { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    } catch { /* no remote */ }
    return info;
}

function loadMarker(markerPath) {
    try {
        const raw = fs.readFileSync(markerPath, 'utf8');
        const data = JSON.parse(raw);
        const missing = SCHEMA_REQUIRED.filter((k) => !(k in data));
        return { ok: missing.length === 0, data, missing, markerPath };
    } catch (err) {
        return { ok: false, error: err.message, markerPath };
    }
}

function daysSince(iso) {
    if (!iso) return null;
    const t = Date.parse(iso);
    if (Number.isNaN(t)) return null;
    return Math.floor((Date.now() - t) / 86400000);
}

const found = findMarkers(SCAN_ROOT, MAX_DEPTH);
const heirs = [];
const invalid = [];
for (const f of found) {
    const result = loadMarker(f.marker);
    if (!result.ok) {
        invalid.push(result);
        continue;
    }
    const data = result.data;
    const optedOut = data.opt_in && data.opt_in.fleet_inventory === false;
    if (optedOut && !INCLUDE_PRIVATE) continue;
    heirs.push({
        heir_id: data.heir_id,
        heir_name: data.heir_name || data.heir_id,
        edition_version: data.edition_version,
        last_sync_at: data.last_sync_at || data.deployed_at,
        days_since_sync: daysSince(data.last_sync_at || data.deployed_at),
        owner: (data.contact && data.contact.owner) || '',
        repo_url: data.repo_url || '',
        opted_out: !!optedOut,
        path: f.dir,
    });
}

heirs.sort((a, b) => a.heir_id.localeCompare(b.heir_id));

// Discover non-ACT Alex-family repos (always discovered; only emitted/printed when flag set)
const nonActFound = findNonActRepos(SCAN_ROOT);
const nonActRepos = nonActFound.map((f) => {
    const g = gitInfo(f.dir);
    return {
        name: f.name,
        path: f.dir,
        last_commit_at: g.last_commit_at,
        days_since_commit: daysSince(g.last_commit_at),
        repo_url: g.repo_url,
    };
}).sort((a, b) => {
    const ad = a.days_since_commit == null ? Infinity : a.days_since_commit;
    const bd = b.days_since_commit == null ? Infinity : b.days_since_commit;
    if (ad !== bd) return ad - bd; // most recent first
    return a.name.localeCompare(b.name);
});

if (EMIT_JSON) {
    const payload = {
        scan_root: SCAN_ROOT,
        scanned_at: new Date().toISOString(),
        heir_count: heirs.length,
        invalid_count: invalid.length,
        heirs,
        invalid: invalid.map((x) => ({ marker: x.markerPath, missing: x.missing, error: x.error })),
        non_act_count: nonActRepos.length,
    };
    if (INCLUDE_NON_ACT) payload.non_act_repos = nonActRepos;
    process.stdout.write(JSON.stringify(payload, null, 2) + '\n');
    process.exit(0);
}

console.log(`ACT Fleet Inventory`);
console.log(`Scan root: ${SCAN_ROOT}`);
console.log(`Scanned at: ${new Date().toISOString()}`);
console.log('');

if (heirs.length === 0) {
    console.log('  No heirs found. Heirs declare themselves by placing .github/.act-heir.json.');
    console.log(`  Template: ${path.relative(REPO_ROOT, path.join(REPO_ROOT, 'fleet', 'templates', 'act-heir.template.json'))}`);
} else {
    console.log(`Heirs: ${heirs.length}`);
    console.log('');
    const rows = heirs.map((h) => [
        h.heir_id,
        h.edition_version,
        h.days_since_sync == null ? '?' : `${h.days_since_sync}d`,
        h.owner || '-',
        h.opted_out ? 'private' : 'public',
    ]);
    const header = ['heir_id', 'version', 'last-sync', 'owner', 'visibility'];
    const widths = header.map((h, i) => Math.max(h.length, ...rows.map((r) => String(r[i]).length)));
    const fmt = (cols) => cols.map((c, i) => String(c).padEnd(widths[i])).join('  ');
    console.log(fmt(header));
    console.log(widths.map((w) => '-'.repeat(w)).join('  '));
    rows.forEach((r) => console.log(fmt(r)));
}

if (invalid.length > 0) {
    console.log('');
    console.log(`Invalid markers: ${invalid.length}`);
    for (const v of invalid) {
        console.log(`  ${v.markerPath}`);
        if (v.missing && v.missing.length) console.log(`    missing: ${v.missing.join(', ')}`);
        if (v.error) console.log(`    error: ${v.error}`);
    }
}

if (INCLUDE_NON_ACT) {
    console.log('');
    console.log(`Non-ACT Alex repos: ${nonActRepos.length} (have copilot-instructions.md, no ACT marker)`);
    if (nonActRepos.length > 0) {
        const rows = nonActRepos.map((r) => [
            r.name,
            r.days_since_commit == null ? '?' : `${r.days_since_commit}d`,
            r.repo_url || '-',
        ]);
        const header = ['repo', 'last-commit', 'remote'];
        const widths = header.map((h, i) => Math.max(h.length, ...rows.map((r) => String(r[i]).length)));
        const fmt = (cols) => cols.map((c, i) => String(c).padEnd(widths[i])).join('  ');
        console.log('');
        console.log(fmt(header));
        console.log(widths.map((w) => '-'.repeat(w)).join('  '));
        rows.forEach((r) => console.log(fmt(r)));
    }
}

console.log('');
const nonActSummary = INCLUDE_NON_ACT ? `, ${nonActRepos.length} non-ACT repo(s)` : (nonActRepos.length > 0 ? `, ${nonActRepos.length} non-ACT repo(s) [run with --include-non-act to list]` : '');
console.log(`Summary: ${heirs.length} heir(s), ${invalid.length} invalid marker(s)${nonActSummary}`);
