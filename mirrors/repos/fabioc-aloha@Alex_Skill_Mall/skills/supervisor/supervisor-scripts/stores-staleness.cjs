#!/usr/bin/env node
/**
 * stores-staleness.cjs
 *
 * Mechanical staleness scan for Alex_Skill_Mall.
 * For each GitHub repo URL in STORES.md, query the GitHub API
 * (or fall back to local heuristics) and flag entries with
 * no recent activity.
 *
 * Activity threshold: 18 months (per staleness-discipline skill).
 *
 * Exit codes:
 *   0 — no stale entries
 *   1 — one or more stale entries flagged
 *   2 — config or fixture problem
 *
 * Note: Uses unauthenticated GitHub API (60 req/hour rate limit).
 * Set GITHUB_TOKEN env var to raise the limit to 5000/hour.
 *
 * @inheritance master-only
 * @currency 2026-04-28
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const REPO_ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(REPO_ROOT, 'scripts', 'repos.config.json');
const STALE_MONTHS = 18;
const TOKEN = process.env.GITHUB_TOKEN || '';

function loadMallPath() {
    const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
    const rel = cfg.siblings && cfg.siblings.mall && cfg.siblings.mall.path;
    if (!rel) {
        console.error('FATAL: repos.config.json missing siblings.mall.path');
        process.exit(2);
    }
    const abs = path.resolve(REPO_ROOT, rel);
    if (!fs.existsSync(abs)) {
        console.error(`FATAL: Mall sibling not found at ${abs}`);
        process.exit(2);
    }
    return abs;
}

function extractGithubRepos(text) {
    // Match both https://github.com/owner/repo and bare github.com/owner/repo
    // (Mall convention — store entries are written as `github.com/owner/repo`)
    const re = /(?:https?:\/\/)?(?<![\/\w])github\.com\/([\w.-]+)\/([\w.-]+)/gi;
    const seen = new Set();
    const repos = [];
    let m;
    while ((m = re.exec(text)) !== null) {
        const owner = m[1];
        const repo = m[2].replace(/\.git$/, '').replace(/[.,;:!?]+$/, '');
        const key = `${owner}/${repo}`;
        if (!seen.has(key)) {
            seen.add(key);
            repos.push({ owner, repo });
        }
    }
    return repos;
}

function ghApi(pathPart) {
    return new Promise((resolve) => {
        const opts = {
            host: 'api.github.com',
            path: pathPart,
            method: 'GET',
            headers: {
                'User-Agent': 'Alex_ACT_Supervisor/stores-staleness',
                Accept: 'application/vnd.github+json',
            },
        };
        if (TOKEN) opts.headers.Authorization = `Bearer ${TOKEN}`;
        const req = https.request(opts, (res) => {
            let body = '';
            res.on('data', (c) => (body += c));
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, json: JSON.parse(body) });
                } catch {
                    resolve({ status: res.statusCode, json: null });
                }
            });
        });
        req.on('error', (err) => resolve({ status: 0, json: null, error: err.code }));
        req.setTimeout(10000, () => {
            req.destroy();
            resolve({ status: 0, json: null, error: 'timeout' });
        });
        req.end();
    });
}

function monthsBetween(iso) {
    if (!iso) return Infinity;
    const then = new Date(iso).getTime();
    const now = Date.now();
    return Math.floor((now - then) / (1000 * 60 * 60 * 24 * 30.44));
}

async function main() {
    const mall = loadMallPath();
    const stores = path.join(mall, 'STORES.md');
    if (!fs.existsSync(stores)) {
        console.error(`FATAL: ${stores} not found`);
        process.exit(2);
    }

    const repos = extractGithubRepos(fs.readFileSync(stores, 'utf8'));
    console.log(`stores-staleness: ${repos.length} GitHub repos to scan (threshold: ${STALE_MONTHS} months)`);
    if (!TOKEN) {
        console.log('  (unauthenticated — limited to 60 req/hour; set GITHUB_TOKEN to raise)');
    }

    const stale = [];
    const failed = [];

    for (const { owner, repo } of repos) {
        const r = await ghApi(`/repos/${owner}/${repo}`);
        if (r.status !== 200 || !r.json) {
            failed.push({ owner, repo, reason: r.error || `HTTP ${r.status}` });
            console.log(`  [SKIP] ${owner}/${repo}: ${r.error || `HTTP ${r.status}`}`);
            continue;
        }
        const archived = !!r.json.archived;
        const pushedMonths = monthsBetween(r.json.pushed_at);
        const isStale = archived || pushedMonths >= STALE_MONTHS;
        const tag = isStale ? 'STALE' : 'OK   ';
        const detail = archived ? 'archived' : `pushed ${pushedMonths}mo ago`;
        console.log(`  [${tag}] ${owner}/${repo} — ${detail}`);
        if (isStale) stale.push({ owner, repo, archived, pushedMonths });
    }

    console.log(`\nSummary: ${stale.length} stale / ${repos.length - stale.length - failed.length} fresh / ${failed.length} unchecked`);

    if (failed.length > 0) {
        console.warn(`\n${failed.length} repo(s) could not be checked — re-run after rate-limit reset or with GITHUB_TOKEN`);
    }
    if (stale.length > 0) {
        console.error(`\n${stale.length} stale entries flagged for staleness-discipline review`);
        process.exit(1);
    }
    process.exit(0);
}

main().catch((err) => {
    console.error('FATAL:', err);
    process.exit(2);
});
