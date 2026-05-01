import fs from 'node:fs';
import path from 'node:path';

import { MaintainerConfig, NormalizedIssue, NormalizedPullRequest } from './types';

const FRONTMATTER_REGEX = /^---\n([\s\S]*?)\n---\n?/;

export type NoteFrontmatter = Record<string, unknown>;

export type NoteFile = {
  frontmatter: NoteFrontmatter;
  body: string;
};

const FRONTMATTER_ORDER = [
  'id',
  'type',
  'status',
  'actionability',
  'priority_score',
  'implementation_score_auto',
  'implementation_score_final',
  'implementation_tier_auto',
  'implementation_tier_final',
  'agent_score',
  'agent_confidence',
  'agent_rationale',
  'relationship_score',
  'relationship_overlap',
  'relationship_quality_auto',
  'relationship_quality_final',
  'sentiment_score',
  'needs_info_score',
  'needs_info_signals',
  'linked_issues',
  'labels',
  'last_seen_at',
  'last_reviewed_at',
  'next_review_at',
  'decisions',
  'tags',
  'owner',
];

function parseScalar(value: string): unknown {
  const trimmed = value.trim();
  if (!trimmed) return '';
  if (trimmed === 'true') return true;
  if (trimmed === 'false') return false;
  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    const inner = trimmed.slice(1, -1).trim();
    if (!inner) return [];
    return inner.split(',').map((entry) => parseScalar(entry.trim()));
  }
  const numberValue = Number(trimmed);
  if (!Number.isNaN(numberValue) && trimmed === String(numberValue)) return numberValue;
  return trimmed.replace(/^"|"$/g, '').replace(/^'|'$/g, '');
}

