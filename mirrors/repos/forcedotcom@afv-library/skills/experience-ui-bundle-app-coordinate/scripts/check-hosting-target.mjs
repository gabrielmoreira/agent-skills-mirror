#!/usr/bin/env node
// Check which hosting target is configured in .uibundle-meta.xml files.
// Usage: node check-hosting-target.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Prints "ExperienceSite" or "CustomApplication" to stdout and exits 0 on
// success. Exits 1 with an error message if no .uibundle-meta.xml files
// are found, or none declare a valid target.

import fs from "node:fs";
import path from "node:path";

const EXCLUDE_DIRS = new Set(["node_modules", "dist", "build", ".git"]);

function findMetaFiles(dir, out) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (EXCLUDE_DIRS.has(entry.name)) continue;
      findMetaFiles(full, out);
    } else if (entry.isFile() && entry.name.endsWith(".uibundle-meta.xml")) {
      out.push(full);
    }
  }
}

const metaFiles = [];
findMetaFiles(".", metaFiles);

if (metaFiles.length === 0) {
  console.error("ERROR: No .uibundle-meta.xml files found");
  process.exit(1);
}

const contents = metaFiles.map((f) => {
  try {
    return fs.readFileSync(f, "utf8");
  } catch {
    return "";
  }
});

if (contents.some((c) => c.includes("<target>ExperienceSite</target>"))) {
  console.log("ExperienceSite");
  process.exit(0);
}

if (contents.some((c) => c.includes("<target>CustomApplication</target>"))) {
  console.log("CustomApplication");
  process.exit(0);
}

console.error("ERROR: No valid hosting target found in .uibundle-meta.xml");
process.exit(1);
