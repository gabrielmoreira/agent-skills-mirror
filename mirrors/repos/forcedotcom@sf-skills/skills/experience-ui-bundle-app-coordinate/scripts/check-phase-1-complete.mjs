#!/usr/bin/env node
// Verify Phase 1 (Scaffolding) completed successfully.
// Usage: node check-phase-1-complete.mjs
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

const bundleDir = findBundleDir();

if (!bundleDir) {
  fail(
    `ERROR: Phase 1 incomplete: No UI bundle directory found in ${UIBUNDLES_DIR}${path.sep}`,
  );
}

if (!fs.existsSync(path.join(bundleDir, "src"))) {
  fail(`ERROR: Phase 1 incomplete: No src/ directory found in ${bundleDir}`);
}

const metaFiles = fs
  .readdirSync(bundleDir)
  .filter((name) => name.endsWith(".uibundle-meta.xml"));

if (metaFiles.length === 0) {
  fail(`ERROR: Phase 1 incomplete: No .uibundle-meta.xml file found in ${bundleDir}`);
}

const hasTarget = metaFiles.some((name) => {
  try {
    return fs.readFileSync(path.join(bundleDir, name), "utf8").includes("<target>");
  } catch {
    return false;
  }
});

if (!hasTarget) {
  fail("ERROR: Phase 1 incomplete: .uibundle-meta.xml missing <target> element");
}

if (!fs.existsSync(path.join(bundleDir, "package.json"))) {
  fail(`ERROR: Phase 1 incomplete: No package.json found in ${bundleDir}`);
}

console.log("SUCCESS: Phase 1 complete: Scaffold verified");
process.exit(0);
