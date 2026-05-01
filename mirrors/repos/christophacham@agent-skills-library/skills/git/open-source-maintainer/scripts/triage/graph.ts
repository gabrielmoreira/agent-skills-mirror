import { NormalizedIssue, NormalizedPullRequest } from './types';

export type GraphNode = {
  id: string;
  type: 'issue' | 'pr';
  title: string;
  priorityScore: number;
  implementationScore?: number;
  actionability: string;
};

export type GraphEdge = {
  from: string;
  to: string;
  type: 'mentions' | 'mentioned_by' | 'possible_duplicate';
};

export type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export function buildGraph(issues: NormalizedIssue[], prs: NormalizedPullRequest[]): GraphData {
  const nodes: GraphNode[] = [];
  const edges: GraphEdge[] = [];

  for (const issue of issues) {
    nodes.push({
      id: `issue:${issue.number}`,
      type: 'issue',
      title: issue.title,
      priorityScore: issue.priorityScore,
      actionability: issue.actionability,
    });

    for (const mention of issue.relations.mentions) {
      edges.push({ from: `issue:${issue.number}`, to: `issue:${mention}`, type: 'mentions' });
    }
    for (const mention of issue.relations.mentionedBy) {
      edges.push({ from: `issue:${mention}`, to: `issue:${issue.number}`, type: 'mentioned_by' });
    }
    for (const dup of issue.relations.possibleDuplicates) {
      edges.push({ from: `issue:${issue.number}`, to: `issue:${dup}`, type: 'possible_duplicate' });
    }
  }

  for (const pr of prs) {
    nodes.push({
      id: `pr:${pr.number}`,
      type: 'pr',
      title: pr.title,
      priorityScore: pr.priorityScore,
      implementationScore: pr.implementationScoreFinal,
      actionability: pr.actionability,
    });

    for (const mention of pr.relations.mentions) {
      edges.push({ from: `pr:${pr.number}`, to: `issue:${mention}`, type: 'mentions' });
    }
    for (const mention of pr.relations.mentionedBy) {
      edges.push({ from: `issue:${mention}`, to: `pr:${pr.number}`, type: 'mentioned_by' });
    }
    for (const dup of pr.relations.possibleDuplicates) {
      edges.push({ from: `pr:${pr.number}`, to: `pr:${dup}`, type: 'possible_duplicate' });
    }
  }

  return { nodes, edges };
}
