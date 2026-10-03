#!/usr/bin/env node
// Verify Phase 4 (UI) completed successfully.
// Usage: node check-phase-4-complete.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Exit 0 if complete, exit 1 with an error message if incomplete.

import fs from "node:fs";
import path from "node:path";

const UIBUNDLES_DIR = path.join("force-app", "main", "default", "uiBundles");

function findBundleDir() {
  let entries;
  try {
    entries = fs.readdirSync(UIBUNDLES_DIR, { withFileTypes: true });
  } catch {
    return "";
  }
  const dirs = entries
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
  return dirs.length > 0 ? path.join(UIBUNDLES_DIR, dirs[0]) : "";
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function findTsxFiles(dir) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return [];
  }
  const out = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...findTsxFiles(full));
    } else if (entry.isFile() && entry.name.endsWith(".tsx")) {
      out.push(full);
    }
  }
  return out;
}

const bundleDir = findBundleDir();

if (!bundleDir) {
  fail("ERROR: Phase 4 cannot run: No UI bundle directory found (Phase 1 not complete)");
}

// Check Phase 1 scaffold prerequisites
const packageJsonPath = path.join(bundleDir, "package.json");
if (!fs.existsSync(packageJsonPath)) {
  fail("ERROR: Phase 4 cannot run: No package.json found (Phase 1 not complete)");
}

let packageJsonContent = "";
try {
  packageJsonContent = fs.readFileSync(packageJsonPath, "utf8");
} catch {
  packageJsonContent = "";
}

if (!packageJsonContent.includes('"react"')) {
  fail("ERROR: Phase 4 cannot run: React dependencies not installed in package.json");
}

// Check Phase 4 completion
if (!fs.existsSync(path.join(bundleDir, "src", "App.tsx"))) {
  fail(`ERROR: Phase 4 incomplete: No App.tsx found in ${path.join(bundleDir, "src")}${path.sep}`);
}

const pagesDir = path.join(bundleDir, "src", "pages");
if (!fs.existsSync(pagesDir) || !fs.statSync(pagesDir).isDirectory()) {
  fail(`ERROR: Phase 4 incomplete: No pages/ directory found in ${path.join(bundleDir, "src")}${path.sep}`);
}

if (findTsxFiles(pagesDir).length === 0) {
  fail("ERROR: Phase 4 incomplete: No .tsx files found in pages/ directory");
}

if (!fs.existsSync(path.join(bundleDir, "dist", "index.html"))) {
  fail("ERROR: Phase 4 incomplete: No dist/index.html found (build not complete)");
}

console.log("SUCCESS: Phase 4 complete: UI verified");
process.exit(0);
