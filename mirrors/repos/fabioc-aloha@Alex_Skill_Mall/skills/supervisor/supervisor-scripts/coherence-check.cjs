#!/usr/bin/env node
/**
 * coherence-check.cjs
 *
 * Cross-repo coherence sweep between Alex_ACT_Edition (brain) and
 * Alex_Skill_Mall (marketplace). Reads scripts/repos.config.json to
 * locate siblings, then performs:
 *
 *   Check 1 — Broken references: any github.com URL or known store
 *             name in Edition/.github/**\/*.md that is NOT in the
 *             current Mall STORES.md / CATALOG.md.
 *
 *   Check 2 — Tag mismatch (partial): if Edition tags a URL as
 *             "primary" or "first-party", verify the Mall lists it
 *             in a First-Party / Primary section heading.
 *
 * Semantic checks (e.g., deprecated install snippets) are out of scope
 * for the mechanical script — those are flagged in the audit report
 * by the /audit-coherence prompt + coherence-audit skill.
 *
 * Exit codes:
 *   0 — clean
 *   1 — one or more hard violations
 *   2 — config or fixture problem
 *
 * @inheritance master-only
 * @currency 2026-04-28
 */

const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(REPO_ROOT, 'scripts', 'repos.config.json');

function loadSiblings() {
    const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
    const ed = cfg.siblings && cfg.siblings.edition && cfg.siblings.edition.path;
    const ml = cfg.siblings && cfg.siblings.mall && cfg.siblings.mall.path;
    if (!ed || !ml) {
        console.error('FATAL: repos.config.json missing edition or mall path');
        process.exit(2);
    }
    const edAbs = path.resolve(REPO_ROOT, ed);
    const mlAbs = path.resolve(REPO_ROOT, ml);
    for (const p of [edAbs, mlAbs]) {
        if (!fs.existsSync(p)) {
            console.error(`FATAL: sibling not found at ${p}`);
            process.exit(2);
        }
    }
    return { edition: edAbs, mall: mlAbs };
}

function walkMarkdown(root) {
    const files = [];
    function recur(dir) {
        let entries;
        try {
            entries = fs.readdirSync(dir, { withFileTypes: true });
        } catch {
            return;
        }
        for (const e of entries) {
            if (e.name.startsWith('.git') || e.name === 'node_modules') continue;
            const full = path.join(dir, e.name);
            if (e.isDirectory()) recur(full);
            else if (e.isFile() && /\.md$/i.test(e.name)) files.push(full);
        }
    }
    recur(root);
    return files;
}

function extractGithubUrls(text) {
    // Match both https://github.com/owner/repo and bare github.com/owner/repo
    // (Mall convention — STORES.md uses `github.com/owner/repo` inside backticks).
    const re = /(?:https?:\/\/)?(?<![\/\w])github\.com\/([\w.-]+)\/([\w.-]+)/gi;
    const urls = new Set();
    let m;
    while ((m = re.exec(text)) !== null) {
        const owner = m[1];
        const repo = m[2].replace(/\.git$/, '').replace(/[.,;:!?)\]`]+$/, '');
        urls.add(`${owner}/${repo}`.toLowerCase());
    }
    return urls;
}

function extractMallCatalog(mallRoot) {
    // Build a set of "owner/repo" identifiers from STORES.md and CATALOG.md
    const targets = ['STORES.md', 'CATALOG.md']
        .map((f) => path.join(mallRoot, f))
        .filter((p) => fs.existsSync(p));
    const catalog = new Set();
    let firstParty = new Set();
    for (const t of targets) {
        const text = fs.readFileSync(t, 'utf8');
        extractGithubUrls(text).forEach((u) => catalog.add(u));
        // Detect First-Party section: collect URLs under a heading that contains "first" or "primary"
        const sections = text.split(/^#{1,6}\s+/m);
        for (const sec of sections) {
            const head = sec.split('\n', 1)[0].toLowerCase();
            if (/first[- ]?party|primary|core/.test(head)) {
                extractGithubUrls(sec).forEach((u) => firstParty.add(u));
            }
        }
    }
    return { catalog, firstParty };
}

function scanEdition(editionRoot) {
    // Walk only .github (the brain) — README/CHANGELOG references are out of scope
    const brain = path.join(editionRoot, '.github');
    if (!fs.existsSync(brain)) {
        return { references: new Map(), primaryTags: new Map() };
    }
    const files = walkMarkdown(brain);
    const references = new Map(); // "owner/repo" -> [files]
    const primaryTags = new Map(); // "owner/repo" -> [files] where the URL appears in a "primary" context
    for (const f of files) {
        const text = fs.readFileSync(f, 'utf8');
        const urls = extractGithubUrls(text);
        for (const u of urls) {
            if (!references.has(u)) references.set(u, []);
            references.get(u).push(path.relative(editionRoot, f));
        }
        // Heuristic for "primary": find any line containing "primary" or "first-party" near a URL
        const lines = text.split(/\r?\n/);
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (!/primary|first[- ]?party/i.test(line)) continue;
            // Look at this line and ±1 line
            const window = [lines[i - 1] || '', line, lines[i + 1] || ''].join('\n');
            const wUrls = extractGithubUrls(window);
            for (const u of wUrls) {
                if (!primaryTags.has(u)) primaryTags.set(u, []);
                const arr = primaryTags.get(u);
                const rel = path.relative(editionRoot, f);
                if (!arr.includes(rel)) arr.push(rel);
            }
        }
    }
    return { references, primaryTags };
}

function main() {
    const { edition, mall } = loadSiblings();
    console.log(`coherence-check`);
    console.log(`  edition: ${edition}`);
    console.log(`  mall:    ${mall}\n`);

    const { catalog, firstParty } = extractMallCatalog(mall);
    console.log(`Mall catalog: ${catalog.size} unique GitHub repos (${firstParty.size} in First-Party / Primary sections)`);

    const { references, primaryTags } = scanEdition(edition);
    console.log(`Edition references: ${references.size} unique GitHub repos across .github/\n`);

    // Check 1: broken references
    const broken = [];
    for (const [repo, files] of references) {
        if (!catalog.has(repo)) broken.push({ repo, files });
    }

    // Check 2: tag mismatch
    const tagMismatch = [];
    for (const [repo, files] of primaryTags) {
        if (catalog.has(repo) && !firstParty.has(repo)) {
            tagMismatch.push({ repo, files });
        }
    }

    console.log('=== Check 1: Broken References (hard violations) ===');
    if (broken.length === 0) {
        console.log('  none\n');
    } else {
        for (const b of broken) {
            console.log(`  [BROKEN] ${b.repo}`);
            for (const f of b.files) console.log(`     ↳ ${f}`);
        }
        console.log('');
    }

    console.log('=== Check 2: Tag Mismatch (soft violations) ===');
    if (tagMismatch.length === 0) {
        console.log('  none\n');
    } else {
        for (const t of tagMismatch) {
            console.log(`  [TAG]    ${t.repo} — Edition treats as primary, Mall does not list in First-Party`);
            for (const f of t.files) console.log(`     ↳ ${f}`);
        }
        console.log('');
    }

    const hardCount = broken.length;
    const softCount = tagMismatch.length;
    console.log(`Summary: ${hardCount} hard, ${softCount} soft`);

    if (hardCount > 0) {
        console.error('\nHard violations present — Edition release should not ship until resolved');
        process.exit(1);
    }
    process.exit(0);
}

try {
    main();
} catch (err) {
    console.error('FATAL:', err);
    process.exit(2);
}
