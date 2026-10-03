#!/usr/bin/env node
// Keep package-lock.json files pointing at the public npm registry.
//
//   node scripts/normalize-lockfile.mjs          rewrite mirror URLs to https://registry.npmjs.org/
//   node scripts/normalize-lockfile.mjs --check  fail if any lockfile uses another registry (CI)
//
// Machines that install through a private npm mirror (company proxies, Azure Artifacts, Artifactory)
// write that mirror's URLs into the lockfile. In a public repository those URLs leak internal hosts,
// break Dependabot ("private_source_authentication_failure") and can break installs for other people.
// The tarballs and integrity hashes are identical, so only the host part changes. npm on a machine with a
// mirror still installs through the mirror (npm's default replace-registry-host=npmjs).
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

// Works on the repo in the current folder (the starter also ships this as scripts/normalize-lockfile.mjs).
const root = process.cwd();
const PUBLIC = 'https://registry.npmjs.org/';

/** Rewrites a mirror tarball URL to the public registry, or returns undefined if it is not a mirror URL. */
export function toPublicUrl(url) {
  if (url.startsWith(PUBLIC)) return url;
  // Azure Artifacts: https://<org>.pkgs.visualstudio.com/<project>/_packaging/<feed>/npm/registry/<pkg>/-/<file>.tgz
  //                  https://pkgs.dev.azure.com/<org>/<project>/_packaging/<feed>/npm/registry/<pkg>/-/<file>.tgz
  // Artifactory/Nexus/Verdaccio and most proxies: https://<host>/<prefix…>/<pkg>/-/<file>.tgz
  const m = url.match(/^https?:\/\/[^/]+\/(?:.*?\/npm\/registry\/|(?:.*?\/)?(?=@[^/]+\/[^/]+\/-\/|[^/@]+\/-\/))(.+\/-\/[^/]+\.tgz)$/);
  return m ? PUBLIC + m[1] : undefined;
}

const files = ['package-lock.json', join('api', 'package-lock.json')].map((f) => join(root, f)).filter(existsSync);
const check = process.argv.includes('--check');
let problems = 0;
for (const file of files) {
  const text = readFileSync(file, 'utf8');
  let changed = 0;
  const out = text.replace(/("resolved":\s*")([^"]+)(")/g, (all, a, url, b) => {
    if (url.startsWith(PUBLIC)) return all;
    const pub = toPublicUrl(url);
    if (!pub) return all;
    changed++;
    return a + pub + b;
  });
  const rel = file.slice(root.length + 1);
  if (check) {
    if (changed) {
      problems += changed;
      console.error(`✗ ${rel}: ${changed} package URL(s) point at a private npm mirror. Run: node scripts/normalize-lockfile.mjs`);
    } else console.log(`✓ ${rel}`);
  } else if (changed) {
    writeFileSync(file, out);
    console.log(`${rel}: ${changed} URL(s) rewritten to ${PUBLIC}`);
  } else console.log(`${rel}: already uses ${PUBLIC}`);
}
if (problems) process.exit(1);
