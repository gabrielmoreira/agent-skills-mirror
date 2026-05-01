import fs from 'node:fs';
import path from 'node:path';

import { DeltaChanges, NormalizedIssue, NormalizedPullRequest, StateSnapshot } from './types';

export function createItemHash(item: NormalizedIssue | NormalizedPullRequest): string {
  const data = `${item.updatedAt}|${item.commentsTotal}|${item.title}`;
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

export function createState(
  datetime: string,
  reportDir: string,
  issues: NormalizedIssue[],
  prs: NormalizedPullRequest[]
): StateSnapshot {
  return {
    schemaVersion: 1,
    lastRunAt: new Date().toISOString(),
    lastReportDir: path.normalize(reportDir),
    issueHashes: Object.fromEntries(issues.map(i => [String(i.number), createItemHash(i)])),
    prHashes: Object.fromEntries(prs.map(p => [String(p.number), createItemHash(p)])),
  };
}

export function readState(stateFilePath: string): StateSnapshot | null {
  if (!fs.existsSync(stateFilePath)) return null;
  try {
    const raw = fs.readFileSync(stateFilePath, 'utf8');
    const parsed = JSON.parse(raw) as StateSnapshot;
    if (!parsed || !parsed.issueHashes || !parsed.prHashes) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeState(stateFilePath: string, state: StateSnapshot) {
  const dir = path.dirname(stateFilePath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(stateFilePath, `${JSON.stringify(state, null, 2)}\n`, 'utf8');
}

export function computeDeltaFromState(
  currentIssues: NormalizedIssue[],
  currentPrs: NormalizedPullRequest[],
  previousState: StateSnapshot
): DeltaChanges {
  const prevIssueHashes = previousState.issueHashes ?? {};
  const prevPrHashes = previousState.prHashes ?? {};

  const currentIssueNumbers = new Set(currentIssues.map(i => String(i.number)));
  const currentPrNumbers = new Set(currentPrs.map(p => String(p.number)));

  const newIssues = currentIssues.filter(i => !prevIssueHashes[String(i.number)]).map(i => i.number);
  const updatedIssues = currentIssues.filter(i => {
    const key = String(i.number);
    return prevIssueHashes[key] && prevIssueHashes[key] !== createItemHash(i);
  }).map(i => i.number);
  const closedIssues = Object.keys(prevIssueHashes)
    .filter((key) => !currentIssueNumbers.has(key))
    .map((key) => Number(key));

  const newPrs = currentPrs.filter(p => !prevPrHashes[String(p.number)]).map(p => p.number);
  const updatedPrs = currentPrs.filter(p => {
    const key = String(p.number);
    return prevPrHashes[key] && prevPrHashes[key] !== createItemHash(p);
  }).map(p => p.number);
  const closedPrs = Object.keys(prevPrHashes)
    .filter((key) => !currentPrNumbers.has(key))
    .map((key) => Number(key));

  return {
    newIssues,
    updatedIssues,
    newPrs,
    updatedPrs,
    closedIssues,
    closedPrs,
  };
}

export function findLatestReportDir(reportsPath: string): string | null {
  if (!fs.existsSync(reportsPath)) return null;

  const dirs = fs.readdirSync(reportsPath, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort()
    .reverse();

  return dirs[0] ?? null;
}
