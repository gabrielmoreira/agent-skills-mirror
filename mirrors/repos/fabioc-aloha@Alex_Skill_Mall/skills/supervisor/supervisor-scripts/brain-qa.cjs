#!/usr/bin/env node
/**
 * brain-qa.cjs — deterministic frontmatter validation + semantic-review priority list
 *
 * Two jobs:
 *   1. Deterministic: validate every instruction/skill in Supervisor and Edition has
 *      well-formed YAML frontmatter with the required fields. Exit non-zero on failure.
 *   2. Priority list: sort files by `lastReviewed` age and emit a queue ordered oldest-first.
 *      The queue is for human/semantic review (Cardinal Rule 3: evolve CT with evidence).
 *
 * Usage:
 *   node scripts/brain-qa.cjs                  # full report, both repos, exit 1 on hard failures
 *   node scripts/brain-qa.cjs --quiet          # only print failures and queue head
 *   node scripts/brain-qa.cjs --queue-only     # skip deterministic checks, just print queue
 *   node scripts/brain-qa.cjs --json           # machine-readable output
 *   node scripts/brain-qa.cjs --stale-days 90  # threshold for "stale" tag (default 90)
 *   node scripts/brain-qa.cjs --top 20         # limit queue display (default 50)
 */

const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const CONFIG = JSON.parse(fs.readFileSync(path.join(__dirname, 'repos.config.json'), 'utf8'));

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
const args = process.argv.slice(2);
const opts = {
    quiet: args.includes('--quiet'),
    json: args.includes('--json'),
    queueOnly: args.includes('--queue-only'),
    staleDays: 90,
    top: 50,
};
for (let i = 0; i < args.length; i++) {
    if (args[i] === '--stale-days') opts.staleDays = parseInt(args[++i], 10);
    if (args[i] === '--top') opts.top = parseInt(args[++i], 10);
}

// ---------------------------------------------------------------------------
// Targets
// ---------------------------------------------------------------------------
const targets = [
    { repo: 'Supervisor', root: REPO_ROOT },
    { repo: 'Edition', root: path.resolve(REPO_ROOT, CONFIG.siblings.edition.path) },
];

function listFiles(repoRoot) {
    const out = [];
    const dirs = [
        path.join(repoRoot, '.github', 'instructions'),
        path.join(repoRoot, '.github', 'skills'),
    ];
    for (const dir of dirs) {
        if (!fs.existsSync(dir)) continue;
        walk(dir, out);
    }
    return out.filter(f =>
        f.endsWith('.instructions.md') || /[\\/]SKILL\.md$/i.test(f)
    );
}

function walk(dir, acc) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full, acc);
        else if (entry.isFile() && entry.name.endsWith('.md')) acc.push(full);
    }
}

