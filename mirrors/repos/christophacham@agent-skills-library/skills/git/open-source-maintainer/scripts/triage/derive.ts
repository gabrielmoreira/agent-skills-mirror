import fs from 'node:fs';
import path from 'node:path';

import { MaintainerConfig } from './types';
import { writeJson } from './utils';

type DerivedResult = {
  overrides: Partial<MaintainerConfig>;
  sources: string[];
};

type DerivedFile = {
  schemaVersion: 1;
  generatedAt: string;
  sources: string[];
  overrides: Partial<MaintainerConfig>;
};

const ISSUE_TEMPLATE_DIR = path.join('.github', 'ISSUE_TEMPLATE');
const PR_TEMPLATE_FILES = [
  path.join('.github', 'PULL_REQUEST_TEMPLATE.md'),
  path.join('.github', 'pull_request_template.md'),
];
const PR_TEMPLATE_DIR = path.join('.github', 'PULL_REQUEST_TEMPLATE');
const CONTRIBUTING_FILES = [
  'CONTRIBUTING.md',
  path.join('.github', 'CONTRIBUTING.md'),
];

const CATEGORY_KEYWORDS: Record<string, string[]> = {
  repro: ['steps to reproduce', 'repro', 'reproduction'],
  expected: ['expected behavior', 'expected result'],
  actual: ['actual behavior', 'actual result'],
  environment: ['environment', 'os', 'operating system', 'platform'],
  version: ['version', 'openskills version', 'node version'],
  logs: ['logs', 'stack trace', 'error output'],
  testPlan: ['test plan', 'testing', 'tests run'],
};

const INTENT_KEYWORDS: Record<string, string[]> = {
  bug: ['bug report', 'bug'],
  feature: ['feature request', 'feature'],
  question: ['question'],
  support: ['support', 'help'],
  meta: ['governance', 'roadmap', 'discussion'],
};

const ENV_TOKENS = ['windows', 'mac', 'macos', 'linux', 'ubuntu', 'debian', 'node', 'npm', 'pnpm', 'yarn'];

