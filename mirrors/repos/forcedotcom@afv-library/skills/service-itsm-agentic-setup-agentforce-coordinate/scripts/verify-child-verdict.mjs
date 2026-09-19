#!/usr/bin/env node
// Deterministic queue-advancement gate (authoring standard A9). Each child
// skill already emits its own machine-readable verdict — Studio's `overall`
// from classify-final-report.mjs, Fulfiller/Employee's Phase 8 aggregate, the
// escalation leaf's `status`, the runtime-access skill's Phase-7 aggregate — so
// this script only maps those fixed value sets to an advance/stop decision.
// It must not be re-derived in prose; the coordinator runs this and reads the
// exit code.
//
// Usage:
//   node verify-child-verdict.mjs <studio|fulfiller|employee|escalation|runtime> <verdict>
//
// Exit 0  -> child succeeded (or benign no-op), safe to advance the queue.
// Exit 1  -> child failed or only partially succeeded, stop the queue.
// Exit 2  -> usage error (bad args).

const SUCCESS_VALUES = {
  studio: new Set(['SUCCESS']),
  fulfiller: new Set(['CREATED', 'ALREADY-CREATED', 'ACTIVATED']),
  employee: new Set(['CREATED', 'ALREADY-CREATED', 'ACTIVATED']),
  // Employee-agent escalation leaf (service-agentforce-human-escalation-configure, IT scenario inputs)
  // emits CONFIGURED when every deterministic surface is satisfied; a re-run is an
  // idempotent CONFIGURED. INCOMPLETE/BLOCKED stop the queue.
  escalation: new Set(['CONFIGURED', 'ALREADY-CONFIGURED']),
  // Runtime-access-assign (service-itsm-agentic-setup-agent-runtime-access-assign),
  // the automatic Stage 3 after any Stage 2 agent goes live, emits its Phase-7
  // aggregate: ASSIGNED (a write landed + read back) or ALREADY-ASSIGNED (all
  // intended state already present). Both advance. PARTIAL / FAILED stop the queue.
  runtime: new Set(['ASSIGNED', 'ALREADY-ASSIGNED']),
};

// Benign no-op verdicts: not a success (nothing was assigned) but not a failure
// either — a legitimate terminal "there is nothing to assign" state that must
// still ADVANCE (the queue is complete, not broken). Runtime-access emits
// NONE-PROVISIONED when no feature permset is provisioned AND no agent is
// activated: correct, expected, and nothing to remediate — so Stage 3 closes
// cleanly rather than reading as a stop. PARTIAL / FAILED are deliberately NOT
// here; those fall through to STOP below.
const NOOP_VALUES = {
  runtime: new Set(['NONE-PROVISIONED']),
};

const [child, verdict] = process.argv.slice(2);

if (!child || !verdict || !SUCCESS_VALUES[child]) {
  process.stderr.write('usage: node verify-child-verdict.mjs <studio|fulfiller|employee|escalation|runtime> <verdict>\n');
  process.exit(2);
}

if (SUCCESS_VALUES[child].has(verdict)) {
  process.stdout.write(`ADVANCE: ${child} verdict "${verdict}" is a success value.\n`);
  process.exit(0);
}

if (NOOP_VALUES[child]?.has(verdict)) {
  process.stdout.write(`ADVANCE: ${child} verdict "${verdict}" is a benign no-op — nothing to assign, queue is complete.\n`);
  process.exit(0);
}

process.stdout.write(`STOP: ${child} verdict "${verdict}" is not a success value — do not advance the queue.\n`);
process.exit(1);