function serializeValue(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map((entry) => serializeValue(entry)).join(', ')}]`;
  }
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  if (typeof value === 'number') return `${value}`;
  if (value === null || value === undefined) return '';
  return `${value}`;
}

function toNumber(value: unknown): number | undefined {
  if (typeof value === 'number') return value;
  if (typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value))) return Number(value);
  return undefined;
}

function tierFromScore(score: number, config: MaintainerConfig): 'strong' | 'medium' | 'weak' {
  if (score >= config.implementation.tierThresholds.strong) return 'strong';
  if (score >= config.implementation.tierThresholds.medium) return 'medium';
  return 'weak';
}

function normalizeConfidence(value: unknown): 'high' | 'medium' | 'low' | 'unset' {
  if (typeof value !== 'string') return 'unset';
  const normalized = value.trim().toLowerCase();
  if (normalized === 'high') return 'high';
  if (normalized === 'medium') return 'medium';
  if (normalized === 'low') return 'low';
  return 'unset';
}

function computeFinalScore(
  autoScore: number,
  agentScore: number,
  agentConfidence: 'high' | 'medium' | 'low' | 'unset',
  config: MaintainerConfig
): number {
  const weights = config.implementation;
  const confidenceMultiplier = weights.agentConfidenceMultipliers[agentConfidence] ?? weights.agentConfidenceMultipliers.unset;
  const adjustedAgentScore = agentScore * weights.agentScoreWeight * confidenceMultiplier;
  return Math.max(weights.scoreFloor, Math.round(autoScore + adjustedAgentScore));
}

export function parseFrontmatter(content: string): NoteFile {
  const match = content.match(FRONTMATTER_REGEX);
  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const raw = match[1] ?? '';
  const frontmatter: NoteFrontmatter = {};

  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const separatorIndex = line.indexOf(':');
    if (separatorIndex === -1) continue;
    const key = line.slice(0, separatorIndex).trim();
    const value = line.slice(separatorIndex + 1).trim();
    frontmatter[key] = parseScalar(value);
  }

  const body = content.slice(match[0].length);
  return { frontmatter, body };
}

export function serializeFrontmatter(frontmatter: NoteFrontmatter): string {
  const keys = new Set(Object.keys(frontmatter));
  const ordered = [...FRONTMATTER_ORDER.filter((key) => keys.has(key))];
  for (const key of keys) {
    if (!ordered.includes(key)) ordered.push(key);
  }

  const lines = ['---'];
  for (const key of ordered) {
    lines.push(`${key}: ${serializeValue(frontmatter[key])}`);
  }
  lines.push('---');
  return `${lines.join('\n')}\n`;
}

export function notePath(baseDir: string, type: 'issue' | 'pr', id: number): string {
  const shard = String(Math.floor(id / 1000)).padStart(3, '0');
  const fileName = `${type === 'issue' ? 'ISSUE' : 'PR'}-${id}.md`;
  return path.join(baseDir, type === 'issue' ? 'issues' : 'prs', shard, fileName);
}

export function ensureNoteDir(filePath: string) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function defaultBody(type: 'issue' | 'pr'): string {
  if (type === 'issue') {
    return [
      '## Intent',
      '- TODO: Summarize the reporter intent and underlying need.',
      '',
      '## Analysis',
      '- TODO: Root cause, severity, scope.',
      '',
      '## Proposed Action',
      '- TODO: Implement, ask for info, close, defer.',
      '',
      '## Draft Response (requires approval)',
      '- TODO: Draft the public response.',
      '',
    ].join('\n');
  }

  return [
    '## Intent',
    '- TODO: Summarize what the PR tries to solve and how.',
    '',
    '## Relationship Quality',
    '- TODO: Does this solve linked issues? Any mismatch? Update relationship_quality_final if needed.',
    '',
    '## Agent Score Adjustment',
    '- TODO: Adjust score based on your judgment. Update agent_score, agent_confidence, agent_rationale.',
    '',
    '## Implementation Plan',
    '- TODO: How you will implement the fix directly.',
    '',
    '## Draft Response (requires approval)',
    '- TODO: Draft the closing response with credit.',
    '',
  ].join('\n');
}

export function readOrCreateNote(
  baseDir: string,
  item: NormalizedIssue | NormalizedPullRequest,
  now: string,
  config: MaintainerConfig
): NoteFile {
  const type = 'itemType' in item ? 'issue' : 'pr';
  const filePath = notePath(baseDir, type, item.number);

  if (!fs.existsSync(filePath)) {
    ensureNoteDir(filePath);
    const frontmatter = buildFrontmatter(item, now, {}, config);
    const body = defaultBody(type);
    const content = serializeFrontmatter(frontmatter) + body;
    fs.writeFileSync(filePath, content, 'utf8');
    return { frontmatter, body };
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const existing = parseFrontmatter(content);
  const merged = buildFrontmatter(item, now, existing.frontmatter, config);
  const mergedContent = serializeFrontmatter(merged) + existing.body;
  fs.writeFileSync(filePath, mergedContent, 'utf8');
  return { frontmatter: merged, body: existing.body };
}

function buildFrontmatter(
  item: NormalizedIssue | NormalizedPullRequest,
  now: string,
  existing: NoteFrontmatter,
  config: MaintainerConfig
): NoteFrontmatter {
  const sanitized: NoteFrontmatter = { ...existing };
  delete sanitized.implementation_score;
  delete sanitized.implementation_tier;

  const base: NoteFrontmatter = {
    ...sanitized,
    id: item.number,
    type: 'itemType' in item ? 'issue' : 'pr',
    status: 'open',
    actionability: item.actionability,
    priority_score: item.priorityScore,
    sentiment_score: item.sentimentScore,
    needs_info_score: item.needsInfoScore,
    needs_info_signals: item.needsInfoSignals,
    labels: item.labels,
    last_seen_at: now,
  };

  if ('itemType' in item) {
    return base;
  }

  const agentScore = toNumber(existing.agent_score) ?? 0;
  const agentConfidence = normalizeConfidence(existing.agent_confidence);
  const agentRationale = typeof existing.agent_rationale === 'string' ? existing.agent_rationale : '';

  const autoScore = item.implementationScoreAuto;
  const finalScore = computeFinalScore(autoScore, agentScore, agentConfidence, config);
  const existingRelationshipQuality = typeof existing.relationship_quality_final === 'string'
    ? existing.relationship_quality_final
    : '';
  const hasAgentOverride = agentScore !== 0 || agentConfidence !== 'unset' || agentRationale.trim().length > 0;
  const relationshipQualityFinal = (!hasAgentOverride && existingRelationshipQuality !== item.relationshipQualityAuto)
    ? item.relationshipQualityAuto
    : (existingRelationshipQuality || item.relationshipQualityAuto);

  return {
    ...base,
    implementation_score_auto: autoScore,
    implementation_score_final: finalScore,
    implementation_tier_auto: tierFromScore(autoScore, config),
    implementation_tier_final: tierFromScore(finalScore, config),
    agent_score: agentScore,
    agent_confidence: agentConfidence,
    agent_rationale: agentRationale,
    relationship_score: item.relationshipScore,
    relationship_overlap: item.relationshipOverlap,
    relationship_quality_auto: item.relationshipQualityAuto,
    relationship_quality_final: relationshipQualityFinal,
    linked_issues: item.linkedIssues,
  };
}
