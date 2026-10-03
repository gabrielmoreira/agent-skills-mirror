#!/usr/bin/env node
// Verify Phase 6 (Deployment) prerequisites are met.
// Usage: node check-phase-6-ready.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Exit 0 if ready, exit 1 with an error message if not ready.

import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

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
  fail("ERROR: Phase 6 cannot run: No UI bundle directory found (Phase 1 not complete)");
}

// Check build artifact exists
if (!fs.existsSync(path.join(bundleDir, "dist", "index.html"))) {
  fail("ERROR: Phase 6 cannot run: No dist/index.html found (Phase 4 build not complete)");
}

// Check org authentication
// `shell: true` resolves `sf`/`sf.cmd` across macOS/Linux/Git Bash and native
// Windows shells alike.
const orgDisplay = spawnSync("sf", ["org", "display", "--json"], {
  shell: true,
  stdio: "ignore",
});

if (orgDisplay.status !== 0) {
  fail("ERROR: Phase 6 cannot run: No authenticated org found (run: sf org login web)");
}

// Check hosting target is set
const metaFiles = fs
  .readdirSync(bundleDir)
  .filter((name) => name.endsWith(".uibundle-meta.xml"));

const hasTarget = metaFiles.some((name) => {
  try {
    return fs.readFileSync(path.join(bundleDir, name), "utf8").includes("<target>");
  } catch {
    return false;
  }
});

if (!hasTarget) {
  fail(
    "ERROR: Phase 6 cannot run: .uibundle-meta.xml missing <target> element (Phase 1 not complete)",
  );
}

console.log("SUCCESS: Phase 6 ready: All deployment prerequisites met");
process.exit(0);