function readFileIfExists(filePath: string): string | null {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

function collectTemplateFiles(repoRoot: string): string[] {
  const files: string[] = [];

  const issueDir = path.join(repoRoot, ISSUE_TEMPLATE_DIR);
  if (fs.existsSync(issueDir)) {
    for (const entry of fs.readdirSync(issueDir)) {
      if (entry.endsWith('.md') || entry.endsWith('.yml') || entry.endsWith('.yaml')) {
        files.push(path.join(issueDir, entry));
      }
    }
  }

  for (const file of PR_TEMPLATE_FILES) {
    const fullPath = path.join(repoRoot, file);
    if (fs.existsSync(fullPath)) files.push(fullPath);
  }

  const prDir = path.join(repoRoot, PR_TEMPLATE_DIR);
  if (fs.existsSync(prDir)) {
    for (const entry of fs.readdirSync(prDir)) {
      if (entry.endsWith('.md')) {
        files.push(path.join(prDir, entry));
      }
    }
  }

  for (const file of CONTRIBUTING_FILES) {
    const fullPath = path.join(repoRoot, file);
    if (fs.existsSync(fullPath)) files.push(fullPath);
  }

  return Array.from(new Set(files));
}

function extractMarkdownPhrases(content: string): string[] {
  const phrases: string[] = [];
  const lines = content.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (/^[-*]\s*\[[ xX]\]/.test(trimmed)) continue;
    if (trimmed.startsWith('#')) {
      phrases.push(sanitizePhrase(trimmed.replace(/^#+\s*/, '')));
      continue;
    }
    if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
      phrases.push(sanitizePhrase(trimmed.replace(/^[-*]\s*/, '')));
      continue;
    }
    if (/^>/.test(trimmed)) continue;
  }
  return phrases;
}

function extractYamlPhrases(content: string): string[] {
  const phrases: string[] = [];
  const lines = content.split('\n');
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const labelMatch = trimmed.match(/^label:\s*(.+)$/i);
    if (labelMatch) {
      phrases.push(sanitizePhrase(labelMatch[1].replace(/^["']|["']$/g, '')));
      continue;
    }
    const idMatch = trimmed.match(/^id:\s*(.+)$/i);
    if (idMatch) {
      phrases.push(sanitizePhrase(idMatch[1].replace(/^["']|["']$/g, '')));
      continue;
    }
  }
  return phrases;
}

function addPhrases(target: Set<string>, phrases: string[]) {
  for (const phrase of phrases) {
    const normalized = phrase.toLowerCase().trim();
    if (!normalized || normalized.length > 180) continue;
    target.add(normalized);
  }
}

function sanitizePhrase(phrase: string): string {
  return phrase
    .replace(/\[[xX ]\]\s*/g, '')
    .replace(/\([^)]*\)/g, '')
    .replace(/^[\[\]xX\s-]+/, '')
    .replace(/[*_`]/g, '')
    .replace(/[：:]\s*$/, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function keywordMatches(phrase: string, keyword: string): boolean {
  if (!keyword) return false;
  if (keyword.length <= 3) {
    const escaped = keyword.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
    return new RegExp(`\\b${escaped}\\b`, 'i').test(phrase);
  }
  return phrase.includes(keyword);
}

function selectPhraseOrKeyword(phrase: string, keyword: string): string {
  const normalized = phrase.trim();
  if (!normalized) return keyword;
  const wordCount = normalized.split(/\s+/).filter(Boolean).length;
  if (wordCount > 6) return keyword;
  if (normalized.length <= 80) return normalized;
  return keyword;
}

function deriveOverridesFromPhrases(phrases: Set<string>, base: MaintainerConfig): Partial<MaintainerConfig> {
  const intentAdds: Record<string, Set<string>> = {
    bug: new Set(),
    feature: new Set(),
    question: new Set(),
    support: new Set(),
    meta: new Set(),
  };
  const needsInfoAdds: Record<string, Set<string>> = {
    repro: new Set(),
    expected: new Set(),
    actual: new Set(),
    environment: new Set(),
    version: new Set(),
    logs: new Set(),
    testPlan: new Set(),
  };
  const envTokens = new Set<string>();

  for (const phrase of phrases) {
    for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
      for (const kw of keywords) {
        if (keywordMatches(phrase, kw)) {
          needsInfoAdds[category].add(selectPhraseOrKeyword(phrase, kw));
          break;
        }
      }
    }
    for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
      for (const kw of keywords) {
        if (keywordMatches(phrase, kw)) {
          intentAdds[intent].add(selectPhraseOrKeyword(phrase, kw));
          break;
        }
      }
    }
    for (const token of ENV_TOKENS) {
      if (keywordMatches(phrase, token)) envTokens.add(token);
    }
  }

  const overrides: Partial<MaintainerConfig> = {
    semantics: {
      intent: {
        bug: Array.from(intentAdds.bug),
        feature: Array.from(intentAdds.feature),
        question: Array.from(intentAdds.question),
        support: Array.from(intentAdds.support),
        meta: Array.from(intentAdds.meta),
      },
      needsInfo: {
        repro: Array.from(needsInfoAdds.repro),
        expected: Array.from(needsInfoAdds.expected),
        actual: Array.from(needsInfoAdds.actual),
        environment: Array.from(needsInfoAdds.environment),
        version: Array.from(needsInfoAdds.version),
        logs: Array.from(needsInfoAdds.logs),
        testPlan: Array.from(needsInfoAdds.testPlan),
      },
      environmentTokens: Array.from(envTokens),
      relationship: {
        linkKeywords: [],
        duplicateHints: [],
      },
      errors: {
        signatures: [],
        keywords: [],
      },
    },
  };

  if (base.semantics && base.semantics.environmentTokens) {
    overrides.semantics!.environmentTokens = Array.from(new Set([...base.semantics.environmentTokens, ...overrides.semantics!.environmentTokens]));
  }

  return overrides;
}

export function deriveRepoOverrides(repoRoot: string, baseConfig: MaintainerConfig): DerivedResult {
  const sources = collectTemplateFiles(repoRoot);
  const phrases = new Set<string>();

  for (const file of sources) {
    const content = readFileIfExists(file);
    if (!content) continue;
    if (file.endsWith('.yml') || file.endsWith('.yaml')) {
      addPhrases(phrases, extractYamlPhrases(content));
    } else {
      addPhrases(phrases, extractMarkdownPhrases(content));
    }
  }

  const overrides = deriveOverridesFromPhrases(phrases, baseConfig);
  return { overrides, sources };
}

export function writeDerivedConfigFile(
  filePath: string,
  derived: DerivedResult
): { wrote: boolean; path: string } {
  const payload: DerivedFile = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    sources: derived.sources,
    overrides: derived.overrides,
  };

  const existing = readFileIfExists(filePath);
  if (existing) {
    try {
      const parsed = JSON.parse(existing) as DerivedFile;
      const same = JSON.stringify(parsed.overrides) === JSON.stringify(payload.overrides) &&
        JSON.stringify(parsed.sources) === JSON.stringify(payload.sources);
      if (same) return { wrote: false, path: filePath };
    } catch {
      // ignore
    }
  }

  const dir = path.dirname(filePath);
  fs.mkdirSync(dir, { recursive: true });
  writeJson(filePath, payload);
  return { wrote: true, path: filePath };
}
