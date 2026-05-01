import {
  ActionabilityState,
  ContributorProfile,
  GhComment,
  GhIssueNode,
  GhPullRequestNode,
  GhReview,
  GhReviewThread,
  MaintainerConfig,
  NormalizedComment,
  NormalizedIssue,
  NormalizedPullRequest,
  NormalizedReactionCounts,
  NormalizedReview,
  NormalizedReviewComment,
} from './types';

function normalizeReactions(groups?: { content: string; users: { totalCount: number } }[] | null): NormalizedReactionCounts {
  const counts: NormalizedReactionCounts = {};
  if (!groups) return counts;
  for (const group of groups) {
    const total = group?.users?.totalCount ?? 0;
    if (total > 0) {
      counts[group.content] = total;
    }
  }
  return counts;
}

function mergeReactionCounts(target: NormalizedReactionCounts, source: NormalizedReactionCounts) {
  for (const [key, value] of Object.entries(source)) {
    target[key] = (target[key] ?? 0) + value;
  }
}

function sortByDate<T extends { createdAt?: string; submittedAt?: string }>(items: T[], key: 'createdAt' | 'submittedAt') {
  return [...items].sort((a, b) => {
    const aTime = new Date(a[key] ?? '').getTime();
    const bTime = new Date(b[key] ?? '').getTime();
    return aTime - bTime;
  });
}

function daysBetween(date1: string, date2: string): number {
  const d1 = new Date(date1).getTime();
  const d2 = new Date(date2).getTime();
  return Math.floor(Math.abs(d2 - d1) / (1000 * 60 * 60 * 24));
}

type SentimentLexicon = {
  positive: Set<string>;
  negative: Set<string>;
};

const STOPWORDS = new Set([
  'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'over', 'under', 'about', 'there', 'their',
  'your', 'you', 'our', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'but', 'not', 'can', 'could',
  'should', 'would', 'will', 'just', 'than', 'then', 'when', 'what', 'which', 'while', 'why', 'how', 'any',
  'all', 'its', 'it', 'also', 'use', 'using', 'used',
]);

function extractTextTokens(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\\s]/g, ' ')
    .split(/\\s+/)
    .filter((token) => token.length > 2 && !STOPWORDS.has(token));
}

function sentimentFromText(text: string, lexicon: SentimentLexicon): number {
  const tokens = extractTextTokens(text);
  let score = 0;
  for (const token of tokens) {
    if (lexicon.positive.has(token)) score += 1;
    if (lexicon.negative.has(token)) score -= 1;
  }
  return score;
}

function aggregateSentiment(texts: Array<string | null | undefined>, lexicon: SentimentLexicon): number {
  let score = 0;
  for (const text of texts) {
    if (!text) continue;
    score += sentimentFromText(text, lexicon);
  }
  return score;
}

function buildSentimentLexicon(config: MaintainerConfig): SentimentLexicon {
  const positive = new Set(config.sentiment.positiveWords.map((word) => word.toLowerCase()));
  const negative = new Set(config.sentiment.negativeWords.map((word) => word.toLowerCase()));
  return { positive, negative };
}

function keywordOverlapScore(a: string, b: string): number {
  const aTokens = new Set(extractTextTokens(a));
  const bTokens = new Set(extractTextTokens(b));
  if (!aTokens.size || !bTokens.size) return 0;
  let overlap = 0;
  for (const token of aTokens) {
    if (bTokens.has(token)) overlap += 1;
  }
  const denominator = Math.max(aTokens.size, bTokens.size);
  return overlap / denominator;
}

function extractMentions(text: string | null, linkKeywords: string[]): number[] {
  if (!text) return [];
  const mentions: number[] = [];
  const keywordPattern = linkKeywords.length
    ? `(?:${linkKeywords.map((k) => k.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')).join('|')})`
    : 'fixes?|closes?|resolves?|addresses|related to|see|ref';
  const pattern = new RegExp(`(?:^|\\s)(?:${keywordPattern})?[:\\s]*#(\\d+)`, 'gi');
  let match;
  while ((match = pattern.exec(text)) !== null) {
    const num = parseInt(match[1], 10);
    if (!isNaN(num) && !mentions.includes(num)) {
      mentions.push(num);
    }
  }
  return mentions;
}

