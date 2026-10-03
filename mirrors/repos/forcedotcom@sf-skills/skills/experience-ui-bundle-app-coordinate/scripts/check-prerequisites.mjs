#!/usr/bin/env node
// Check prerequisites for UI Bundle app building.
// Usage: node check-prerequisites.mjs
//
// Always invoke via `node` (never as a bare executable) so this works on
// Windows cmd/PowerShell as well as macOS/Linux/Git Bash.
//
// Exit 0 if all prerequisites are met, exit 1 with an error message if any
// are missing.

const [major] = process.versions.node.split(".").map(Number);

if (!Number.isFinite(major) || major < 20) {
  console.error(
    `ERROR: Node.js version ${process.versions.node} detected. Requires >= 20.x`,
  );
  process.exit(1);
}

console.log(`SUCCESS: Node.js v${process.versions.node} meets the >= 20.x requirement`);
process.exit(0);
