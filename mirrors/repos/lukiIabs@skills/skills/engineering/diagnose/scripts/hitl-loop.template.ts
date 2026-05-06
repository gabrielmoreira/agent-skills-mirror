#!/usr/bin/env node
/**
 * Human-in-the-loop reproduction loop template (TypeScript / Node).
 * Copy this file, edit the steps below, run: npm run hitl-loop
 * Or: npm run build && node dist/skills/engineering/diagnose/scripts/hitl-loop.template.js
 */
import * as readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

const rl = readline.createInterface({ input, output });

async function step(msg: string): Promise<void> {
  console.log(`\n>>> ${msg}`);
  await rl.question('    [Enter when done] ');
}

async function capture(question: string): Promise<string> {
  console.log(`\n>>> ${question}`);
  return (await rl.question('    > ')).trim();
}

// --- edit below ---------------------------------------------------------

await step('Open the app at http://localhost:3000 and sign in.');

const ERRORED = await capture("Click the 'Export' button. Did it throw an error? (y/n)");

const ERROR_MSG = await capture("Paste the error message (or 'none'):");

// --- edit above ---------------------------------------------------------

console.log('\n--- Captured ---');
console.log(`ERRORED=${ERRORED}`);
console.log(`ERROR_MSG=${ERROR_MSG}`);
rl.close();
