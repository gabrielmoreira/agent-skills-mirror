#!/usr/bin/env node
// Verifies that a UI bundle was created under force-app/main/default/uiBundles/
// (and not at the repo root, which would be non-deployable), AND that the
// scaffold itself is complete (package.json, src/, entry index.html present) —
// not just a hand-authored metadata-only directory.
//
// The entry index.html lives at the bundle root for React (reactbasic) and at
// src/index.html for Angular (angularbasic), so both locations are accepted.
//
// If a custom output directory was used (--output-dir on the scaffold command),
// pass it as the second argument. The script then verifies the bundle exists
// there instead of assuming the default location. Pass the framework
// (react|angular) as the third argument so the remediation hint uses the right
// --template flag; pass "" for the second argument to supply only a framework.
//
// Usage: node verify-bundle-location.mjs <BundleName> [<CustomOutputDir>] [<framework>]
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.

import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);

if (args.length < 1 || args.length > 3) {
  console.log("ERROR: Bundle name required");
  console.log("Usage: node verify-bundle-location.mjs <BundleName> [<CustomOutputDir>] [<framework>]");
  process.exit(1);
}

const BUNDLE_NAME = args[0];
const CUSTOM_OUTPUT_DIR = args[1] ?? "";
const FRAMEWORK = args[2] ?? "";

// Pick the remediation template and the expected entry-HTML location from the
// framework. When the framework is not supplied we stay lenient: default the
// hint to reactbasic and accept the entry index.html at either location.
let TEMPLATE;
let ENTRY;
switch (FRAMEWORK) {
  case "angular":
    TEMPLATE = "angularbasic";
    ENTRY = "src/index.html";
    break;
  case "react":
    TEMPLATE = "reactbasic";
    ENTRY = "index.html";
    break;
  default:
    TEMPLATE = "reactbasic";
    ENTRY = "";
    break;
}

function isFile(p) {
  try {
    return fs.statSync(p).isFile();
  } catch {
    return false;
  }
}

function isDir(p) {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
}

// Checks that the scaffold actually produced a full project, not just
// hand-written metadata files. Returns false (and prints guidance) if
// incomplete.
function checkScaffoldComplete(bundlePath, outputDir = "") {
  const missing = [];
  if (!isFile(path.join(bundlePath, "package.json"))) missing.push("package.json");
  if (!isDir(path.join(bundlePath, "src"))) missing.push("src/");
  // Entry HTML lives at the bundle root for React and at src/index.html for
  // Angular. When the framework is known, require the correct location; when
  // it is unknown, accept either.
  if (ENTRY) {
    if (!isFile(path.join(bundlePath, ENTRY))) missing.push(ENTRY);
  } else if (!isFile(path.join(bundlePath, "index.html")) && !isFile(path.join(bundlePath, "src", "index.html"))) {
    missing.push("index.html");
  }

  if (missing.length > 0) {
    let scaffoldCmd = `sf template generate ui-bundle -n ${BUNDLE_NAME} --template ${TEMPLATE}`;
    if (outputDir) {
      scaffoldCmd = `${scaffoldCmd} --output-dir "${outputDir}"`;
    }
    console.error(`ERROR: Bundle found at ${bundlePath}, but the scaffold is incomplete. Missing:`);
    for (const item of missing) {
      console.error(`  - ${item}`);
    }
    console.error("");
    console.error("This usually means 'sf template generate ui-bundle' was never run — metadata");
    console.error("files alone were hand-authored instead. Run the scaffold command now:");
    console.error(`  ${scaffoldCmd}`);
    console.error("Metadata files are configuration ON TOP of the scaffold, not a substitute for it.");
    return false;
  }
  return true;
}

if (CUSTOM_OUTPUT_DIR) {
  const customPath = path.join(CUSTOM_OUTPUT_DIR, BUNDLE_NAME);
  if (isDir(customPath)) {
    if (checkScaffoldComplete(customPath, CUSTOM_OUTPUT_DIR)) {
      console.log(`OK: Bundle found at ${customPath} (custom output-dir location, scaffold complete)`);
      process.exit(0);
    }
    process.exit(1);
  }
  console.log(`ERROR: Bundle not found at custom output-dir location: ${customPath}`);
  console.log("Check that --output-dir matched what was passed to the scaffold command.");
  process.exit(1);
}

const EXPECTED_PATH = path.join("force-app", "main", "default", "uiBundles", BUNDLE_NAME);
const WRONG_PATH = path.join("uiBundles", BUNDLE_NAME);

if (isDir(EXPECTED_PATH)) {
  if (checkScaffoldComplete(EXPECTED_PATH)) {
    console.log(`OK: Bundle found at ${EXPECTED_PATH} (deployable location, scaffold complete)`);
    process.exit(0);
  }
  process.exit(1);
}

if (isDir(WRONG_PATH)) {
  console.log(`ERROR: Bundle found at repo root: ${WRONG_PATH}`);
  console.log("This location is NOT deployable. The SFDX deploy command will not find it.");
  console.log("");
  console.log("To fix: Move the bundle to force-app/main/default/uiBundles/");
  console.log(`  Create the directory force-app/main/default/uiBundles/ (if it doesn't exist),`);
  console.log(`  then move ${WRONG_PATH} to ${EXPECTED_PATH}.`);
  console.log("");
  checkScaffoldComplete(WRONG_PATH);
  process.exit(1);
}

console.log("ERROR: Bundle not found at either location:");
console.log(`  - Expected: ${EXPECTED_PATH}`);
console.log(`  - Also checked: ${WRONG_PATH}`);
console.log("");
console.log("If a custom --output-dir was used, re-run this script with that directory");
console.log(`as the second argument: node verify-bundle-location.mjs ${BUNDLE_NAME} <CustomOutputDir>`);
console.log("");
console.log("Otherwise, the scaffold command may have failed. Check for errors above.");
process.exit(1);
