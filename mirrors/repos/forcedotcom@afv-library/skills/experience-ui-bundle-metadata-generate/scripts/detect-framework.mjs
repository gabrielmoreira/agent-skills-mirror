#!/usr/bin/env node
//
// detect-framework.mjs — deterministic UI Bundle framework detector.
//
// Usage: node detect-framework.mjs [ROOT]
//   ROOT  app or uiBundle root to inspect (default: current directory)
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Prints exactly one of the following tokens to stdout, nothing else, and sets
// a matching exit code so callers can branch without parsing:
//   react      (exit 0) — React signals only
//   angular    (exit 0) — Angular signals only
//   ambiguous  (exit 2) — both React and Angular signals present
//   unknown    (exit 3) — neither framework detected
//
// Step 0 of the skill acts on the result: a single framework (exit 0) proceeds;
// `ambiguous` asks the user to disambiguate; `unknown` TERMINATES the workflow
// (no supported framework found — do not guess).

import fs from "node:fs";
import path from "node:path";

const ROOT = process.argv[2] ?? ".";

let angular = false;
let react = false;

// Resolve ROOT to an absolute path when possible (for the angular.json walk-up).
let absRoot = "";
try {
  if (fs.statSync(ROOT).isDirectory()) {
    absRoot = fs.realpathSync(ROOT);
  }
} catch {
  absRoot = "";
}

// 1) angular.json at or above ROOT → Angular workspace.
if (absRoot) {
  let dir = absRoot;
  for (;;) {
    if (fs.existsSync(path.join(dir, "angular.json"))) {
      angular = true;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
}

// Recursively collect file paths under `root`, skipping node_modules directories.
function walk(root) {
  const results = [];
  const stack = [root];
  while (stack.length > 0) {
    const current = stack.pop();
    let entries;
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (entry.name === "node_modules") continue;
        stack.push(path.join(current, entry.name));
      } else if (entry.isFile()) {
        results.push(path.join(current, entry.name));
      }
    }
  }
  return results;
}

const files = walk(ROOT);

// 2) package.json dependencies (excluding node_modules).
for (const file of files) {
  if (path.basename(file) !== "package.json") continue;
  let content = "";
  try {
    content = fs.readFileSync(file, "utf8");
  } catch {
    continue;
  }
  if (content.includes('"@angular/core"')) angular = true;
  if (/"react"\s*:/.test(content)) react = true;
}

// 3) Source-file signatures (excluding node_modules).
function hasFile(matches) {
  return files.some(matches);
}

// Angular: component files, routing module, or @Component-decorated classes.
if (hasFile((f) => f.endsWith(".component.ts"))) angular = true;
if (hasFile((f) => path.basename(f) === "app.routes.ts")) angular = true;

for (const file of files) {
  if (!file.endsWith(".ts")) continue;
  let content = "";
  try {
    content = fs.readFileSync(file, "utf8");
  } catch {
    continue;
  }
  if (content.includes("@Component")) {
    angular = true;
    break;
  }
}

// React: JSX/TSX source files.
if (hasFile((f) => f.endsWith(".tsx"))) react = true;
if (hasFile((f) => f.endsWith(".jsx"))) react = true;

if (angular && react) {
  console.log("ambiguous");
  process.exit(2);
} else if (angular) {
  console.log("angular");
  process.exit(0);
} else if (react) {
  console.log("react");
  process.exit(0);
} else {
  console.log("unknown");
  process.exit(3);
}
