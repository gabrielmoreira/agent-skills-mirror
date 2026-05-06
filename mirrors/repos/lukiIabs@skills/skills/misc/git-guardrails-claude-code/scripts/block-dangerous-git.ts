#!/usr/bin/env node
/**
 * Claude Code PreToolUse hook — reads JSON on stdin, blocks dangerous git Bash commands.
 * Exit 2 when blocked (stderr message), 0 when allowed.
 */
import process from 'node:process';

const DANGEROUS: readonly RegExp[] = [
  /git\s+push/,
  /git\s+reset\s+--hard/,
  /git\s+clean\s+-fd\b/,
  /git\s+clean\s+-f\b/,
  /git\s+branch\s+-D\b/,
  /git\s+checkout\s+\./,
  /git\s+restore\s+\./,
  /push\s+--force/,
  /reset\s+--hard/,
];

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString('utf8');
}

const raw = (await readStdin()).trim();
if (!raw) process.exit(0);

let cmd = '';
try {
  const parsed = JSON.parse(raw) as { tool_input?: { command?: string } };
  cmd = typeof parsed.tool_input?.command === 'string' ? parsed.tool_input.command : '';
} catch {
  process.exit(0);
}

for (const re of DANGEROUS) {
  if (re.test(cmd)) {
    console.error(
      `BLOCKED: '${cmd}' matches dangerous pattern '${re.source}'. The user has prevented you from doing this.`,
    );
    process.exit(2);
  }
}

process.exit(0);
