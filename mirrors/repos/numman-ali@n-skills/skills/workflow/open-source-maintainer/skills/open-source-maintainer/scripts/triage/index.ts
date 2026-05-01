import fs from 'node:fs';
import path from 'node:path';

import { NoteFrontmatter, parseFrontmatter } from './notes';

export type IndexItem = {
  id: number;
  type: 'issue' | 'pr';
  title: string;
  actionability: string;
  priorityScore: number;
  implementationScoreAuto?: number;
  implementationScoreFinal?: number;
  implementationTierAuto?: string;
  implementationTierFinal?: string;
  agentScore?: number;
  agentConfidence?: string;
  relationshipScore?: number;
  relationshipOverlap?: number;
  relationshipQualityAuto?: string;
  relationshipQualityFinal?: string;
  sentimentScore?: number;
  needsInfoScore?: number;
  needsInfoSignals?: string[];
  linkedIssues?: number[];
  labels: string[];
  notePath: string;
  lastSeenAt?: string;
  lastReviewedAt?: string;
};

function readNoteFrontmatter(notePath: string): NoteFrontmatter | null {
  const content = fs.readFileSync(notePath, 'utf8');
  const parsed = parseFrontmatter(content);
  return parsed.frontmatter;
}

function toNumber(value: unknown): number | undefined {
  if (typeof value === 'number') return value;
  if (typeof value === 'string' && value.trim() !== '' && !Number.isNaN(Number(value))) return Number(value);
  return undefined;
}

function toStringArray(value: unknown): string[] {
  if (Array.isArray(value)) return value.map((entry) => String(entry));
  if (typeof value === 'string' && value.trim()) return [value.trim()];
  return [];
}

function toNumberArray(value: unknown): number[] {
  if (Array.isArray(value)) return value.map((entry) => Number(entry)).filter((num) => !Number.isNaN(num));
  return [];
}

export function buildIndexFromNotes(baseDir: string, titles: Map<string, string>): IndexItem[] {
  const notesDir = path.resolve(baseDir);
  const items: IndexItem[] = [];

  if (!fs.existsSync(notesDir)) return items;

  const walk = (dir: string) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath);
      } else if (entry.name.endsWith('.md')) {
        const frontmatter = readNoteFrontmatter(fullPath);
        if (!frontmatter) continue;
        const type = (frontmatter.type === 'pr' ? 'pr' : 'issue') as 'issue' | 'pr';
        const id = toNumber(frontmatter.id) ?? 0;
        if (!id) continue;
        const titleKey = `${type}:${id}`;
        items.push({
          id,
          type,
          title: titles.get(titleKey) ?? '',
          actionability: String(frontmatter.actionability ?? ''),
          priorityScore: toNumber(frontmatter.priority_score) ?? 0,
          implementationScoreAuto: toNumber(frontmatter.implementation_score_auto),
          implementationScoreFinal: toNumber(frontmatter.implementation_score_final),
          implementationTierAuto: frontmatter.implementation_tier_auto ? String(frontmatter.implementation_tier_auto) : undefined,
          implementationTierFinal: frontmatter.implementation_tier_final ? String(frontmatter.implementation_tier_final) : undefined,
          agentScore: toNumber(frontmatter.agent_score),
          agentConfidence: frontmatter.agent_confidence ? String(frontmatter.agent_confidence) : undefined,
          relationshipScore: toNumber(frontmatter.relationship_score),
          relationshipOverlap: toNumber(frontmatter.relationship_overlap),
          relationshipQualityAuto: frontmatter.relationship_quality_auto ? String(frontmatter.relationship_quality_auto) : undefined,
          relationshipQualityFinal: frontmatter.relationship_quality_final ? String(frontmatter.relationship_quality_final) : undefined,
          sentimentScore: toNumber(frontmatter.sentiment_score),
          needsInfoScore: toNumber(frontmatter.needs_info_score),
          needsInfoSignals: toStringArray(frontmatter.needs_info_signals),
          linkedIssues: toNumberArray(frontmatter.linked_issues),
          labels: toStringArray(frontmatter.labels),
          notePath: path.relative(process.cwd(), fullPath),
          lastSeenAt: frontmatter.last_seen_at ? String(frontmatter.last_seen_at) : undefined,
          lastReviewedAt: frontmatter.last_reviewed_at ? String(frontmatter.last_reviewed_at) : undefined,
        });
      }
    }
  };

  walk(notesDir);
  return items.sort((a, b) => a.type.localeCompare(b.type) || a.id - b.id);
}
