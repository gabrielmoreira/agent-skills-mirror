#!/usr/bin/env node
/**
 * sync-from-master.cjs — pinned-instruction drift checker
 *
 * Supervisor pins a small set of shared-core instructions copied from AlexMaster.
 * They carry `inheritance: inheritable` but Supervisor is NOT a sync-target of
 * AlexMaster's `sync-to-heir.cjs`, so updates do not flow automatically.
 *
 * This script reports drift between the pinned copies here and the originals
 * at sibling path `../AlexMaster/.github/instructions/`. Run it as part of
 * the brain-curation ritual.
 *
 * Usage:
 *   node scripts/sync-from-master.cjs              # report drift
 *   node scripts/sync-from-master.cjs --apply      # copy master -> Supervisor
 *   node scripts/sync-from-master.cjs --diff       # also print unified diffs
 *
 * Exit codes: 0 = in-sync, 1 = drift detected (report mode).
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

// Pinned files: shared-core instructions Supervisor inherits-by-copy from AlexMaster.
// To unpin, delete the entry. To pin a new file, add it here.
const PINNED = [
    'act-pass.instructions.md',
    'epistemic-calibration.instructions.md',
    'pii-memory-filter.instructions.md',
    'system-prompt-skepticism.instructions.md',
    'terminal-command-safety.instructions.md',
    'markdown-mermaid.instructions.md',
    'git-workflow.instructions.md',
    'doc-hygiene.instructions.md',
    'code-review.instructions.md',
    'critical-thinking.instructions.md',
    'problem-framing-audit.instructions.md',
    'mcp-development.instructions.md',
    'release-process.instructions.md',
    'release-management.instructions.md',
    'status-reporting.instructions.md',
];

const args = new Set(process.argv.slice(2));
const APPLY = args.has('--apply');
const SHOW_DIFF = args.has('--diff');

const supDir = path.resolve(__dirname, '..', '.github', 'instructions');
const masterDir = path.resolve(__dirname, '..', '..', 'AlexMaster', '.github', 'instructions');

if (!fs.existsSync(masterDir)) {
    console.error(`ERROR: AlexMaster not found at ${masterDir}`);
    console.error('Expected sibling layout: C:\\Development\\AlexMaster and C:\\Development\\Alex_ACT_Supervisor');
    process.exit(2);
}

function hash(p) {
    return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').slice(0, 12);
}

function lineDiff(a, b) {
    const al = a.split(/\r?\n/);
    const bl = b.split(/\r?\n/);
    const out = [];
    const max = Math.max(al.length, bl.length);
    for (let i = 0; i < max; i++) {
        if (al[i] !== bl[i]) {
            if (al[i] !== undefined) out.push(`  - ${al[i]}`);
            if (bl[i] !== undefined) out.push(`  + ${bl[i]}`);
        }
    }
    return out.slice(0, 40); // cap output
}

let drift = 0;
const results = [];

for (const name of PINNED) {
    const supPath = path.join(supDir, name);
    const masPath = path.join(masterDir, name);
    if (!fs.existsSync(supPath)) {
        results.push({ name, state: 'MISSING-LOCAL' });
        drift++;
        continue;
    }
    if (!fs.existsSync(masPath)) {
        results.push({ name, state: 'MISSING-MASTER' });
        drift++;
        continue;
    }
    const sh = hash(supPath);
    const mh = hash(masPath);
    if (sh === mh) {
        results.push({ name, state: 'IN-SYNC', sup: sh, mas: mh });
    } else {
        results.push({ name, state: 'DRIFTED', sup: sh, mas: mh, supPath, masPath });
        drift++;
    }
}

console.log('=== Pinned instruction drift report ===');
console.log(`Source: ${masterDir}`);
console.log(`Target: ${supDir}`);
console.log('');
for (const r of results) {
    const tag = r.state.padEnd(15);
    console.log(`  ${tag}  ${r.name}${r.sup ? `  (sup=${r.sup} master=${r.mas})` : ''}`);
}
console.log('');

if (drift === 0) {
    console.log(`Summary: ${PINNED.length}/${PINNED.length} in sync`);
    process.exit(0);
}

if (SHOW_DIFF) {
    console.log('=== Diffs ===');
    for (const r of results.filter(x => x.state === 'DRIFTED')) {
        console.log(`\n--- ${r.name} ---`);
        const a = fs.readFileSync(r.supPath, 'utf8');
        const b = fs.readFileSync(r.masPath, 'utf8');
        const lines = lineDiff(a, b);
        if (lines.length === 40) lines.push('  ... (truncated)');
        lines.forEach(l => console.log(l));
    }
    console.log('');
}

if (APPLY) {
    console.log('=== Applying master -> Supervisor ===');
    for (const r of results.filter(x => x.state === 'DRIFTED')) {
        fs.copyFileSync(r.masPath, r.supPath);
        console.log(`  copied: ${r.name}`);
    }
    console.log(`\nApplied: ${results.filter(x => x.state === 'DRIFTED').length} file(s). Re-run without --apply to verify.`);
    process.exit(0);
}

console.log(`Summary: ${drift} drifted of ${PINNED.length} pinned. Run with --diff to inspect, --apply to pull master.`);
process.exit(1);
