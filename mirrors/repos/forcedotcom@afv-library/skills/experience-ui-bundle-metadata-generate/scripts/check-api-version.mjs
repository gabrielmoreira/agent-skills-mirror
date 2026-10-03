#!/usr/bin/env node
// Checks that sourceApiVersion in sfdx-project.json is 67.0 or higher.
// If lower, updates it to "67.0".
//
// Usage: node check-api-version.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash. Parses and rewrites
// sfdx-project.json with native JSON (no jq dependency).

import fs from "node:fs";

const PROJECT_FILE = "sfdx-project.json";

if (!fs.existsSync(PROJECT_FILE) || !fs.statSync(PROJECT_FILE).isFile()) {
  console.log(`ERROR: ${PROJECT_FILE} not found in current directory`);
  process.exit(1);
}

let data;
try {
  data = JSON.parse(fs.readFileSync(PROJECT_FILE, "utf8"));
} catch {
  console.log(`ERROR: ${PROJECT_FILE} is not valid JSON`);
  process.exit(1);
}

const version = data.sourceApiVersion || "0";
const major = Number.parseInt(String(version).split(".")[0], 10);
const isBelow = Number.isNaN(major) || major < 67;

if (isBelow) {
  console.log(`WARNING: sourceApiVersion is ${version} (< 67.0)`);
  console.log(`Updating ${PROJECT_FILE} to set sourceApiVersion to "67.0"`);

  data.sourceApiVersion = "67.0";
  fs.writeFileSync(PROJECT_FILE, `${JSON.stringify(data, null, 2)}\n`);

  console.log("OK: Updated sourceApiVersion to 67.0");
  process.exit(0);
}

console.log(`OK: sourceApiVersion is ${version} (>= 67.0)`);
