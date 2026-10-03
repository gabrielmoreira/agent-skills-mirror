#!/usr/bin/env node
// Verify no surviving file still imports/references a file deleted during
// scaffold pruning.
// Usage: node check-dangling-refs.mjs <deleted-basename> [<deleted-basename> ...]
//   <deleted-basename> is the file name without extension, e.g. "codegen" for
//   codegen.yml, "graphqlClient" for src/api/graphqlClient.ts, "useAsyncData"
//   for the deleted hook.
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash. Quote each
// <deleted-basename> argument.
//
// Exit 0 if no dangling references found, exit 1 with error message(s) if
// any are found.

import fs from "node:fs";
import path from "node:path";

const EXCLUDE_DIRS = new Set(["node_modules", "dist", "build", ".git"]);
const UIBUNDLES_DIR = path.join("force-app", "main", "default", "uiBundles");

// Filesystem read errors encountered while walking the bundle or reading a
// file. A dangling-reference scan that could not read part of the tree has NOT
// proven the reference is gone, so any entry here must turn a would-be SUCCESS
// into a non-zero exit (see the end of the script).
const ioErrors = [];

function findBundleDir() {
  let entries;
  try {
    entries = fs.readdirSync(UIBUNDLES_DIR, { withFileTypes: true });
  } catch {
    // uiBundles dir absent/unreadable: return "" so the caller emits an explicit
    // "No UI bundle directory found" error and exits non-zero. This is a handled,
    // expected case (e.g. a fresh project), not a silently-swallowed failure.
    return "";
  }
  const dirs = entries
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
  return dirs.length > 0 ? path.join(UIBUNDLES_DIR, dirs[0]) : "";
}

function collectFiles(dir, out) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch (err) {
    // A subdirectory we cannot list may hide a surviving reference. Record it so
    // the run fails rather than reporting an untrustworthy SUCCESS.
    ioErrors.push(`could not read directory '${dir}': ${err.message}`);
    return;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (EXCLUDE_DIRS.has(entry.name)) continue;
      collectFiles(full, out);
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
}

const basenames = process.argv.slice(2);

if (basenames.length === 0) {
  console.error(
    "ERROR: check-dangling-refs.mjs requires at least one deleted-file basename as an argument",
  );
  process.exit(1);
}

const bundleDir = findBundleDir();

if (!bundleDir) {
  console.error(`ERROR: No UI bundle directory found in ${UIBUNDLES_DIR}${path.sep}`);
  process.exit(1);
}

const files = [];
collectFiles(bundleDir, files);

let foundDangling = false;

for (const basename of basenames) {
  const matches = [];
  for (const file of files) {
    let content;
    try {
      content = fs.readFileSync(file, "utf8");
    } catch (err) {
      // Could not read a surviving file — record and skip. We cannot confirm it
      // is free of the deleted reference, so the run must not report SUCCESS.
      ioErrors.push(`could not read file '${file}': ${err.message}`);
      continue;
    }
    if (content.includes(basename)) {
      matches.push(file);
    }
  }

  if (matches.length > 0) {
    foundDangling = true;
    console.error(`ERROR: Dangling reference to deleted file '${basename}' found in:`);
    for (const match of matches) {
      console.error(`  - ${match}`);
    }
  }
}

if (foundDangling) {
  process.exit(1);
}

// A read failure means the scan was incomplete — do not claim SUCCESS.
if (ioErrors.length > 0) {
  console.error(
    "ERROR: dangling-reference scan is incomplete — some paths could not be read:",
  );
  for (const e of ioErrors) {
    console.error(`  - ${e}`);
  }
  console.error(
    "Resolve the read errors above and re-run; not reporting SUCCESS on an incomplete scan.",
  );
  process.exit(1);
}

console.log(`SUCCESS: No dangling references found for: ${basenames.join(" ")}`);
process.exit(0);