// ---------------------------------------------------------------------------
// Frontmatter parser (minimal YAML — enough for our schema)
// ---------------------------------------------------------------------------
function parseFrontmatter(content) {
    if (!content.startsWith('---')) return { ok: false, reason: 'no frontmatter delimiter' };
    const lines = content.split(/\r?\n/);
    let end = -1;
    for (let i = 1; i < lines.length; i++) {
        if (lines[i] === '---') { end = i; break; }
    }
    if (end < 0) return { ok: false, reason: 'unclosed frontmatter' };

    const fm = {};
    for (let i = 1; i < end; i++) {
        const line = lines[i];
        if (!line.trim() || line.trim().startsWith('#')) continue;
        const m = line.match(/^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$/);
        if (!m) continue; // skip continuation/list lines — we only need top-level scalars
        let [, key, value] = m;
        value = value.trim().replace(/^["'](.*)["']$/, '$1');
        fm[key] = value;
    }
    return { ok: true, fm, headerEnd: end };
}

// ---------------------------------------------------------------------------
// Deterministic schema
// ---------------------------------------------------------------------------
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function validate(file, fm) {
    const errors = [];
    const warnings = [];
    const isInstruction = file.endsWith('.instructions.md');
    const isSkill = /SKILL\.md$/i.test(file);

    if (!fm.description) errors.push('missing description');

    if (isInstruction) {
        if (!fm.applyTo && !fm.application) {
            errors.push('instruction missing applyTo or application');
        }
    }

    if (!fm.lastReviewed) {
        errors.push('missing lastReviewed (run S2 backfill or add manually)');
    } else if (!ISO_DATE.test(fm.lastReviewed)) {
        errors.push(`lastReviewed not ISO YYYY-MM-DD: "${fm.lastReviewed}"`);
    }

    if (fm.currency && !ISO_DATE.test(fm.currency)) {
        warnings.push(`currency not ISO YYYY-MM-DD: "${fm.currency}"`);
    }

    return { errors, warnings };
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------
const today = new Date();
const results = { hardFailures: [], warnings: [], queue: [], counts: {} };

for (const target of targets) {
    const files = listFiles(target.root);
    results.counts[target.repo] = files.length;

    for (const file of files) {
        const rel = path.relative(target.root, file).replace(/\\/g, '/');
        const content = fs.readFileSync(file, 'utf8');
        const parsed = parseFrontmatter(content);

        if (!parsed.ok) {
            results.hardFailures.push({ repo: target.repo, file: rel, error: parsed.reason });
            continue;
        }

        const { errors, warnings } = validate(file, parsed.fm);
        for (const e of errors) results.hardFailures.push({ repo: target.repo, file: rel, error: e });
        for (const w of warnings) results.warnings.push({ repo: target.repo, file: rel, warning: w });

        // Build queue entry (always — even if validation has soft issues, we still want a
        // priority slot. Hard failures with no lastReviewed are surfaced separately.)
        let ageDays = null;
        if (parsed.fm.lastReviewed && ISO_DATE.test(parsed.fm.lastReviewed)) {
            const lr = new Date(parsed.fm.lastReviewed + 'T00:00:00Z');
            ageDays = Math.floor((today - lr) / (1000 * 60 * 60 * 24));
        }
        results.queue.push({
            repo: target.repo,
            file: rel,
            lastReviewed: parsed.fm.lastReviewed || null,
            ageDays,
            stale: ageDays !== null && ageDays >= opts.staleDays,
            type: file.endsWith('.instructions.md') ? 'instruction' : 'skill',
        });
    }
}

// Sort queue oldest-first; null lastReviewed pinned to top (highest priority)
results.queue.sort((a, b) => {
    if (a.ageDays === null && b.ageDays !== null) return -1;
    if (b.ageDays === null && a.ageDays !== null) return 1;
    return (b.ageDays ?? 0) - (a.ageDays ?? 0);
});

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------
if (opts.json) {
    process.stdout.write(JSON.stringify(results, null, 2) + '\n');
    process.exit(results.hardFailures.length > 0 ? 1 : 0);
}

const log = (...a) => { if (!opts.quiet) console.log(...a); };

if (!opts.queueOnly) {
    log('=== brain-qa: deterministic check ===');
    log(`Supervisor files: ${results.counts.Supervisor}`);
    log(`Edition files:    ${results.counts.Edition}`);
    log('');

    if (results.hardFailures.length === 0) {
        log('OK: no hard failures');
    } else {
        console.log(`HARD FAILURES (${results.hardFailures.length}):`);
        for (const f of results.hardFailures) {
            console.log(`  [${f.repo}] ${f.file}: ${f.error}`);
        }
    }

    if (results.warnings.length > 0 && !opts.quiet) {
        log('');
        log(`WARNINGS (${results.warnings.length}):`);
        for (const w of results.warnings) {
            log(`  [${w.repo}] ${w.file}: ${w.warning}`);
        }
    }
    log('');
}

// Priority queue
const stale = results.queue.filter(q => q.stale || q.ageDays === null);
console.log('=== semantic review queue (oldest first) ===');
console.log(`Threshold: >=${opts.staleDays} days. Stale items: ${stale.length} / ${results.queue.length}.`);
console.log('');
const head = results.queue.slice(0, opts.top);
const w1 = Math.max(...head.map(q => q.repo.length));
const w2 = Math.max(...head.map(q => q.file.length));
console.log(`${'AGE'.padStart(5)}  ${'REPO'.padEnd(w1)}  TYPE         FILE`);
for (const q of head) {
    const age = q.ageDays === null ? '  ?  ' : String(q.ageDays).padStart(5);
    const tag = q.stale ? '*' : ' ';
    console.log(`${age}${tag} ${q.repo.padEnd(w1)}  ${q.type.padEnd(11)}  ${q.file}`);
}
if (results.queue.length > opts.top) {
    console.log(`... ${results.queue.length - opts.top} more (use --top N to extend)`);
}

process.exit(results.hardFailures.length > 0 ? 1 : 0);
