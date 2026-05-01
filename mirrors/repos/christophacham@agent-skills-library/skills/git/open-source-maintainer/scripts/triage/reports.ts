import {
  ContributorProfile,
  DeltaChanges,
  NormalizedIssue,
  NormalizedPullRequest,
  NormalizedReactionCounts,
} from './types';
import { formatReactionCounts } from './utils';

export function summarizeIssue(issue: NormalizedIssue): string {
  const relationsSection = [];
  if (issue.relations.mentions.length > 0) {
    relationsSection.push(`Mentions: ${issue.relations.mentions.map(n => `#${n}`).join(', ')}`);
  }
  if (issue.relations.mentionedBy.length > 0) {
    relationsSection.push(`Mentioned by: ${issue.relations.mentionedBy.map(n => `#${n}`).join(', ')}`);
  }
  if (issue.relations.possibleDuplicates.length > 0) {
    relationsSection.push(`Possible duplicates: ${issue.relations.possibleDuplicates.map(n => `#${n}`).join(', ')}`);
  }

  return [
    `# ISSUE ${issue.number}: ${issue.title}`,
    '',
    `URL: ${issue.url}`,
    `Author: ${issue.author}`,
    `Type: ${issue.itemType}`,
    `Created: ${issue.createdAt} (${issue.ageInDays} days ago)`,
    `Updated: ${issue.updatedAt} (${issue.daysSinceUpdate} days ago)`,
    `Labels: ${issue.labels.length ? issue.labels.join(', ') : 'none'}`,
    `Assignees: ${issue.assignees.length ? issue.assignees.join(', ') : 'none'}`,
    `Comments: ${issue.comments.length} (totalCount=${issue.commentsTotal})`,
    `Reactions: ${formatReactionCounts(issue.reactionTotals)}`,
    `Participants: ${issue.participants.join(', ')}`,
    '',
    '## Analysis',
    `Priority Score: ${issue.priorityScore}`,
    `Sentiment Score: ${issue.sentimentScore}`,
    `Needs-Info Score: ${issue.needsInfoScore}${issue.needsInfoSignals.length ? ` (${issue.needsInfoSignals.join(', ')})` : ''}`,
    `Actionability: ${issue.actionability}`,
    relationsSection.length ? relationsSection.join('\n') : 'No relations detected',
    '',
    '## Comment Index (chronological)',
    ...(issue.comments.length
      ? issue.comments.map((comment) => {
          const reactions = formatReactionCounts(comment.reactions);
          const assoc = comment.authorAssociation ? ` (${comment.authorAssociation})` : '';
          return `- ISSUE:${issue.number}:C:${comment.index} | ${comment.createdAt} | ${comment.author}${assoc} | reactions: ${reactions}`;
        })
      : ['- No comments yet.']),
    '',
    '## Comment Analysis',
    issue.comments.length ? '- TODO: Fill analysis per comment.' : '- No comments to analyze.',
    '',
    '## Agent Review Prompt',
    '- Summarize the user intent and the underlying need.',
    '- Assess sentiment and urgency from comments/reactions.',
    '- Identify duplicates/related issues and consolidate if needed.',
    '- Propose the maintainer action (implement, ask for info, close, defer).',
    '- Draft the public response (requires human approval before posting).',
    '',
    '## Notes',
    '- TODO: Summarize issue intent, blockers, and suggested next steps.',
    '',
  ].join('\n');
}

export function summarizePullRequest(pr: NormalizedPullRequest): string {
  const relationsSection = [];
  if (pr.relations.mentions.length > 0) {
    relationsSection.push(`Mentions: ${pr.relations.mentions.map(n => `#${n}`).join(', ')}`);
  }
  if (pr.relations.mentionedBy.length > 0) {
    relationsSection.push(`Mentioned by: ${pr.relations.mentionedBy.map(n => `#${n}`).join(', ')}`);
  }
  if (pr.relations.possibleDuplicates.length > 0) {
    relationsSection.push(`Possible duplicates: ${pr.relations.possibleDuplicates.map(n => `#${n}`).join(', ')}`);
  }

  const readinessSignals = [];
  if (pr.hasApproval) readinessSignals.push('Has approval');
  if (pr.hasChangesRequested) readinessSignals.push('Changes requested');
  if (pr.unresolvedThreads > 0) readinessSignals.push(`${pr.unresolvedThreads} unresolved threads`);
  if (pr.statusCheckState === 'SUCCESS') readinessSignals.push('CI passing');
  if (pr.statusCheckState === 'FAILURE') readinessSignals.push('CI failing');
  if (pr.isDraft) readinessSignals.push('Draft');
  if (pr.touchesTests) readinessSignals.push('Touches tests');

  return [
    `# PR ${pr.number}: ${pr.title}`,
    '',
    `URL: ${pr.url}`,
    `Author: ${pr.author}`,
    `Created: ${pr.createdAt} (${pr.ageInDays} days ago)`,
    `Updated: ${pr.updatedAt} (${pr.daysSinceUpdate} days ago)`,
    `Draft: ${pr.isDraft ? 'yes' : 'no'}`,
    `Labels: ${pr.labels.length ? pr.labels.join(', ') : 'none'}`,
    `Assignees: ${pr.assignees.length ? pr.assignees.join(', ') : 'none'}`,
    `Comments: ${pr.comments.length} (totalCount=${pr.commentsTotal})`,
    `Reviews: ${pr.reviews.length} (totalCount=${pr.reviewsTotal})`,
    `Review comments: ${pr.reviewComments.length} (threads=${pr.reviewCommentsTotal})`,
    `Files: ${pr.files.length} (totalCount=${pr.filesTotal})`,
    `Lines changed: ${pr.linesChanged}`,
    `Status checks: ${pr.statusCheckState ?? 'unknown'}`,
    `Participants: ${pr.participants.join(', ')}`,
    '',
    '## Analysis',
    `Priority Score: ${pr.priorityScore}`,
    `Implementation Score (auto): ${pr.implementationScoreAuto}`,
    `Agent Score: ${pr.agentScore}`,
    `Agent Confidence: ${pr.agentConfidence}`,
    `Implementation Score (final): ${pr.implementationScoreFinal}`,
    `Implementation Tier: ${pr.implementationTierFinal}`,
    `Needs-Info Score: ${pr.needsInfoScore}${pr.needsInfoSignals.length ? ` (${pr.needsInfoSignals.join(', ')})` : ''}`,
    `Actionability: ${pr.actionability}`,
    `Signals: ${readinessSignals.length ? readinessSignals.join(', ') : 'No signals'}`,
    `Linked issues: ${pr.linkedIssues.length ? pr.linkedIssues.map(n => `#${n}`).join(', ') : 'none'} (priority sum: ${pr.linkedIssuePriority})`,
    `Relationship Score: ${pr.relationshipScore}`,
    `Relationship Quality: ${pr.relationshipQualityFinal}`,
    `Relationship Overlap: ${pr.relationshipOverlap.toFixed(2)}`,
    `Sentiment Score: ${pr.sentimentScore}`,
    `Reactions: ${formatReactionCounts(pr.reactionTotals)}`,
    relationsSection.length ? relationsSection.join('\n') : 'No relations detected',
    '',
    '## Comment Index (chronological)',
    ...(pr.comments.length
      ? pr.comments.map((comment) => {
          const reactions = formatReactionCounts(comment.reactions);
          const assoc = comment.authorAssociation ? ` (${comment.authorAssociation})` : '';
          return `- PR:${pr.number}:C:${comment.index} | ${comment.createdAt} | ${comment.author}${assoc} | reactions: ${reactions}`;
        })
      : ['- No PR conversation comments.']),
    '',
    '## Review Index (chronological)',
    ...(pr.reviews.length
      ? pr.reviews.map((review) => {
          const reactions = formatReactionCounts(review.reactions);
          const assoc = review.authorAssociation ? ` (${review.authorAssociation})` : '';
          return `- PR:${pr.number}:R:${review.index} | ${review.submittedAt} | ${review.author}${assoc} | state:${review.state} | reactions: ${reactions}`;
        })
      : ['- No reviews yet.']),
    '',
    '## Review Comment Index (chronological)',
    ...(pr.reviewComments.length
      ? pr.reviewComments.map((comment) => {
          const reactions = formatReactionCounts(comment.reactions);
          const assoc = comment.authorAssociation ? ` (${comment.authorAssociation})` : '';
          const location = comment.path ? `${comment.path}:${comment.position ?? ''}` : 'unknown-location';
          return `- PR:${pr.number}:RC:${comment.index} | ${comment.createdAt} | ${comment.author}${assoc} | ${location} | thread:${comment.threadIndex} resolved:${comment.threadResolved ? 'yes' : 'no'} | reactions: ${reactions}`;
        })
      : ['- No review comments yet.']),
    '',
    '## File Summary',
    ...(pr.files.length
      ? pr.files.map((file) => `- ${file.path} (+${file.additions}/-${file.deletions})`)
      : ['- No file data.']),
    '',
    '## Comment Analysis',
    (pr.comments.length || pr.reviews.length || pr.reviewComments.length)
      ? '- TODO: Fill analysis per comment/review.'
      : '- No comments to analyze.',
    '',
    '## Agent Review Prompt',
    '- Extract the problem and solution approach from the PR.',
    '- Validate relationship quality to linked issues (does it solve the right thing?).',
    '- Assess sentiment and community signals (comments, reactions).',
    '- Decide if the PR is a strong implementation candidate.',
    '- Update agent_score, agent_confidence, agent_rationale, and relationship_quality_final in the persistent note.',
    '- Outline how you would implement the fix directly (tests, docs, release notes).',
    '- Draft the closing response that credits the contributor (requires human approval).',
    '',
    '## Notes',
    '- TODO: Summarize PR intent, quality signals, and suggested next steps.',
    '',
  ].join('\n');
}

export function generateExecutiveSummary(
  reportLabel: string,
  generatedAt: string,
  owner: string,
  repo: string,
  issues: NormalizedIssue[],
  prs: NormalizedPullRequest[],
  contributors: Map<string, ContributorProfile>,
  staleDaysIssues: number,
  staleDaysPrs: number
): string {
  const issueComments = issues.reduce((sum, issue) => sum + issue.comments.length, 0);
  const prComments = prs.reduce((sum, pr) => sum + pr.comments.length, 0);
  const prReviews = prs.reduce((sum, pr) => sum + pr.reviews.length, 0);
  const prReviewComments = prs.reduce((sum, pr) => sum + pr.reviewComments.length, 0);
  const totalCommentArtifacts = issueComments + prComments + prReviews + prReviewComments;

  const reactionTotals: NormalizedReactionCounts = {};
  for (const issue of issues) {
    const totals = issue.reactionTotals;
    for (const [key, value] of Object.entries(totals)) {
      reactionTotals[key] = (reactionTotals[key] ?? 0) + value;
    }
  }

  const priorityIssues = [...issues].sort((a, b) => b.priorityScore - a.priorityScore).slice(0, 5);
  const priorityPrs = [...prs].sort((a, b) => b.priorityScore - a.priorityScore).slice(0, 5);
  const implementationPrs = [...prs].sort((a, b) => b.implementationScoreFinal - a.implementationScoreFinal).slice(0, 5);

  const readyIssues = issues.filter(i => i.actionability === 'ready');
  const closableIssues = issues.filter(i => i.actionability === 'closable');
  const staleIssues = issues.filter(i => i.actionability === 'stale');
  const needsAnalysisPrs = prs.filter(p => p.actionability === 'needs-analysis');
  const stalePrs = prs.filter(p => p.actionability === 'stale');
  const strongImpl = prs.filter(p => p.implementationTierFinal === 'strong');
  const mediumImpl = prs.filter(p => p.implementationTierFinal === 'medium');

  const issuesWithDuplicates = issues.filter(i => i.relations.possibleDuplicates.length > 0);
  const prsWithDuplicates = prs.filter(p => p.relations.possibleDuplicates.length > 0);

  const oldestIssues = [...issues].sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()).slice(0, 3);

  const firstTimers = Array.from(contributors.values()).filter(c => c.isFirstTime);
  const formatFirstTimer = (c: ContributorProfile) => {
    const parts: string[] = [];
    if (c.issuesOpened.length) parts.push(`issues ${c.issuesOpened.map(n => `#${n}`).join(', ')}`);
    if (c.prsOpened.length) parts.push(`PRs ${c.prsOpened.map(n => `#${n}`).join(', ')}`);
    if (c.commentsOn.length) parts.push(`comments ${c.commentsOn.map(n => `#${n}`).join(', ')}`);
    return parts.join('; ') || 'comments only';
  };

  return [
    '# Executive Summary',
    '',
    `Generated: ${generatedAt}`,
    `Repository: ${owner}/${repo}`,
    `Report folder: ${reportLabel}`,
    '',
    '## Snapshot',
    `- Open issues: ${issues.length}`,
    `- Open PRs: ${prs.length}`,
    `- Comment artifacts: ${totalCommentArtifacts}`,
    `- Reactions: ${formatReactionCounts(reactionTotals)}`,
    `- Unique contributors: ${contributors.size}`,
    '',
    '## Priority Queue (by score)',
    '',
    '### Top Issues',
    ...(priorityIssues.length
      ? priorityIssues.map(i => `- #${i.number} (score:${i.priorityScore}, ${i.actionability}) - ${i.title}`)
      : ['- None']),
    '',
    '### Top PRs',
    ...(priorityPrs.length
      ? priorityPrs.map(p => `- #${p.number} (score:${p.priorityScore}, ${p.actionability}) - ${p.title}`)
      : ['- None']),
    '',
    '### Top Implementation Candidates',
    ...(implementationPrs.length
      ? implementationPrs.map(p => `- #${p.number} (impl:${p.implementationScoreFinal}, ${p.actionability}) - ${p.title}`)
      : ['- None']),
    '',
    '## Actionability Summary',
    '',
    '### Issues',
    `- Ready to work: ${readyIssues.length}`,
    `- Closable: ${closableIssues.length}${closableIssues.length ? ` (${closableIssues.map(i => `#${i.number}`).join(', ')})` : ''}`,
    `- Stale (>${staleDaysIssues} days): ${staleIssues.length}${staleIssues.length ? ` (${staleIssues.map(i => `#${i.number}`).join(', ')})` : ''}`,
    '',
    '### PRs',
    `- Needs analysis: ${needsAnalysisPrs.length}${needsAnalysisPrs.length ? ` (${needsAnalysisPrs.map(p => `#${p.number}`).join(', ')})` : ''}`,
    `- Implementation candidates (strong): ${strongImpl.length}${strongImpl.length ? ` (${strongImpl.map(p => `#${p.number}`).join(', ')})` : ''}`,
    `- Implementation candidates (medium): ${mediumImpl.length}${mediumImpl.length ? ` (${mediumImpl.map(p => `#${p.number}`).join(', ')})` : ''}`,
    `- Stale (>${staleDaysPrs} days): ${stalePrs.length}${stalePrs.length ? ` (${stalePrs.map(p => `#${p.number}`).join(', ')})` : ''}`,
    '',
    '## Possible Duplicates',
    ...(issuesWithDuplicates.length || prsWithDuplicates.length
      ? [
          ...issuesWithDuplicates.map(i => `- ISSUE #${i.number} may duplicate: ${i.relations.possibleDuplicates.map(n => `#${n}`).join(', ')}`),
          ...prsWithDuplicates.map(p => `- PR #${p.number} may duplicate: ${p.relations.possibleDuplicates.map(n => `#${n}`).join(', ')}`),
        ]
      : ['- No duplicates detected']),
    '',
    '## Oldest Open Issues',
    ...(oldestIssues.length
      ? oldestIssues.map(i => `- #${i.number} (${i.ageInDays} days old) - ${i.title}`)
      : ['- None']),
    '',
    '## First-Time Contributors',
    ...(firstTimers.length
      ? firstTimers.map(c => `- @${c.login}: ${formatFirstTimer(c)}`)
      : ['- None in current open items']),
    '',
  ].join('\n');
}

export function generateTriageTemplate(
  generatedAt: string,
  owner: string,
  repo: string,
  issues: NormalizedIssue[],
  prs: NormalizedPullRequest[]
): string {
  const priorityIssues = [...issues].sort((a, b) => b.priorityScore - a.priorityScore);
  const priorityPrs = [...prs].sort((a, b) => b.priorityScore - a.priorityScore);

  return [
    '# Triage Report',
    '',
    `Generated: ${generatedAt}`,
    `Repository: ${owner}/${repo}`,
    '',
    '## Priority Queue',
    '',
    'Fill in your top 5-7 priorities with citations:',
    '',
    '1. TODO',
    '2. TODO',
    '3. TODO',
    '4. TODO',
    '5. TODO',
    '',
    '## Issues by Priority Score',
    '',
    ...(priorityIssues.length
      ? priorityIssues.map(i => `- ISSUE:${i.number} (${i.priorityScore}) [${i.actionability}] ${i.title}`)
      : ['- None']),
    '',
    '## PRs by Priority Score',
    '',
    ...(priorityPrs.length
      ? priorityPrs.map(p => `- PR:${p.number} (priority:${p.priorityScore}, impl:${p.implementationScoreFinal}, agent:${p.agentScore}, rel:${p.relationshipScore}, relq:${p.relationshipQualityFinal}, sent:${p.sentimentScore}, tier:${p.implementationTierFinal}) [${p.actionability}] ${p.title}`)
      : ['- None']),
    '',
    '## Decisions Needed',
    '',
    '- TODO: List items requiring maintainer decisions',
    '',
    '## Opportunity Backlog',
    '',
    '- TODO: Docs, onboarding, hygiene, UX improvements not tied to a single issue/PR',
    '',
    '## Notes',
    '',
    '- TODO: Add observations and patterns',
    '',
  ].join('\n');
}

export function generateAgentBriefsTemplate(
  generatedAt: string,
  owner: string,
  repo: string
): string {
  return [
    '# Agent Briefs',
    '',
    `Generated: ${generatedAt}`,
    `Repository: ${owner}/${repo}`,
    '',
    '## How to Use',
    '',
    'Convert priorities into actionable briefs for coding agents:',
    '',
    '```',
    '## Brief: [Title]',
    '',
    '**Intent**: What needs to be done and why',
    '**Related**: ISSUE:X, PR:Y',
    '**Constraints**: Any limitations or requirements',
    '**Acceptance**: How to verify completion',
    '**Prompt Draft**: The exact agent prompt to execute this task',
    '**Approval needed**: Comment/close actions need human OK',
    '```',
    '',
    '## Briefs',
    '',
    '### Brief 1',
    '',
    'TODO: Add first priority brief',
    '',
    '### Brief 2',
    '',
    'TODO: Add second priority brief',
    '',
  ].join('\n');
}

export function generateAgentPromptsTemplate(
  generatedAt: string,
  owner: string,
  repo: string
): string {
  return [
    '# Agent Prompts',
    '',
    `Generated: ${generatedAt}`,
    `Repository: ${owner}/${repo}`,
    '',
    '## How to Use',
    '',
    'Create one prompt per brief. Each prompt should be executable by a coding agent and include constraints, acceptance criteria, and references.',
    '',
    '## Prompts',
    '',
    '### Prompt 1',
    '',
    'TODO: Add the first prompt derived from Brief 1',
    '',
    '### Prompt 2',
    '',
    'TODO: Add the second prompt derived from Brief 2',
    '',
  ].join('\n');
}

export function generateContributorsSummary(contributors: Map<string, ContributorProfile>): string {
  const sorted = Array.from(contributors.values()).sort((a, b) => {
    const aTotal = a.issuesOpened.length + a.prsOpened.length + a.commentsOn.length;
    const bTotal = b.issuesOpened.length + b.prsOpened.length + b.commentsOn.length;
    return bTotal - aTotal;
  });

  return [
    '# Contributors',
    '',
    '## Summary',
    '',
    `Total unique contributors: ${contributors.size}`,
    `First-time contributors: ${sorted.filter(c => c.isFirstTime).length}`,
    '',
    '## Profiles',
    '',
    ...sorted.map(c => [
      `### @${c.login}`,
      '',
      `- First seen: ${c.firstSeen}`,
      `- Last seen: ${c.lastSeen}`,
      `- First-time: ${c.isFirstTime ? 'yes' : 'no'}`,
      `- Issues opened: ${c.issuesOpened.length ? c.issuesOpened.map(n => `#${n}`).join(', ') : 'none'}`,
      `- PRs opened: ${c.prsOpened.length ? c.prsOpened.map(n => `#${n}`).join(', ') : 'none'}`,
      `- Commented on: ${c.commentsOn.length ? c.commentsOn.map(n => `#${n}`).join(', ') : 'none'}`,
      `- Association types: ${c.associationTypes.size ? Array.from(c.associationTypes).join(', ') : 'none'}`,
      '',
    ].join('\n')),
  ].join('\n');
}

export function generateDeltaReport(delta: DeltaChanges, previousLabel: string, currentLabel: string): string {
  return [
    '# Delta Report',
    '',
    `Previous run: ${previousLabel}`,
    `Current run: ${currentLabel}`,
    '',
    '## New Items',
    '',
    `### New Issues (${delta.newIssues.length})`,
    delta.newIssues.length ? delta.newIssues.map(n => `- #${n}`).join('\n') : '- None',
    '',
    `### New PRs (${delta.newPrs.length})`,
    delta.newPrs.length ? delta.newPrs.map(n => `- #${n}`).join('\n') : '- None',
    '',
    '## Updated Items',
    '',
    `### Updated Issues (${delta.updatedIssues.length})`,
    delta.updatedIssues.length ? delta.updatedIssues.map(n => `- #${n}`).join('\n') : '- None',
    '',
    `### Updated PRs (${delta.updatedPrs.length})`,
    delta.updatedPrs.length ? delta.updatedPrs.map(n => `- #${n}`).join('\n') : '- None',
    '',
    '## Closed Since Last Run',
    '',
    `### Closed Issues (${delta.closedIssues.length})`,
    delta.closedIssues.length ? delta.closedIssues.map(n => `- #${n}`).join('\n') : '- None',
    '',
    `### Closed PRs (${delta.closedPrs.length})`,
    delta.closedPrs.length ? delta.closedPrs.map(n => `- #${n}`).join('\n') : '- None',
    '',
  ].join('\n');
}
