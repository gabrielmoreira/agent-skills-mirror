#!/usr/bin/env node

import path from "node:path";
import { spawnSync } from "node:child_process";
import { detectHermesHome, resolveHermesScopedOutputPath } from "../lib/attestation.mjs";

const MARKER_START = "# >>> hermes-attestation-guardian >>>";
const MARKER_END = "# <<< hermes-attestation-guardian <<<";

function usage() {
  process.stdout.write(
    [
      "Usage: node scripts/setup_attestation_cron.mjs [options]",
      "",
      "Options:",
      "  --every <Nh|Nd>         Interval cadence (default: 6h)",
      "  --policy <path>         Optional policy file passed to generator",
      "  --baseline <path>       Optional baseline path passed to verifier",
      "  --baseline-sha256 <hex> Trusted baseline SHA256 passed to verifier",
      "  --baseline-signature <path> Baseline detached signature for verifier",
      "  --baseline-public-key <path> Baseline signature public key for verifier",
      "  --output <path>         Optional output attestation path",
      "  --apply                 Apply to current user's crontab",
      "  --print-only            Print resulting cron block (default)",
      "  --help                  Show this help",
      "",
      "Hermes assumptions:",
      "- Writes only under ~/.hermes paths by default",
      "- Uses Node + this skill's scripts only",
      "- No OpenClaw runtime dependencies",
      "",
    ].join("\n"),
  );
}

function parseArgs(argv) {
  const args = {
    every: process.env.HERMES_ATTESTATION_INTERVAL || "6h",
    policy: process.env.HERMES_ATTESTATION_POLICY || null,
    baseline: process.env.HERMES_ATTESTATION_BASELINE || null,
    baselineSha256: process.env.HERMES_ATTESTATION_BASELINE_SHA256 || null,
    baselineSignature: process.env.HERMES_ATTESTATION_BASELINE_SIGNATURE || null,
    baselinePublicKey: process.env.HERMES_ATTESTATION_BASELINE_PUBLIC_KEY || null,
    output: process.env.HERMES_ATTESTATION_OUTPUT_DIR
      ? path.join(process.env.HERMES_ATTESTATION_OUTPUT_DIR, "current.json")
      : null,
    apply: false,
    printOnly: true,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--help") {
      args.help = true;
      continue;
    }
    if (token === "--every") {
      args.every = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--policy") {
      args.policy = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--baseline") {
      args.baseline = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--baseline-sha256") {
      args.baselineSha256 = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--baseline-signature") {
      args.baselineSignature = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--baseline-public-key") {
      args.baselinePublicKey = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--output") {
      args.output = argv[i + 1];
      i += 1;
      continue;
    }
    if (token === "--apply") {
      args.apply = true;
      args.printOnly = false;
      continue;
    }
    if (token === "--print-only") {
      args.printOnly = true;
      args.apply = false;
      continue;
    }

    throw new Error(`Unknown argument: ${token}`);
  }

  return args;
}

function cadenceToCron(cadence) {
  const normalized = String(cadence || "").trim().toLowerCase();
  const match = normalized.match(/^(\d+)([hd])$/);
  if (!match) {
    throw new Error(`Invalid cadence '${cadence}'. Expected <number>h or <number>d.`);
  }

  const n = Number(match[1]);
  const unit = match[2];

  if (!Number.isInteger(n) || n <= 0) {
    throw new Error(`Cadence must be a positive integer: ${cadence}`);
  }

  if (unit === "h") {
    if (n > 24) {
      throw new Error("Hourly cadence cannot exceed 24h for cron expression generation.");
    }
    return `0 */${n} * * *`;
  }

  if (n > 31) {
    throw new Error("Daily cadence cannot exceed 31d for cron expression generation.");
  }
  return `0 2 */${n} * *`;
}