function classifyIssueType(title: string, body: string | null, labels: string[], config: MaintainerConfig): NormalizedIssue['itemType'] {
  const titleLower = title.toLowerCase();
  const bodyLower = (body ?? '').toLowerCase();
  const labelSet = new Set(labels.map((l) => l.toLowerCase()));

  const matchesLabel = (values: string[]) => values.some((value) => labelSet.has(value));
  const matchesText = (values: string[]) => values.some((value) => titleLower.includes(value) || bodyLower.includes(value));

  if (matchesLabel(config.typeLabels.bug) || titleLower.includes('[bug]') || titleLower.includes('bug:')) return 'bug';
  if (matchesLabel(config.typeLabels.feature) || titleLower.includes('[feature]') || titleLower.includes('feat:')) return 'feature';
  if (matchesLabel(config.typeLabels.question) || titleLower.includes('[question]') || titleLower.includes('?')) return 'question';
  if (matchesLabel(config.typeLabels.support) || titleLower.includes('help') || bodyLower.includes('how do i') || bodyLower.includes('how can i')) return 'support';
  if (matchesLabel(config.typeLabels.meta) || titleLower.includes('contributor') || titleLower.includes('maintainer') || titleLower.includes('roadmap')) return 'meta';

  if (matchesText(config.semantics.intent.bug)) return 'bug';
  if (matchesText(config.semantics.intent.feature)) return 'feature';
  if (matchesText(config.semantics.intent.question)) return 'question';
  if (matchesText(config.semantics.intent.support)) return 'support';
  if (matchesText(config.semantics.intent.meta)) return 'meta';

  return 'unknown';
}

function computeIssuePriorityScore(issue: {
  commentsTotal: number;
  reactionTotals: NormalizedReactionCounts;
  ageInDays: number;
  daysSinceUpdate: number;
  itemType: string;
  labels: string[];
}, config: MaintainerConfig): number {
  const weights = config.priority.issue;
  let score = 0;

  score += issue.commentsTotal * weights.commentWeight;
  for (const [reaction, weight] of Object.entries(weights.reactionWeights)) {
    score += (issue.reactionTotals[reaction] ?? 0) * weight;
  }

  score += weights.typeBoosts[issue.itemType] ?? 0;

  if (issue.daysSinceUpdate > 30) score += weights.stalePenalty.over30;
  if (issue.daysSinceUpdate > 60) score += weights.stalePenalty.over60;

  if (issue.ageInDays > 30 && issue.daysSinceUpdate < 7) {
    score += weights.ageBoost.over30AndFresh;
  }

  for (const label of issue.labels) {
    const boost = config.priority.labelBoosts[label.toLowerCase()];
    if (boost) score += boost;
  }

  return Math.max(0, score);
}

function computePrPriorityScore(pr: {
  commentsTotal: number;
  reviewsTotal: number;
  daysSinceUpdate: number;
  hasApproval: boolean;
  hasChangesRequested: boolean;
  unresolvedThreads: number;
  statusCheckState: string | null;
  isDraft: boolean;
  labels: string[];
}, config: MaintainerConfig): number {
  const weights = config.priority.pr;
  let score = 0;

  score += pr.commentsTotal * weights.commentWeight;
  score += pr.reviewsTotal * weights.reviewWeight;

  if (pr.hasApproval) score += weights.approvalBoost;
  if (pr.statusCheckState === 'SUCCESS') score += weights.ciSuccessBoost;
  if (pr.unresolvedThreads > 0) score += weights.unresolvedThreadsPenalty;

  if (pr.hasChangesRequested) score += weights.changesRequestedPenalty;
  if (pr.isDraft) score += weights.draftPenalty;

  if (pr.daysSinceUpdate > 14) score += weights.stalePenalty.over14;
  if (pr.daysSinceUpdate > 30) score += weights.stalePenalty.over30;

  for (const label of pr.labels) {
    const boost = config.priority.labelBoosts[label.toLowerCase()];
    if (boost) score += boost;
  }

  return Math.max(0, score);
}

function matchesAny(labelSet: Set<string>, labels: string[]): boolean {
  return labels.some((label) => labelSet.has(label));
}

function classifyIssueActionability(issue: NormalizedIssue, config: MaintainerConfig): ActionabilityState {
  const labelSet = new Set(issue.labels.map((l) => l.toLowerCase()));

  if (matchesAny(labelSet, config.labels.blocked)) return 'blocked';
  if (matchesAny(labelSet, config.labels.needsInfo)) return 'needs-info';
  if (matchesAny(labelSet, config.labels.needsDecision)) return 'needs-decision';
  if (matchesAny(labelSet, config.labels.closable)) return 'closable';

  if (issue.daysSinceUpdate > config.staleDays.issues) return 'stale';

  if (config.heuristics.needsInfo.enabled && issue.needsInfoScore >= config.heuristics.needsInfo.threshold) {
    return 'needs-info';
  }

  const lastComment = issue.comments[issue.comments.length - 1];
  if (lastComment && lastComment.author !== issue.author && lastComment.body?.includes('?')) {
    return 'needs-info';
  }

  if (issue.comments.some(c =>
    c.body?.toLowerCase().includes('fixed in') ||
    c.body?.toLowerCase().includes('released in') ||
    c.body?.toLowerCase().includes('issue can be closed')
  )) {
    return 'closable';
  }

  return 'ready';
}

