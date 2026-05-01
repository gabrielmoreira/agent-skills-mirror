import fs from 'node:fs';
import path from 'node:path';

import { loadConfig, mergeWithBase } from './config';
import { buildContributorProfiles, buildMentionedByRelations, enrichPullRequestsWithIssueSignals, normalizeIssues, normalizePullRequests } from './analysis';
import { deriveRepoOverrides, writeDerivedConfigFile } from './derive';
import { buildGraph } from './graph';
import { buildIndexFromNotes } from './index';
import { getGitSummary } from './git-summary';
import { getRepo, ISSUE_QUERY, PR_QUERY, runGraphql, type IssuePage, type PrPage } from './github';
import { readOrCreateNote } from './notes';
import {
  generateAgentBriefsTemplate,
  generateAgentPromptsTemplate,
  generateContributorsSummary,
  generateDeltaReport,
  generateExecutiveSummary,
  generateTriageTemplate,
  summarizeIssue,
  summarizePullRequest,
} from './reports';
import { computeDeltaFromState, createState, findLatestReportDir, readState, writeState } from './state';
import { ensureDir, getArgValue, getDatetimeString, hasFlag, writeJson, writeText } from './utils';
import { ensureMaintainerState, ensureWorkspace, ensureWorkFiles, listWorkFiles } from './workspace';
import { NormalizedIssue, NormalizedPullRequest } from './types';

function sanitizeDatetime(input: string): string {
  return input.trim().replace(/:/g, '-');
}

function computeDeltaFromPreviousReport(
  currentIssues: NormalizedIssue[],
  currentPrs: NormalizedPullRequest[],
  previousDataPath: string
) {
  const issuesPath = path.join(previousDataPath, 'issues.json');
  const prsPath = path.join(previousDataPath, 'prs.json');

  if (!fs.existsSync(issuesPath) || !fs.existsSync(prsPath)) {
    return null;
  }

  const prevIssuesData = JSON.parse(fs.readFileSync(issuesPath, 'utf8'));
  const prevPrsData = JSON.parse(fs.readFileSync(prsPath, 'utf8'));

  const prevIssueNumbers = new Set(prevIssuesData.issues.map((i: any) => i.number));
  const prevPrNumbers = new Set(prevPrsData.pullRequests.map((p: any) => p.number));
  const prevIssueUpdates = new Map(prevIssuesData.issues.map((i: any) => [i.number, i.updatedAt]));
  const prevPrUpdates = new Map(prevPrsData.pullRequests.map((p: any) => [p.number, p.updatedAt]));

  const currentIssueNumbers = new Set(currentIssues.map(i => i.number));
  const currentPrNumbers = new Set(currentPrs.map(p => p.number));

  return {
    newIssues: currentIssues.filter(i => !prevIssueNumbers.has(i.number)).map(i => i.number),
    updatedIssues: currentIssues.filter(i =>
      prevIssueNumbers.has(i.number) &&
      prevIssueUpdates.get(i.number) !== i.updatedAt
    ).map(i => i.number),
    newPrs: currentPrs.filter(p => !prevPrNumbers.has(p.number)).map(p => p.number),
    updatedPrs: currentPrs.filter(p =>
      prevPrNumbers.has(p.number) &&
      prevPrUpdates.get(p.number) !== p.updatedAt
    ).map(p => p.number),
    closedIssues: Array.from(prevIssueNumbers).filter(n => !currentIssueNumbers.has(n)) as number[],
    closedPrs: Array.from(prevPrNumbers).filter(n => !currentPrNumbers.has(n)) as number[],
  };
}

