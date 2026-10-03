#!/usr/bin/env node
// Verify a resolved UI bundle directory is actually scaffolded before any
// rule in this skill applies.
// Usage: node check-preconditions.mjs <bundle-dir>
//   <bundle-dir> is the path printed by resolve-ui-bundle.mjs.
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash. Quote
// <bundle-dir> so Windows paths and spaces survive the shell.
//
// Exit 0 if the bundle is scaffolded (src/appLayout.tsx, src/routes.tsx, and
// src/components/ui/ all present).
// Exit 1 with the missing pieces listed if the bundle is a fresh SFDX
// project, a non-UI-bundle React project, or only partially scaffolded —
// the caller must stop and redirect the user to
// experience-ui-bundle-app-coordinate (or experience-ui-bundle-metadata-generate)
// instead of falling back to generic React knowledge.

import fs from "node:fs";
import path from "node:path";

const BUNDLE_DIR = process.argv[2] ?? "";

function fail(message) {
  console.error(message);
  process.exit(1);
}

if (!BUNDLE_DIR) {
  fail("ERROR: check-preconditions.mjs requires a valid bundle directory argument");
}

let isDir = false;
try {
  isDir = fs.statSync(BUNDLE_DIR).isDirectory();
} catch {
  isDir = false;
}

if (!isDir) {
  fail("ERROR: check-preconditions.mjs requires a valid bundle directory argument");
}

const missing = [];
if (!fs.existsSync(path.join(BUNDLE_DIR, "src", "appLayout.tsx"))) {
  missing.push("src/appLayout.tsx");
}
if (!fs.existsSync(path.join(BUNDLE_DIR, "src", "routes.tsx"))) {
  missing.push("src/routes.tsx");
}
const uiDir = path.join(BUNDLE_DIR, "src", "components", "ui");
if (!fs.existsSync(uiDir) || !fs.statSync(uiDir).isDirectory()) {
  missing.push("src/components/ui/");
}

if (missing.length > 0) {
  console.error(`ERROR: ${BUNDLE_DIR} is not a scaffolded UI bundle. Missing:`);
  for (const item of missing) {
    console.error(`  - ${item}`);
  }
  console.error(
    "Stop here. Tell the user the bundle isn't scaffolded yet and direct them to experience-ui-bundle-app-coordinate (or experience-ui-bundle-metadata-generate) to scaffold it first.",
  );
  process.exit(1);
}

console.log(
  `SUCCESS: ${BUNDLE_DIR} is scaffolded (src/appLayout.tsx, src/routes.tsx, src/components/ui/ present)`,
);
process.exit(0);