function classifyPrActionability(pr: NormalizedPullRequest, config: MaintainerConfig): ActionabilityState {
  const labelSet = new Set(pr.labels.map((l) => l.toLowerCase()));

  if (matchesAny(labelSet, config.labels.blocked)) return 'blocked';
  if (matchesAny(labelSet, config.labels.needsInfo)) return 'needs-info';
  if (matchesAny(labelSet, config.labels.needsDecision)) return 'needs-decision';
  if (matchesAny(labelSet, config.labels.closable)) return 'closable';

  if (pr.daysSinceUpdate > config.staleDays.prs) return 'stale';

  if (config.heuristics.needsInfo.enabled && pr.needsInfoScore >= config.heuristics.needsInfo.threshold) {
    return 'needs-info';
  }

  return 'needs-analysis';
}

function findPossibleDuplicates(
  item: { number: number; title: string; body: string | null },
  allItems: Array<{ number: number; title: string; body: string | null }>,
  config: MaintainerConfig
): number[] {
  const duplicates: number[] = [];
  const titleWords = new Set(item.title.toLowerCase().split(/\s+/).filter(w => w.length > 3));
  const itemText = `${item.title} ${item.body ?? ''}`;
  const itemErrors = extractErrorSignatures(itemText);
  const configuredErrors = config.semantics.errors.signatures.map((sig) => sig.toLowerCase());
  const duplicateHints = config.semantics.relationship.duplicateHints;

  for (const other of allItems) {
    if (other.number === item.number) continue;

    const otherTitleWords = other.title.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    const otherText = `${other.title} ${other.body ?? ''}`;
    const otherErrors = extractErrorSignatures(otherText);

    let titleOverlap = 0;
    for (const word of otherTitleWords) {
      if (titleWords.has(word)) titleOverlap++;
    }
    const titleSimilarity = titleWords.size > 0 ? titleOverlap / titleWords.size : 0;

    const overlapScore = keywordOverlapScore(itemText, otherText);
    const sharedError = hasSharedSignature(itemErrors, otherErrors);
    const sharedConfiguredError = configuredErrors.some((sig) => sig && itemText.toLowerCase().includes(sig) && otherText.toLowerCase().includes(sig));
    const duplicateHintPresent = duplicateHints.some((hint) => itemText.toLowerCase().includes(hint) || otherText.toLowerCase().includes(hint));

    const match =
      titleSimilarity > config.heuristics.duplicates.titleSimilarityThreshold ||
      overlapScore > config.heuristics.duplicates.overlapThreshold ||
      sharedError ||
      sharedConfiguredError;

    if (match && (!config.heuristics.duplicates.requireSharedError || sharedError || sharedConfiguredError || duplicateHintPresent)) {
      duplicates.push(other.number);
    }
  }

  return duplicates;
}