function escapeForShell(value) {
  return String(value).replace(/'/g, "'\\''");
}

function buildCronCommand({ output, policy, baseline, baselineSha256, baselineSignature, baselinePublicKey }) {
  const scriptDir = path.resolve(path.dirname(new URL(import.meta.url).pathname));
  const generator = path.join(scriptDir, "generate_attestation.mjs");
  const verifier = path.join(scriptDir, "verify_attestation.mjs");

  const outputArg = output ? `--output '${escapeForShell(path.resolve(output))}'` : "";
  const policyArg = policy ? `--policy '${escapeForShell(path.resolve(policy))}'` : "";
  const baselineArg = baseline ? `--baseline '${escapeForShell(path.resolve(baseline))}'` : "";
  const baselineShaArg = baselineSha256 ? `--baseline-expected-sha256 '${escapeForShell(String(baselineSha256).trim())}'` : "";
  const baselineSigArg = baselineSignature
    ? `--baseline-signature '${escapeForShell(path.resolve(baselineSignature))}'`
    : "";
  const baselinePubArg = baselinePublicKey
    ? `--baseline-public-key '${escapeForShell(path.resolve(baselinePublicKey))}'`
    : "";

  return [
    `node '${escapeForShell(generator)}' ${outputArg} ${policyArg}`.replace(/\s+/g, " ").trim(),
    `node '${escapeForShell(verifier)}' --input '${escapeForShell(path.resolve(output || path.join(detectHermesHome(), "security", "attestations", "current.json")))}' ${baselineArg} ${baselineShaArg} ${baselineSigArg} ${baselinePubArg}`
      .replace(/\s+/g, " ")
      .trim(),
  ].join(" && ");
}

function buildCronBlock({ cronExpr, command, hermesHome }) {
  const envPrefix = [
    `HERMES_HOME='${escapeForShell(hermesHome)}'`,
    `PATH='${escapeForShell(process.env.PATH || "/usr/local/bin:/usr/bin:/bin")}'`,
  ].join(" ");

  return [
    MARKER_START,
    `# Managed by hermes-attestation-guardian (${new Date().toISOString()})`,
    `${cronExpr} ${envPrefix} ${command}`,
    MARKER_END,
  ].join("\n");
}

function removeManagedBlock(text) {
  const lines = String(text || "").split(/\r?\n/);
  const out = [];

  let inManagedBlock = false;
  let managedStartLine = null;

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed === MARKER_START) {
      if (inManagedBlock) {
        throw new Error(`Malformed crontab markers: nested managed block start at line ${i + 1}`);
      }
      inManagedBlock = true;
      managedStartLine = i + 1;
      continue;
    }

    if (trimmed === MARKER_END) {
      if (!inManagedBlock) {
        throw new Error(`Malformed crontab markers: unmatched managed block end at line ${i + 1}`);
      }
      inManagedBlock = false;
      managedStartLine = null;
      continue;
    }

    if (!inManagedBlock) {
      out.push(line);
    }
  }

  if (inManagedBlock) {
    throw new Error(`Malformed crontab markers: managed block start at line ${managedStartLine} has no end marker`);
  }

  return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

function readCurrentCrontab() {
  const res = spawnSync("crontab", ["-l"], { encoding: "utf8" });
  if (res.status !== 0) {
    const stderr = String(res.stderr || "").toLowerCase();
    if (stderr.includes("no crontab") || stderr.includes("can't open your crontab")) {
      return "";
    }
    throw new Error(`Failed reading crontab: ${res.stderr || res.stdout}`);
  }
  return res.stdout || "";
}

function writeCrontab(content) {
  const res = spawnSync("crontab", ["-"], { input: `${content.trim()}\n`, encoding: "utf8" });
  if (res.status !== 0) {
    throw new Error(`Failed writing crontab: ${res.stderr || res.stdout}`);
  }
}

function run() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return;
  }

  const hermesHome = path.resolve(detectHermesHome());
  const output = resolveHermesScopedOutputPath(args.output, hermesHome);

  if (args.baseline && !args.baselineSha256 && !(args.baselineSignature && args.baselinePublicKey)) {
    throw new Error(
      "baseline scheduling requires --baseline-sha256 or both --baseline-signature and --baseline-public-key",
    );
  }

  const cronExpr = cadenceToCron(args.every);
  const command = buildCronCommand({
    output,
    policy: args.policy,
    baseline: args.baseline,
    baselineSha256: args.baselineSha256,
    baselineSignature: args.baselineSignature,
    baselinePublicKey: args.baselinePublicKey,
  });
  const block = buildCronBlock({ cronExpr, command, hermesHome });

  const preflightLines = [
    "Preflight review:",
    "- This helper configures recurring Hermes attestation generation + verification.",
    `- Hermes home: ${hermesHome}`,
    `- Attestation output: ${output}`,
    `- Cadence: ${args.every} (${cronExpr})`,
    `- Baseline: ${args.baseline ? path.resolve(args.baseline) : "not configured"}`,
    `- Baseline trusted sha256: ${args.baselineSha256 ? String(args.baselineSha256).trim() : "not configured"}`,
    `- Baseline signature: ${args.baselineSignature ? path.resolve(args.baselineSignature) : "not configured"}`,
    `- Baseline public key: ${args.baselinePublicKey ? path.resolve(args.baselinePublicKey) : "not configured"}`,
    `- Policy: ${args.policy ? path.resolve(args.policy) : "not configured"}`,
    "- Scope: Hermes-only.",
  ];
  process.stdout.write(`${preflightLines.join("\n")}\n\n`);

  if (args.printOnly) {
    process.stdout.write(`${block}\n`);
    return;
  }

  const current = readCurrentCrontab();
  const withoutManaged = removeManagedBlock(current);
  const merged = [withoutManaged, block].filter(Boolean).join("\n\n").trim();
  writeCrontab(merged);

  process.stdout.write("INFO: Updated user crontab with hermes-attestation-guardian managed block\n");
}

try {
  run();
} catch (error) {
  process.stderr.write(`CRITICAL: ${error?.message || String(error)}\n`);
  process.exit(1);
}
