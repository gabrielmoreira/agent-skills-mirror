import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export function ensureWorkspace(baseDir: string) {
  fs.mkdirSync(baseDir, { recursive: true });
}

function writeIfMissing(filePath: string, content: string) {
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, `${content}\n`, 'utf8');
  }
}

export function ensureWorkFiles(workDir: string) {
  ensureWorkspace(workDir);

  writeIfMissing(
    path.join(workDir, 'queue.md'),
    [
      '# Maintainer Queue',
      '',
      '- TODO: Prioritized items for implementation',
    ].join('\n')
  );

  writeIfMissing(
    path.join(workDir, 'agent-briefs.md'),
    [
      '# Agent Briefs',
      '',
      'Use this file to write task briefs derived from triage.',
    ].join('\n')
  );

  writeIfMissing(
    path.join(workDir, 'agent-prompts.md'),
    [
      '# Agent Prompts',
      '',
      'Use this file to draft executable prompts for each brief.',
    ].join('\n')
  );

  writeIfMissing(
    path.join(workDir, 'opportunities.md'),
    [
      '# Opportunity Backlog',
      '',
      '- TODO: Docs, onboarding, hygiene, UX improvements',
    ].join('\n')
  );
}

export function listWorkFiles(workDir: string): Array<{ path: string; updatedAt: string }> {
  if (!fs.existsSync(workDir)) return [];
  const entries = fs.readdirSync(workDir);
  return entries.map((entry) => {
    const fullPath = path.join(workDir, entry);
    const stats = fs.statSync(fullPath);
    return {
      path: path.relative(process.cwd(), fullPath),
      updatedAt: stats.mtime.toISOString(),
    };
  });
}

const STATE_FILES = [
  'context.md',
  'decisions.md',
  'contributors.md',
  'patterns.md',
  'standing-rules.md',
  'runs.md',
];

function loadRepoStateTemplate(): Record<string, string> {
  const fallback: Record<string, string> = {
    'context.md': `# Project Context

## Vision
[One paragraph: what is this project and why does it exist?]

## Current Priorities
1. [Top priority]
2. [Second priority]
3. [Third priority]

## Success Metrics
- [Adoption goal or usage signal]
- [Quality goal: reliability, docs, tests, etc.]

## Areas

| Area | Status | Notes |
|------|--------|-------|
| \`src/core/\` | Stable | High scrutiny for changes |
| \`src/cli/\` | Active | Moderate churn okay |
| \`docs/\` | Needs work | Contributions welcome |

## Contribution Guidelines
- [Key guideline 1]
- [Key guideline 2]

## Tone
[How should responses sound? Formal? Casual? Technical?]

## Out of Scope
- [Thing we explicitly don't want]
- [Another thing]
`,
    'decisions.md': `# Decision Log

## YYYY-MM

### [ISSUE:XX] Title
**Date:** YYYY-MM-DD
**Decision:** [Implemented / Deferred / Closed]
**Reasoning:** [Why this decision was made]
`,
    'contributors.md': `# Contributor Notes

## Active Contributors

### @username
- **First seen:** YYYY-MM-DD
- **Contributions:** [X PRs, Y issues]
- **Strengths:** [Notable qualities]
- **Notes:** [Any relevant context]

## Former Contributors

[Record contributors who are no longer active]
`,
    'patterns.md': `# Observed Patterns

## Recurring Issues

### [Pattern Name]
- **First seen:** YYYY-MM-DD
- **Frequency:** [X duplicate reports]
- **Root cause:** [What causes this]
- **Resolution:** [How it was fixed]
- **Prevention:** [How to prevent recurrence]

## Contributor Patterns

- [Observations about contributor behavior]

## Codebase Patterns

- [Observations about where bugs cluster, coverage gaps, etc.]
`,
    'standing-rules.md': `# Standing Rules

## Stale Policy

| Condition | Days | Action |
|-----------|------|--------|
| Issue waiting on reporter | 30 | Comment asking for update |
| Issue waiting on reporter | 60 | Close as stale |
| PR waiting on author | 30 | Close as stale |

## Auto-Labels

| Condition | Label |
|-----------|-------|
| PR touches \`src/core/\` | \`core\` |
| Issue mentions "windows" | \`platform:windows\` |
| First-time contributor | \`first-contribution\` |

## External PR Handling

- Never merge external PRs
- Extract intent and implement fixes directly
- Close PRs with explanation and credit
`,
    'runs.md': `# Run Ledger

| Date | Report Path | Summary |
|------|-------------|---------|
`,
  };

  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    const templatePath = path.resolve(here, '..', '..', 'references', 'repo-state-template.md');
    const content = fs.readFileSync(templatePath, 'utf8');
    const result: Record<string, string> = {};
    for (const fileName of STATE_FILES) {
      const section = extractCodeBlockAfterHeading(content, `## ${fileName}`);
      if (section) {
        result[fileName] = section;
      }
    }
    return { ...fallback, ...result };
  } catch {
    return fallback;
  }
}

function extractCodeBlockAfterHeading(content: string, heading: string): string | null {
  const index = content.indexOf(heading);
  if (index === -1) return null;
  const after = content.slice(index + heading.length);
  const fenceStart = after.indexOf('```');
  if (fenceStart === -1) return null;
  const fenceEnd = after.indexOf('```', fenceStart + 3);
  if (fenceEnd === -1) return null;
  const block = after.slice(fenceStart + 3, fenceEnd);
  const lines = block.split('\n');
  if (lines.length && lines[0].trim().length <= 10) {
    lines.shift();
  }
  const text = lines.join('\n').trimEnd();
  return text ? `${text}\n` : null;
}

export function ensureMaintainerState(maintainerDir: string) {
  ensureWorkspace(maintainerDir);
  const template = loadRepoStateTemplate();
  for (const fileName of STATE_FILES) {
    const filePath = path.join(maintainerDir, fileName);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, `${template[fileName] ?? ''}\n`, 'utf8');
    }
  }

  // Initialize state.json if missing
  const statePath = path.join(maintainerDir, 'state.json');
  if (!fs.existsSync(statePath)) {
    const initialState = {
      schemaVersion: 1,
      lastRunAt: null,
      lastReportDir: null,
      issueHashes: {},
      prHashes: {},
    };
    fs.writeFileSync(statePath, `${JSON.stringify(initialState, null, 2)}\n`, 'utf8');
  }
}
