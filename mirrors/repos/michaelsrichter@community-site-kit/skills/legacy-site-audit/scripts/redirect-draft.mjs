#!/usr/bin/env node
// Draft a legacy-URL → new-URL map from a crawl, using ordered regex rules.
//
//   node redirect-draft.mjs --crawl audit/crawl.json --rules redirect-rules.json --out legacy-redirects.json
//
// redirect-rules.json: [{ "match": "^/index\\.php/events_archive/([^/]+)/?$", "to": "/events/$1/" }, ...]
// The first matching rule wins; matching is done on pathname + search. Unmatched URLs map to "/" and are
// listed in <out>.review.md so a person can decide.
import { readFileSync, writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
const get = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i >= 0 ? args[i + 1] : d;
};
const crawlPath = get('crawl', 'audit/crawl.json');
const rulesPath = get('rules');
const out = get('out', 'legacy-redirects.json');
if (!rulesPath) {
  console.error('Usage: node redirect-draft.mjs --crawl audit/crawl.json --rules redirect-rules.json --out legacy-redirects.json');
  process.exit(1);
}
const crawl = JSON.parse(readFileSync(crawlPath, 'utf8'));
const rules = JSON.parse(readFileSync(rulesPath, 'utf8')).map((r) => ({ ...r, re: new RegExp(r.match, r.flags ?? 'i') }));

const seen = new Set();
const map = [];
const review = [];
for (const p of crawl.pages) {
  if (p.status !== 200 && !p.redirect) continue;
  const u = new URL(p.url);
  const from = u.pathname + u.search;
  if (seen.has(from) || from === '/') continue;
  seen.add(from);
  const rule = rules.find((r) => r.re.test(from));
  if (rule) {
    const to = from.replace(rule.re, rule.to).replace(/\?.*$/, '');
    map.push({ from, to, rule: rule.name ?? rule.match, title: p.title ?? '' });
  } else {
    map.push({ from, to: '/', rule: 'fallback', title: p.title ?? '' });
    review.push(`- ${from}${p.title ? ` — "${p.title}"` : ''}`);
  }
}
map.sort((a, b) => a.from.localeCompare(b.from));
writeFileSync(out, JSON.stringify(map, null, 2) + '\n');
const byRule = new Map();
for (const m of map) byRule.set(m.rule, (byRule.get(m.rule) || 0) + 1);
writeFileSync(
  out.replace(/\.json$/, '') + '.review.md',
  [`# Redirects needing review`, ``, `${review.length} of ${map.length} old URLs matched no rule and point to "/".`, ``, `## Counts by rule`, ``, ...[...byRule].map(([r, n]) => `- \`${r}\`: ${n}`), ``, `## Unmatched`, ``, ...review].join('\n') + '\n',
);
console.log(`${map.length} redirects written to ${out}; ${review.length} need review.`);