function extractErrorSignatures(text: string): string[] {
  const signatures = new Set<string>();
  if (!text) return [];
  const lower = text.toLowerCase();
  const lines = lower.split('\n').map((line) => line.trim()).filter(Boolean);
  for (const line of lines) {
    if (line.length < 10 || line.length > 180) continue;
    if (/(error|exception|failed|failure|security error|cannot|can't|can not|unable)/i.test(line)) {
      signatures.add(line.replace(/\s+/g, ' '));
    }
  }
  const quotePattern = /["'`]{1}([^"'`]{10,180})["'`]{1}/g;
  let match;
  while ((match = quotePattern.exec(text)) !== null) {
    const snippet = match[1].toLowerCase().trim();
    if (/(error|exception|failed|failure|security error)/i.test(snippet)) {
      signatures.add(snippet.replace(/\s+/g, ' '));
    }
  }
  return Array.from(signatures);
}

function hasSharedSignature(a: string[], b: string[]): boolean {
  if (!a.length || !b.length) return false;
  const setA = new Set(a);
  for (const entry of b) {
    if (setA.has(entry)) return true;
  }
  return false;
}

function normalizeComments(comments: GhComment[]): NormalizedComment[] {
  const sorted = sortByDate(comments, 'createdAt');
  return sorted.map((comment, index) => ({
    index: index + 1,
    url: comment.url,
    body: comment.body ?? null,
    createdAt: comment.createdAt,
    author: comment.author?.login ?? 'unknown',
    authorAssociation: comment.authorAssociation ?? null,
    reactions: normalizeReactions(comment.reactionGroups),
  }));
}

function normalizeReviews(reviews: GhReview[]): NormalizedReview[] {
  const sorted = sortByDate(reviews, 'submittedAt');
  return sorted.map((review, index) => ({
    index: index + 1,
    url: review.url,
    body: review.body ?? null,
    state: review.state,
    submittedAt: review.submittedAt,
    author: review.author?.login ?? 'unknown',
    authorAssociation: review.authorAssociation ?? null,
    reactions: normalizeReactions(review.reactionGroups),
  }));
}

function normalizeReviewComments(threads: GhReviewThread[]): NormalizedReviewComment[] {
  const flattened: NormalizedReviewComment[] = [];
  threads.forEach((thread, threadIndex) => {
    const sorted = sortByDate(thread.comments.nodes, 'createdAt');
    sorted.forEach((comment) => {
      flattened.push({
        index: 0,
        threadIndex: threadIndex + 1,
        threadResolved: thread.isResolved,
        url: comment.url,
        body: comment.body ?? null,
        createdAt: comment.createdAt,
        author: comment.author?.login ?? 'unknown',
        authorAssociation: comment.authorAssociation ?? null,
        reactions: normalizeReactions(comment.reactionGroups),
        path: comment.path ?? null,
        position: comment.position ?? null,
      });
    });
  });
  const sorted = flattened.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  sorted.forEach((comment, index) => {
    comment.index = index + 1;
  });
  return sorted;
}

function collectParticipants(...authorArrays: Array<string[]>): string[] {
  const set = new Set<string>();
  for (const arr of authorArrays) {
    for (const author of arr) {
      if (author) set.add(author);
    }
  }
  return Array.from(set).sort();
}

function isTestPath(filePath: string): boolean {
  const lower = filePath.toLowerCase();
  return (
    lower.includes('test') ||
    lower.includes('__tests__') ||
    lower.includes('spec') ||
    lower.endsWith('.test.ts') ||
    lower.endsWith('.test.js') ||
    lower.endsWith('.spec.ts') ||
    lower.endsWith('.spec.js')
  );
}

export function normalizeIssues(nodes: GhIssueNode[], now: string, config: MaintainerConfig): NormalizedIssue[] {
  const basicItems = nodes.map(issue => ({
    number: issue.number,
    title: issue.title,
    body: issue.body,
  }));
  const sentimentLexicon = buildSentimentLexicon(config);
  const linkKeywords = config.semantics.relationship.linkKeywords;

  return nodes.map((issue) => {
    const comments = normalizeComments(issue.comments.nodes ?? []);
    const reactionTotals: NormalizedReactionCounts = {};
    const commentAuthors = comments.map((comment) => comment.author);
    for (const comment of comments) {
      mergeReactionCounts(reactionTotals, comment.reactions);
    }
    const participants = collectParticipants(
      [issue.author?.login ?? 'unknown'],
      commentAuthors
    );
    const labels = issue.labels?.nodes?.map((label) => label.name) ?? [];

    const ageInDays = daysBetween(issue.createdAt, now);
    const daysSinceUpdate = daysBetween(issue.updatedAt, now);
    const itemType = classifyIssueType(issue.title, issue.body, labels, config);

    const bodyMentions = extractMentions(issue.body, linkKeywords);
    const commentMentions = comments.flatMap(c => extractMentions(c.body, linkKeywords));
    const allMentions = [...new Set([...bodyMentions, ...commentMentions])].filter(n => n !== issue.number);

    const possibleDuplicates = findPossibleDuplicates(
      { number: issue.number, title: issue.title, body: issue.body },
      basicItems,
      config
    );

    const sentimentScore = aggregateSentiment([
      issue.title,
      issue.body ?? '',
      ...comments.map((comment) => comment.body ?? ''),
    ], sentimentLexicon);

    const baseIssue: NormalizedIssue = {
      number: issue.number,
      title: issue.title,
      body: issue.body ?? null,
      url: issue.url,
      createdAt: issue.createdAt,
      updatedAt: issue.updatedAt,
      author: issue.author?.login ?? 'unknown',
      labels,
      assignees: issue.assignees?.nodes?.map((assignee) => assignee.login) ?? [],
      commentsTotal: issue.comments.totalCount,
      comments,
      reactionTotals,
      sentimentScore,
      participants,
      ageInDays,
      daysSinceUpdate,
      itemType,
      relations: {
        mentions: allMentions,
        mentionedBy: [],
        possibleDuplicates,
      },
      priorityScore: 0,
      actionability: 'ready',
      needsInfoScore: 0,
      needsInfoSignals: [],
    };

    const needsInfo = computeNeedsInfoSignalsForIssue(baseIssue, config);
    baseIssue.needsInfoScore = needsInfo.score;
    baseIssue.needsInfoSignals = needsInfo.signals;

    baseIssue.priorityScore = computeIssuePriorityScore(baseIssue, config);
    baseIssue.actionability = classifyIssueActionability(baseIssue, config);

    return baseIssue;
  });
}

export function normalizePullRequests(nodes: GhPullRequestNode[], now: string, config: MaintainerConfig): NormalizedPullRequest[] {
  const basicItems = nodes.map(pr => ({
    number: pr.number,
    title: pr.title,
    body: pr.body,
  }));
  const sentimentLexicon = buildSentimentLexicon(config);
  const linkKeywords = config.semantics.relationship.linkKeywords;

  return nodes.map((pr) => {
    const comments = normalizeComments(pr.comments.nodes ?? []);
    const reviews = normalizeReviews(pr.reviews.nodes ?? []);
    const reviewComments = normalizeReviewComments(pr.reviewThreads.nodes ?? []);

    const reactionTotals: NormalizedReactionCounts = {};
    for (const comment of comments) mergeReactionCounts(reactionTotals, comment.reactions);
    for (const review of reviews) mergeReactionCounts(reactionTotals, review.reactions);
    for (const reviewComment of reviewComments) mergeReactionCounts(reactionTotals, reviewComment.reactions);

    const commentAuthors = comments.map((comment) => comment.author);
    const reviewAuthors = reviews.map((review) => review.author);
    const reviewCommentAuthors = reviewComments.map((comment) => comment.author);

    const participants = collectParticipants(
      [pr.author?.login ?? 'unknown'],
      commentAuthors,
      reviewAuthors,
      reviewCommentAuthors
    );

    const statusCheckState = pr.commits.nodes[0]?.commit?.statusCheckRollup?.state ?? null;
    const labels = pr.labels?.nodes?.map((label) => label.name) ?? [];

    const ageInDays = daysBetween(pr.createdAt, now);
    const daysSinceUpdate = daysBetween(pr.updatedAt, now);

    const hasApproval = reviews.some(r => r.state === 'APPROVED');
    const hasChangesRequested = reviews.some(r => r.state === 'CHANGES_REQUESTED');
    const unresolvedThreads = pr.reviewThreads.nodes?.filter(t => !t.isResolved).length ?? 0;

    const bodyMentions = extractMentions(pr.body, linkKeywords);
    const commentMentions = comments.flatMap(c => extractMentions(c.body, linkKeywords));
    const allMentions = [...new Set([...bodyMentions, ...commentMentions])].filter(n => n !== pr.number);

    const possibleDuplicates = findPossibleDuplicates(
      { number: pr.number, title: pr.title, body: pr.body },
      basicItems,
      config
    );

    const sentimentScore = aggregateSentiment([
      pr.title,
      pr.body ?? '',
      ...comments.map((comment) => comment.body ?? ''),
      ...reviews.map((review) => review.body ?? ''),
      ...reviewComments.map((comment) => comment.body ?? ''),
    ], sentimentLexicon);

    const linesChanged = (pr.files.nodes ?? []).reduce((sum, file) => sum + file.additions + file.deletions, 0);

    const basePr: NormalizedPullRequest = {
      number: pr.number,
      title: pr.title,
      body: pr.body ?? null,
      url: pr.url,
      createdAt: pr.createdAt,
      updatedAt: pr.updatedAt,
      isDraft: pr.isDraft,
      author: pr.author?.login ?? 'unknown',
      labels,
      assignees: pr.assignees?.nodes?.map((assignee) => assignee.login) ?? [],
      commentsTotal: pr.comments.totalCount,
      comments,
      reactionTotals,
      sentimentScore,
      reviewsTotal: pr.reviews.totalCount,
      reviews,
      reviewCommentsTotal: pr.reviewThreads.totalCount,
      reviewComments,
      filesTotal: pr.files.totalCount,
      files: pr.files.nodes ?? [],
      linesChanged,
      statusCheckState,
      participants,
      ageInDays,
      daysSinceUpdate,
      hasApproval,
      hasChangesRequested,
      unresolvedThreads,
      relations: {
        mentions: allMentions,
        mentionedBy: [],
        possibleDuplicates,
      },
      priorityScore: 0,
      actionability: 'needs-analysis',
      needsInfoScore: 0,
      needsInfoSignals: [],
      linkedIssues: [],
      linkedIssuePriority: 0,
      relationshipScore: 0,
      relationshipOverlap: 0,
      relationshipQualityAuto: 'none',
      relationshipQualityFinal: 'none',
      touchesTests: (pr.files.nodes ?? []).some(file => isTestPath(file.path)),
      implementationScoreAuto: 0,
      implementationScoreFinal: 0,
      implementationTierAuto: 'weak',
      implementationTierFinal: 'weak',
      agentScore: 0,
      agentConfidence: 'unset',
      agentRationale: '',
    };

    basePr.priorityScore = computePrPriorityScore(basePr, config);
    const needsInfo = computeNeedsInfoSignalsForPr(basePr, config);
    basePr.needsInfoScore = needsInfo.score;
    basePr.needsInfoSignals = needsInfo.signals;
    basePr.actionability = classifyPrActionability(basePr, config);

    return basePr;
  });
}

export function buildMentionedByRelations(issues: NormalizedIssue[], prs: NormalizedPullRequest[]) {
  for (const issue of issues) {
    for (const mentioned of issue.relations.mentions) {
      const targetIssue = issues.find(i => i.number === mentioned);
      if (targetIssue && !targetIssue.relations.mentionedBy.includes(issue.number)) {
        targetIssue.relations.mentionedBy.push(issue.number);
      }
      const targetPr = prs.find(p => p.number === mentioned);
      if (targetPr && !targetPr.relations.mentionedBy.includes(issue.number)) {
        targetPr.relations.mentionedBy.push(issue.number);
      }
    }
  }

  for (const pr of prs) {
    for (const mentioned of pr.relations.mentions) {
      const targetIssue = issues.find(i => i.number === mentioned);
      if (targetIssue && !targetIssue.relations.mentionedBy.includes(pr.number)) {
        targetIssue.relations.mentionedBy.push(pr.number);
      }
      const targetPr = prs.find(p => p.number === mentioned);
      if (targetPr && !targetPr.relations.mentionedBy.includes(pr.number)) {
        targetPr.relations.mentionedBy.push(pr.number);
      }
    }
  }
}

function scoreReactions(reactions: NormalizedReactionCounts): number {
  const positive = (reactions.THUMBS_UP ?? 0) + (reactions.HEART ?? 0) + (reactions.HOORAY ?? 0) + (reactions.ROCKET ?? 0);
  const negative = (reactions.THUMBS_DOWN ?? 0) + (reactions.CONFUSED ?? 0);
  return (positive * 2) - (negative * 2);
}

type RelationshipQuality = 'strong' | 'medium' | 'weak' | 'none';

function classifyRelationshipQuality(
  overlapScore: number,
  explicitLink: boolean,
  linkedIssues: number,
  config: MaintainerConfig
): RelationshipQuality {
  if (linkedIssues === 0) return 'none';
  if (config.heuristics.relationshipQuality.strongWhenExplicit && explicitLink) return 'strong';
  if (overlapScore >= config.heuristics.relationshipQuality.strongOverlapThreshold) return 'strong';
  if (overlapScore >= config.heuristics.relationshipQuality.mediumOverlapThreshold) return 'medium';
  return config.heuristics.relationshipQuality.defaultWhenLinked;
}

function computeImplementationScore(
  pr: NormalizedPullRequest,
  linkedIssueReactions: number,
  linkedIssueSentiment: number,
  config: MaintainerConfig
): number {
  const weights = config.implementation;
  let score = 0;

  score += pr.commentsTotal * weights.commentWeight;
  score += pr.reviewsTotal * weights.reviewWeight;
  score += pr.reviewCommentsTotal * weights.reviewCommentWeight;
  score += scoreReactions(pr.reactionTotals) * weights.reactionWeight;
  score += pr.linkedIssuePriority * weights.linkedIssuePriorityWeight;
  score += linkedIssueReactions * weights.linkedIssueReactionWeight;
  score += linkedIssueSentiment * weights.linkedIssueSentimentWeight;
  score += pr.relationshipScore * weights.relationshipScoreWeight;
  score += weights.relationshipQualityBoosts[pr.relationshipQualityAuto];

  if (pr.touchesTests) score += weights.touchesTestsBoost;
  if (pr.statusCheckState === 'SUCCESS') score += weights.ciSuccessBoost;
  if (pr.statusCheckState === 'FAILURE') score += weights.ciFailurePenalty;
  if (pr.hasChangesRequested) score += weights.changesRequestedPenalty;
  if (pr.unresolvedThreads > 0) score += weights.unresolvedThreadsPenalty;
  if (pr.isDraft) score += weights.draftPenalty;

  if (pr.daysSinceUpdate > 60) score += weights.agePenalty.over60;
  else if (pr.daysSinceUpdate > 30) score += weights.agePenalty.over30;
  else if (pr.daysSinceUpdate > 14) score += weights.agePenalty.over14;

  if (pr.filesTotal > 25) score += weights.sizePenalty.filesOver25;
  else if (pr.filesTotal > 10) score += weights.sizePenalty.filesOver10;

  if (pr.linesChanged > 1000) score += weights.sizePenalty.linesOver1000;
  else if (pr.linesChanged > 500) score += weights.sizePenalty.linesOver500;

  return Math.max(weights.scoreFloor, Math.round(score));
}

function hasAnyPhrase(text: string, phrases: string[]): boolean {
  return phrases.some((phrase) => phrase && phraseMatches(text, phrase));
}

function phraseMatches(text: string, phrase: string): boolean {
  const normalized = phrase.trim().toLowerCase();
  if (!normalized) return false;
  if (normalized.length <= 3) {
    const escaped = normalized.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
    return new RegExp(`\\b${escaped}\\b`, 'i').test(text);
  }
  return text.includes(normalized);
}

function containsEnvToken(text: string, tokens: string[]): boolean {
  return tokens.some((token) => token && phraseMatches(text, token));
}

function computeNeedsInfoSignalsForIssue(issue: NormalizedIssue, config: MaintainerConfig): { score: number; signals: string[] } {
  if (!config.heuristics.needsInfo.enabled) return { score: 0, signals: [] };
  const text = `${issue.title}\n${issue.body ?? ''}\n${issue.comments.map(c => c.body ?? '').join('\n')}`.toLowerCase();
  const signals: string[] = [];
  const weights = config.heuristics.needsInfo.weights;

  const missingReproConfig = config.heuristics.needsInfo.issueSignals.missingRepro;
  if (missingReproConfig.enabled && missingReproConfig.applyTo.includes(issue.itemType)) {
    const hasRepro = hasAnyPhrase(text, config.semantics.needsInfo.repro);
    if (!hasRepro) signals.push('missing-repro');
  }

  const missingExpectedActualConfig = config.heuristics.needsInfo.issueSignals.missingExpectedActual;
  if (missingExpectedActualConfig.enabled && missingExpectedActualConfig.applyTo.includes(issue.itemType)) {
    const hasExpected = hasAnyPhrase(text, config.semantics.needsInfo.expected);
    const hasActual = hasAnyPhrase(text, config.semantics.needsInfo.actual);
    if (!(hasExpected && hasActual)) signals.push('missing-expected-actual');
  }

  const missingEnvironmentConfig = config.heuristics.needsInfo.issueSignals.missingEnvironment;
  if (missingEnvironmentConfig.enabled && missingEnvironmentConfig.applyTo.includes(issue.itemType)) {
    const hasEnvironment = hasAnyPhrase(text, config.semantics.needsInfo.environment) || containsEnvToken(text, config.semantics.environmentTokens);
    if (!hasEnvironment) signals.push('missing-environment');
  }

  const missingVersionConfig = config.heuristics.needsInfo.issueSignals.missingVersion;
  if (missingVersionConfig.enabled && missingVersionConfig.applyTo.includes(issue.itemType)) {
    const hasVersionPhrase = hasAnyPhrase(text, config.semantics.needsInfo.version);
    const hasVersionPattern = /\bv?\d+\.\d+(\.\d+)?\b/.test(text);
    if (!(hasVersionPhrase || hasVersionPattern)) signals.push('missing-version');
  }

  const missingLogsConfig = config.heuristics.needsInfo.issueSignals.missingLogs;
  if (missingLogsConfig.enabled && missingLogsConfig.applyTo.includes(issue.itemType)) {
    const hasErrorKeyword = config.semantics.errors.keywords.some((kw) => kw && text.includes(kw));
    const hasLogs = hasAnyPhrase(text, config.semantics.needsInfo.logs) || /```/.test(text) || text.includes('stack trace');
    if (hasErrorKeyword && !hasLogs) signals.push('missing-logs');
  }

  const weightFor = (signal: string) => {
    const map: Record<string, string> = {
      'missing-repro': 'missingRepro',
      'missing-expected-actual': 'missingExpectedActual',
      'missing-environment': 'missingEnvironment',
      'missing-version': 'missingVersion',
      'missing-logs': 'missingLogs',
    };
    const key = map[signal] ?? signal;
    return weights[key] ?? 1;
  };
  const score = signals.reduce((sum, signal) => sum + weightFor(signal), 0);
  return { score, signals };
}

function computeNeedsInfoSignalsForPr(pr: NormalizedPullRequest, config: MaintainerConfig): { score: number; signals: string[] } {
  if (!config.heuristics.needsInfo.enabled) return { score: 0, signals: [] };
  const text = `${pr.title}\n${pr.body ?? ''}\n${pr.comments.map(c => c.body ?? '').join('\n')}`.toLowerCase();
  const signals: string[] = [];
  const weights = config.heuristics.needsInfo.weights;

  if (config.heuristics.needsInfo.prSignals.missingDescription.enabled) {
    const hasDescription = pr.body && pr.body.trim().length > 0;
    if (!hasDescription) signals.push('missing-description');
  }

  if (config.heuristics.needsInfo.prSignals.missingTestPlan.enabled) {
    const hasTestPlan = hasAnyPhrase(text, config.semantics.needsInfo.testPlan);
    if (!hasTestPlan) signals.push('missing-test-plan');
  }

  const weightFor = (signal: string) => {
    const map: Record<string, string> = {
      'missing-test-plan': 'missingTestPlan',
      'missing-description': 'missingDescription',
    };
    const key = map[signal] ?? signal;
    return weights[key] ?? 1;
  };
  const score = signals.reduce((sum, signal) => sum + weightFor(signal), 0);
  return { score, signals };
}

export function enrichPullRequestsWithIssueSignals(
  prs: NormalizedPullRequest[],
  issues: NormalizedIssue[],
  config: MaintainerConfig
) {
  const issueMap = new Map<number, NormalizedIssue>(issues.map(issue => [issue.number, issue]));

  for (const pr of prs) {
    const linkedIssues = pr.relations.mentions.filter((num) => issueMap.has(num));
    const linkedIssuePriority = linkedIssues.reduce((sum, num) => sum + (issueMap.get(num)?.priorityScore ?? 0), 0);
    const linkedIssueReactions = linkedIssues.reduce((sum, num) => {
      const issue = issueMap.get(num);
      return sum + (issue ? scoreReactions(issue.reactionTotals) : 0);
    }, 0);
    const linkedIssueSentiment = linkedIssues.reduce((sum, num) => {
      const issue = issueMap.get(num);
      return sum + (issue?.sentimentScore ?? 0);
    }, 0);

    let overlapScore = 0;
    for (const num of linkedIssues) {
      const issue = issueMap.get(num);
      if (!issue) continue;
      const issueText = `${issue.title} ${issue.body ?? ''}`;
      const prText = `${pr.title} ${pr.body ?? ''}`;
      overlapScore = Math.max(overlapScore, keywordOverlapScore(issueText, prText));
    }

    const linkKeywords = config.semantics.relationship.linkKeywords;
    const linkPattern = linkKeywords.length
      ? new RegExp(`(?:${linkKeywords.map((k) => k.replace(/[-/\\^$*+?.()|[\\]{}]/g, '\\$&')).join('|')})\\s+#\\d+`, 'i')
      : /fixes\\s+#\\d+|closes\\s+#\\d+|resolves\\s+#\\d+/i;
    const explicitLink = linkPattern.test(pr.body ?? '');
    const relationshipQuality = classifyRelationshipQuality(overlapScore, explicitLink, linkedIssues.length, config);

    pr.linkedIssues = linkedIssues;
    pr.linkedIssuePriority = linkedIssuePriority;
    pr.relationshipOverlap = overlapScore;
    pr.relationshipQualityAuto = relationshipQuality;
    pr.relationshipQualityFinal = relationshipQuality;
    const relWeights = config.relationshipScore;
    pr.relationshipScore = Math.round(
      (overlapScore * relWeights.overlapWeight) +
      (explicitLink ? relWeights.explicitLinkBoost : 0) +
      (linkedIssues.length * relWeights.linkedIssuesWeight) +
      (pr.relations.mentionedBy.length * relWeights.mentionedByWeight) +
      (linkedIssuePriority * relWeights.linkedIssuePriorityWeight)
    );

    pr.implementationScoreAuto = computeImplementationScore(pr, linkedIssueReactions, linkedIssueSentiment, config);
    pr.implementationScoreFinal = pr.implementationScoreAuto;
    const tierThresholds = config.implementation.tierThresholds;
    if (pr.implementationScoreAuto >= tierThresholds.strong) {
      pr.implementationTierAuto = 'strong';
      pr.implementationTierFinal = 'strong';
    } else if (pr.implementationScoreAuto >= tierThresholds.medium) {
      pr.implementationTierAuto = 'medium';
      pr.implementationTierFinal = 'medium';
    } else {
      pr.implementationTierAuto = 'weak';
      pr.implementationTierFinal = 'weak';
    }
  }
}

export function buildContributorProfiles(issues: NormalizedIssue[], prs: NormalizedPullRequest[]): Map<string, ContributorProfile> {
  const profiles = new Map<string, ContributorProfile>();

  const getOrCreate = (login: string): ContributorProfile => {
    if (!profiles.has(login)) {
      profiles.set(login, {
        login,
        issuesOpened: [],
        prsOpened: [],
        commentsOn: [],
        firstSeen: '',
        lastSeen: '',
        isFirstTime: true,
        associationTypes: new Set(),
      });
    }
    return profiles.get(login)!;
  };

  for (const issue of issues) {
    const profile = getOrCreate(issue.author);
    profile.issuesOpened.push(issue.number);
    if (!profile.firstSeen || issue.createdAt < profile.firstSeen) profile.firstSeen = issue.createdAt;
    if (!profile.lastSeen || issue.createdAt > profile.lastSeen) profile.lastSeen = issue.createdAt;

    for (const comment of issue.comments) {
      const cProfile = getOrCreate(comment.author);
      if (!cProfile.commentsOn.includes(issue.number)) cProfile.commentsOn.push(issue.number);
      if (comment.authorAssociation) cProfile.associationTypes.add(comment.authorAssociation);
      if (!cProfile.firstSeen || comment.createdAt < cProfile.firstSeen) cProfile.firstSeen = comment.createdAt;
      if (!cProfile.lastSeen || comment.createdAt > cProfile.lastSeen) cProfile.lastSeen = comment.createdAt;
    }
  }

  for (const pr of prs) {
    const profile = getOrCreate(pr.author);
    profile.prsOpened.push(pr.number);
    if (!profile.firstSeen || pr.createdAt < profile.firstSeen) profile.firstSeen = pr.createdAt;
    if (!profile.lastSeen || pr.createdAt > profile.lastSeen) profile.lastSeen = pr.createdAt;

    for (const comment of pr.comments) {
      const cProfile = getOrCreate(comment.author);
      if (!cProfile.commentsOn.includes(pr.number)) cProfile.commentsOn.push(pr.number);
      if (comment.authorAssociation) cProfile.associationTypes.add(comment.authorAssociation);
    }

    for (const review of pr.reviews) {
      const rProfile = getOrCreate(review.author);
      if (review.authorAssociation) rProfile.associationTypes.add(review.authorAssociation);
    }
  }

  for (const profile of profiles.values()) {
    profile.isFirstTime = profile.issuesOpened.length + profile.prsOpened.length <= 1;
  }

  return profiles;
}
