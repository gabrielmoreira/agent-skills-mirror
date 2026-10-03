#!/usr/bin/env node
// Resolve the single UI bundle directory for this project.
// Usage: node resolve-ui-bundle.mjs [project-root]   (default: current directory)
//
// Reads sfdx-project.json's packageDirectories[0].path, looks under
// <that-path>/main/default/uiBundles/, and prints the resolved bundle
// directory to stdout on success.
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash. Quote the
// project-root argument so paths with spaces or Windows backslashes stay
// a single argv.
//
// Exit 0: exactly one bundle directory found — printed to stdout.
// Exit 1: sfdx-project.json missing/invalid, or no uiBundles/* subdirectory
//         found at all (not a scaffolded SFDX project yet).
// Exit 2: multiple uiBundles/* subdirectories found — caller MUST ask the
//         user which one they mean rather than guessing; candidate names are
//         printed to stderr.

import fs from "node:fs";
import path from "node:path";

const PROJECT_ROOT = path.resolve(process.argv[2] ?? ".");
const SFDX_PROJECT = path.join(PROJECT_ROOT, "sfdx-project.json");

function fail(code, message) {
  console.error(message);
  process.exit(code);
}

if (!fs.existsSync(SFDX_PROJECT) || !fs.statSync(SFDX_PROJECT).isFile()) {
  fail(1, `ERROR: sfdx-project.json not found at ${SFDX_PROJECT}`);
}

let sourcePath = "";
try {
  const data = JSON.parse(fs.readFileSync(SFDX_PROJECT, "utf8"));
  const dirs = data?.packageDirectories ?? [];
  sourcePath = dirs[0]?.path ?? "";
} catch {
  sourcePath = "";
}

if (!sourcePath) {
  fail(1, "ERROR: sfdx-project.json is invalid or has no packageDirectories[0].path");
}

const BUNDLES_DIR = path.join(PROJECT_ROOT, sourcePath, "main", "default", "uiBundles");

if (!fs.existsSync(BUNDLES_DIR) || !fs.statSync(BUNDLES_DIR).isDirectory()) {
  fail(1, `ERROR: No uiBundles/ directory found at ${BUNDLES_DIR}`);
}

const bundleDirs = fs
  .readdirSync(BUNDLES_DIR, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => path.join(BUNDLES_DIR, entry.name))
  .sort();

if (bundleDirs.length === 0) {
  fail(1, `ERROR: ${BUNDLES_DIR} exists but contains no bundle subdirectories`);
}

if (bundleDirs.length > 1) {
  console.error(
    "AMBIGUOUS: Multiple UI bundle directories found — ask the user which one they mean before editing or running any command:",
  );
  for (const dir of bundleDirs) {
    console.error(`  - ${dir}`);
  }
  process.exit(2);
}

console.log(bundleDirs[0]);
process.exit(0);