export function main() {
  const args = process.argv.slice(2);
  const keepExisting = hasFlag(args, '--keep');
  const computeDeltaMode = hasFlag(args, '--delta');

  const configPathArg = getArgValue(args, '--config') ?? '.github/maintainer/config.json';
  const configResult = loadConfig(configPathArg);
  let config = configResult.config;

  if (configResult.warnings.length) {
    for (const warning of configResult.warnings) {
      console.warn(`Warning: ${warning}`);
    }
  }

  const datetimeArg = getArgValue(args, '--datetime');
  const datetime = datetimeArg ? sanitizeDatetime(datetimeArg) : getDatetimeString();
  const generatedAt = new Date().toISOString();
  const now = generatedAt;

  const { owner, repo } = getRepo();

  const derivedPath = path.resolve('.github/maintainer/semantics.generated.json');
  const derived = deriveRepoOverrides(process.cwd(), config);
  const derivedWrite = writeDerivedConfigFile(derivedPath, derived);
  config = mergeWithBase(config, derived.overrides);

  const reportsRoot = path.resolve(config.reportsDir);
  const baseDir = path.join(reportsRoot, datetime);
  const dataDir = path.join(baseDir, 'data');
  const issueDir = path.join(baseDir, 'items', 'issues');
  const prDir = path.join(baseDir, 'items', 'prs');
  const maintainerDir = path.resolve('.github/maintainer');
  const notesDir = path.join(maintainerDir, 'notes');
  const workDir = path.join(maintainerDir, 'work');
  const indexDir = path.join(maintainerDir, 'index');

  const stateFilePath = path.resolve(config.stateFile);
  let previousLabel: string | null = null;
  let delta: ReturnType<typeof computeDeltaFromState> | null = null;

  if (computeDeltaMode) {
    const previousState = readState(stateFilePath);
    if (previousState) {
      previousLabel = previousState.lastRunAt;
    } else {
      const previousDir = findLatestReportDir(reportsRoot);
      if (previousDir) {
        const previousPath = path.join(reportsRoot, previousDir);
        previousLabel = path.relative(process.cwd(), previousPath) || previousPath;
      }
    }
  }

  if (fs.existsSync(baseDir) && !keepExisting) {
    fs.rmSync(baseDir, { recursive: true, force: true });
  }

  ensureDir(dataDir);
  ensureDir(issueDir);
  ensureDir(prDir);
  ensureMaintainerState(maintainerDir);
  ensureWorkspace(notesDir);
  ensureWorkspace(indexDir);
  ensureWorkFiles(workDir);

  console.log(`Fetching data from ${owner}/${repo}...`);

  const issuePages = runGraphql<IssuePage>(ISSUE_QUERY, { owner, repo });
  const prPages = runGraphql<PrPage>(PR_QUERY, { owner, repo });

  const issuesRaw = issuePages.flatMap((page) => page.data.repository.issues.nodes);
  const prsRaw = prPages.flatMap((page) => page.data.repository.pullRequests.nodes);

  console.log(`Found ${issuesRaw.length} issues and ${prsRaw.length} PRs`);

  const issues = normalizeIssues(issuesRaw, now, config).sort((a, b) => b.priorityScore - a.priorityScore);
  const prs = normalizePullRequests(prsRaw, now, config).sort((a, b) => b.priorityScore - a.priorityScore);

  buildMentionedByRelations(issues, prs);
  enrichPullRequestsWithIssueSignals(prs, issues, config);
  const contributors = buildContributorProfiles(issues, prs);

  if (computeDeltaMode) {
    const previousState = readState(stateFilePath);
    if (previousState) {
      delta = computeDeltaFromState(issues, prs, previousState);
    } else {
      const previousDir = findLatestReportDir(reportsRoot);
      if (previousDir) {
        const previousDataPath = path.join(reportsRoot, previousDir, 'data');
        delta = computeDeltaFromPreviousReport(issues, prs, previousDataPath);
      }
    }
  }

  writeJson(path.join(dataDir, 'issues.json'), {
    generatedAt,
    owner,
    repo,
    count: issues.length,
    issues,
  });

  writeJson(path.join(dataDir, 'prs.json'), {
    generatedAt,
    owner,
    repo,
    count: prs.length,
    pullRequests: prs,
  });

  writeJson(path.join(dataDir, 'contributors.json'), {
    generatedAt,
    owner,
    repo,
    count: contributors.size,
    contributors: Object.fromEntries(
      Array.from(contributors.entries()).map(([k, v]) => [k, {
        ...v,
        associationTypes: Array.from(v.associationTypes),
      }])
    ),
  });

  const toNumber = (value: unknown): number | undefined => {
    if (typeof value === 'number') return value;
    if (typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value))) return Number(value);
    return undefined;
  };

  for (const issue of issues) {
    const filePath = path.join(issueDir, `ISSUE-${issue.number}.md`);
    const note = readOrCreateNote(notesDir, issue, generatedAt, config);
    const noteBody = note.body.trim();
    const noteSection = noteBody ? `## Maintainer Notes (Persistent)\n${noteBody}\n` : '';
    fs.writeFileSync(filePath, summarizeIssue(issue) + '\n' + noteSection, 'utf8');
  }

  for (const pr of prs) {
    const filePath = path.join(prDir, `PR-${pr.number}.md`);
    const note = readOrCreateNote(notesDir, pr, generatedAt, config);
    const fm = note.frontmatter;
    const autoScore = toNumber(fm.implementation_score_auto) ?? pr.implementationScoreAuto;
    const finalScore = toNumber(fm.implementation_score_final) ?? pr.implementationScoreFinal;
    const agentScore = toNumber(fm.agent_score) ?? pr.agentScore;
    pr.implementationScoreAuto = autoScore;
    pr.implementationScoreFinal = finalScore;
    pr.implementationTierAuto = (fm.implementation_tier_auto as typeof pr.implementationTierAuto) ?? pr.implementationTierAuto;
    pr.implementationTierFinal = (fm.implementation_tier_final as typeof pr.implementationTierFinal) ?? pr.implementationTierFinal;
    pr.agentScore = agentScore;
    pr.agentConfidence = typeof fm.agent_confidence === 'string' ? fm.agent_confidence : pr.agentConfidence;
    pr.agentRationale = typeof fm.agent_rationale === 'string' ? fm.agent_rationale : pr.agentRationale;
    pr.relationshipOverlap = toNumber(fm.relationship_overlap) ?? pr.relationshipOverlap;
    pr.relationshipQualityAuto = (fm.relationship_quality_auto as typeof pr.relationshipQualityAuto) ?? pr.relationshipQualityAuto;
    pr.relationshipQualityFinal = (fm.relationship_quality_final as typeof pr.relationshipQualityFinal) ?? pr.relationshipQualityFinal;
    const noteBody = note.body.trim();
    const noteSection = noteBody ? `## Maintainer Notes (Persistent)\n${noteBody}\n` : '';
    fs.writeFileSync(filePath, summarizePullRequest(pr) + '\n' + noteSection, 'utf8');
  }

  const reportLabel = path.relative(process.cwd(), baseDir) || baseDir;

  writeText(
    path.join(baseDir, 'executive-summary.md'),
    generateExecutiveSummary(
      reportLabel,
      generatedAt,
      owner,
      repo,
      issues,
      prs,
      contributors,
      config.staleDays.issues,
      config.staleDays.prs
    )
  );

  writeText(
    path.join(baseDir, 'triage.md'),
    generateTriageTemplate(generatedAt, owner, repo, issues, prs)
  );

  writeText(
    path.join(baseDir, 'agent-briefs.md'),
    generateAgentBriefsTemplate(generatedAt, owner, repo)
  );

  writeText(
    path.join(baseDir, 'agent-prompts.md'),
    generateAgentPromptsTemplate(generatedAt, owner, repo)
  );

  writeText(
    path.join(baseDir, 'contributors.md'),
    generateContributorsSummary(contributors)
  );

  if (delta && computeDeltaMode) {
    const previous = previousLabel ?? 'unknown';
    writeText(
      path.join(baseDir, 'delta.md'),
      generateDeltaReport(delta, previous, generatedAt)
    );
  }

  const readmeLines = [
    '# Maintenance Report',
    '',
    `Repository: ${owner}/${repo}`,
    `Generated: ${generatedAt}`,
    `Report folder: ${reportLabel}`,
    `Open issues: ${issues.length}`,
    `Open PRs: ${prs.length}`,
    `Unique contributors: ${contributors.size}`,
    `Config: ${path.relative(process.cwd(), configResult.path) || configResult.path}`,
    '',
    '## Files',
    '',
    '- `executive-summary.md` - Priority queue, actionability, duplicates',
    '- `triage.md` - Prioritized list for triage',
    '- `agent-briefs.md` - Task briefs for coding agents',
    '- `agent-prompts.md` - Prompt drafts derived from briefs',
    '- `contributors.md` - Contributor profiles',
    delta ? '- `delta.md` - Changes since last run' : '',
    '- `data/issues.json` - Raw issue data',
    '- `data/prs.json` - Raw PR data',
    '- `data/contributors.json` - Contributor data',
    '- `items/issues/ISSUE-*.md` - Per-issue analysis (includes persistent notes)',
    '- `items/prs/PR-*.md` - Per-PR analysis (includes persistent notes)',
    '- `run-summary.md` - Work files, note counts, git summary',
    '',
    '## Next Steps',
    '',
    '1. Review `executive-summary.md` for quick overview',
    '2. Fill in priorities in `triage.md`',
    '3. Create agent briefs for top items',
    '4. Draft prompts in `agent-prompts.md`',
    '5. Update `.github/maintainer/` with decisions',
    '',
  ].filter(Boolean);

  writeText(path.join(baseDir, 'README.md'), readmeLines.join('\n'));

  const workFiles = listWorkFiles(workDir);
  const gitSummary = getGitSummary();
  const runSummaryLines = [
    '# Run Summary',
    '',
    `Generated: ${generatedAt}`,
    `Report folder: ${reportLabel}`,
    `Config: ${path.relative(process.cwd(), configResult.path) || configResult.path}`,
    '',
    '## Work Files',
    ...(workFiles.length ? workFiles.map((file) => `- ${file.path} (updated ${file.updatedAt})`) : ['- None']),
    '',
    '## Notes',
    `- Issues: ${issues.length}`,
    `- PRs: ${prs.length}`,
    `- Derived config: ${path.relative(process.cwd(), derivedPath)} (${derivedWrite.wrote ? 'updated' : 'unchanged'})`,
    derived.sources.length ? `- Derived sources: ${derived.sources.length}` : '- Derived sources: none',
    '',
    '## Git Status',
    gitSummary ? gitSummary.status : '- Git status unavailable',
    '',
    '## Git Diff (.github/maintainer)',
    gitSummary && gitSummary.diffStat ? gitSummary.diffStat : '- No diff or unavailable',
    '',
    '## Untracked (.github/maintainer)',
    gitSummary && gitSummary.untracked.length ? gitSummary.untracked.map((file) => `- ${file}`).join('\n') : '- None',
    '',
  ].filter(Boolean);
  writeText(path.join(baseDir, 'run-summary.md'), runSummaryLines.join('\n'));

  const runsLogPath = path.join(maintainerDir, 'runs.md');
  const runLine = `- ${generatedAt} | ${reportLabel} | issues:${issues.length} prs:${prs.length}`;
  fs.appendFileSync(runsLogPath, `${runLine}\n`, 'utf8');

  const titleMap = new Map<string, string>();
  for (const issue of issues) titleMap.set(`issue:${issue.number}`, issue.title);
  for (const pr of prs) titleMap.set(`pr:${pr.number}`, pr.title);
  const indexItems = buildIndexFromNotes(notesDir, titleMap);
  writeJson(path.join(indexDir, 'items.json'), {
    generatedAt,
    count: indexItems.length,
    items: indexItems,
  });

  const graph = buildGraph(issues, prs);
  writeJson(path.join(indexDir, 'graph.json'), {
    generatedAt,
    nodes: graph.nodes,
    edges: graph.edges,
  });

  const state = createState(datetime, reportLabel, issues, prs);
  writeState(stateFilePath, state);
  writeJson(path.join(dataDir, 'state.json'), state);

  writeText(path.join(reportsRoot, 'LATEST'), `${reportLabel}`);

  console.log(`\nReport generated: ${reportLabel}`);
  console.log(`  - ${issues.length} issues`);
  console.log(`  - ${prs.length} PRs`);
  console.log(`  - ${contributors.size} contributors`);
  if (delta) {
    console.log(`  - Delta: ${delta.newIssues.length} new issues, ${delta.updatedIssues.length} updated, ${delta.closedIssues.length} closed`);
    console.log(`  - Delta: ${delta.newPrs.length} new PRs, ${delta.updatedPrs.length} updated, ${delta.closedPrs.length} closed`);
  }
}
