#!/usr/bin/env node
/**
 * mall-link-check.cjs
 *
 * Mechanical link reachability check for Alex_Skill_Mall.
 * Reads scripts/repos.config.json to locate the sibling Mall repo,
 * extracts URLs from STORES.md and CATALOG.md, and HEAD-checks each.
 *
 * Exit codes:
 *   0 — all links reachable
 *   1 — one or more links unreachable
 *   2 — config or fixture problem (Mall not found, files missing)
 *
 * @inheritance master-only
 * @currency 2026-04-28
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const REPO_ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(REPO_ROOT, 'scripts', 'repos.config.json');
const TIMEOUT_MS = 10000;

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

function extractUrls(text) {
    // Match http(s) URLs AND bare github.com/owner/repo refs (Mall convention).
    // Strip trailing punctuation and common markdown closers.
    const seen = new Set();
    const matches = [];
    const stripTail = (u) => u.replace(/[.,;:!?)\]`>]+$/, '');

    const httpRe = /https?:\/\/[^\s)\]<>"'`]+/g;
    let m;
    while ((m = httpRe.exec(text)) !== null) {
        const url = stripTail(m[0]);
        if (!seen.has(url)) {
            seen.add(url);
            matches.push(url);
        }
    }
    // Bare github.com/owner/repo (no scheme) — common in STORES.md tables/code spans
    const bareRe = /(?<![\/\w])github\.com\/[\w.-]+\/[\w.-]+/g;
    while ((m = bareRe.exec(text)) !== null) {
        const url = 'https://' + stripTail(m[0]);
        if (!seen.has(url)) {
            seen.add(url);
            matches.push(url);
        }
    }
    return matches;
}

function headCheck(url) {
    return new Promise((resolve) => {
        let lib;
        try {
            lib = url.startsWith('https:') ? https : http;
        } catch {
            return resolve({ url, ok: false, status: 'invalid' });
        }
        const req = lib.request(url, { method: 'HEAD', timeout: TIMEOUT_MS }, (res) => {
            // Some servers reject HEAD; treat 405 as a soft pass and try GET? Keep simple here.
            const ok = res.statusCode >= 200 && res.statusCode < 400;
            resolve({ url, ok, status: res.statusCode });
            res.resume();
        });
        req.on('error', (err) => resolve({ url, ok: false, status: err.code || 'error' }));
        req.on('timeout', () => {
            req.destroy();
            resolve({ url, ok: false, status: 'timeout' });
        });
        req.end();
    });
}

async function main() {
    const mall = loadMallPath();
    const targets = ['STORES.md', 'CATALOG.md'].map((f) => path.join(mall, f));
    const missing = targets.filter((t) => !fs.existsSync(t));
    if (missing.length > 0) {
        console.error(`FATAL: missing Mall files: ${missing.join(', ')}`);
        process.exit(2);
    }

    const allUrls = new Set();
    for (const t of targets) {
        extractUrls(fs.readFileSync(t, 'utf8')).forEach((u) => allUrls.add(u));
    }
    const urls = [...allUrls];
    console.log(`mall-link-check: ${urls.length} unique URLs to check`);

    const results = await Promise.all(urls.map(headCheck));
    const failed = results.filter((r) => !r.ok);

    for (const r of results) {
        const tag = r.ok ? 'OK ' : 'FAIL';
        console.log(`  [${tag}] ${r.status}\t${r.url}`);
    }

    console.log(`\nSummary: ${results.length - failed.length}/${results.length} reachable`);
    if (failed.length > 0) {
        console.error(`\n${failed.length} unreachable URL(s) — review for refresh or prune`);
        process.exit(1);
    }
    process.exit(0);
}

main().catch((err) => {
    console.error('FATAL:', err);
    process.exit(2);
});
