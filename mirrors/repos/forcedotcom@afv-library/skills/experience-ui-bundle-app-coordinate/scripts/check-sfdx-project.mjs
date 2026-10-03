#!/usr/bin/env node
// Check if sfdx-project.json exists and is valid JSON.
// Usage: node check-sfdx-project.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Exit 0 if sfdx-project.json exists and parses as JSON, exit 1 with an
// error message otherwise.

import fs from "node:fs";

const SFDX_PROJECT = "sfdx-project.json";

if (!fs.existsSync(SFDX_PROJECT)) {
  console.error("ERROR: sfdx-project.json not found");
  process.exit(1);
}

try {
  JSON.parse(fs.readFileSync(SFDX_PROJECT, "utf8"));
} catch {
  console.error("ERROR: sfdx-project.json is not valid JSON");
  process.exit(1);
}

console.log("sfdx-project.json is valid");
process.exit(0);
