#!/usr/bin/env node
// Verification of the hard, checkable rules in this skill that
// `npm run lint` / `npm run build` do not catch on their own — a wrong
// react-router-dom import, a hardcoded basename, an inline style prop, a
// stray lightning/*-or-@wire import, or leftover template boilerplate can
// all lint and build clean while breaking at runtime or shipping unfinished
// branding.
//
// Usage: node verify-rules.mjs <file-or-dir> [<file-or-dir> ...]
//   Pass the specific files you edited, or the bundle's src/ directory (and
//   its index.html) to check everything.
//
// Always invoke via `node` (never as a bare executable, and never via a
// shell-specific tool like grep/sed) so this works on Windows
// cmd/PowerShell as well as macOS/Linux/Git Bash. Quote path arguments so
// Windows paths and spaces survive the shell.
//
// Exit 0 if no violations are found.
// Exit 1 with every violation listed (rule + matching file paths) if any
// are found — fix them before considering the task complete, even if lint
// and build passed.

import fs from "node:fs";
import path from "node:path";

const INCLUDE_EXT = new Set([".ts", ".tsx", ".js", ".jsx", ".html"]);
const EXCLUDE_DIRS = new Set(["node_modules", "dist", "build"]);

const RULES = [
  {
    label: 'import from "react-router-dom" (must be "react-router")',
    pattern: /from\s+['"]react-router-dom['"]/,
  },
  {
    label: "a hardcoded basename literal (must derive from <base href> at runtime)",
    pattern: /basename:\s*['"][/A-Za-z0-9_-]+['"]/,
  },
  {
    label: "an inline style={{...}} prop (Tailwind utility classes only)",
    pattern: /style=\{\{/,
  },
  {
    label: "a forbidden lightning/* import or @wire usage (LWC-only)",
    pattern: /from\s+['"]lightning\/|@wire/,
  },
  {
    label: "leftover boilerplate branding (<title>React App</title> / Vite + React)",
    pattern: /<title>[^<]*React App[^<]*<\/title>|Vite\s*\+\s*React/,
  },
];

const targets = process.argv.slice(2);

if (targets.length === 0) {
  console.error("ERROR: verify-rules.mjs requires at least one file or directory argument");
  process.exit(1);
}

for (const p of targets) {
  if (!fs.existsSync(p)) {
    console.error(`ERROR: path does not exist: ${p}`);
    process.exit(1);
  }
}

function collectFiles(target, out) {
  const stat = fs.statSync(target);
  if (stat.isDirectory()) {
    const base = path.basename(target);
    if (EXCLUDE_DIRS.has(base)) return;
    for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
      collectFiles(path.join(target, entry.name), out);
    }
    return;
  }
  if (stat.isFile() && INCLUDE_EXT.has(path.extname(target))) {
    out.push(target);
  }
}

const files = [];
for (const t of targets) {
  collectFiles(t, files);
}

let found = false;

for (const rule of RULES) {
  const hits = [];
  for (const file of files) {
    let content;
    try {
      content = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }
    if (rule.pattern.test(content)) {
      hits.push(file);
    }
  }
  if (hits.length > 0) {
    found = true;
    console.error(`ERROR: ${rule.label} found in:`);
    for (const hit of hits) {
      console.error(`  - ${hit}`);
    }
  }
}

if (found) {
  process.exit(1);
}

console.log(`SUCCESS: No hard-rule violations found in: ${targets.join(" ")}`);
process.exit(0);
