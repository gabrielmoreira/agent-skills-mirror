export type ReactionGroup = {
  content: string;
  users: { totalCount: number };
};

export type GhAuthor = {
  login: string | null;
} | null;

export type GhLabelConnection = {
  nodes: Array<{ name: string }>;
} | null;

export type GhAssigneeConnection = {
  nodes: Array<{ login: string }>;
} | null;

export type GhComment = {
  url: string;
  body: string | null;
  createdAt: string;
  author: GhAuthor;
  authorAssociation?: string | null;
  reactionGroups?: ReactionGroup[] | null;
};

export type GhIssueNode = {
  number: number;
  title: string;
  body: string | null;
  url: string;
  createdAt: string;
  updatedAt: string;
  author: GhAuthor;
  labels: GhLabelConnection;
  assignees: GhAssigneeConnection;
  comments: {
    totalCount: number;
    nodes: GhComment[];
  };
};

export type GhReview = {
  url: string;
  body: string | null;
  state: string;
  submittedAt: string;
  author: GhAuthor;
  authorAssociation?: string | null;
  reactionGroups?: ReactionGroup[] | null;
};

export type GhReviewComment = GhComment & {
  path?: string | null;
  position?: number | null;
};

export type GhReviewThread = {
  isResolved: boolean;
  comments: {
    nodes: GhReviewComment[];
  };
};

export type GhPrFile = {
  path: string;
  additions: number;
  deletions: number;
};

export type GhPullRequestNode = {
  number: number;
  title: string;
  body: string | null;
  url: string;
  createdAt: string;
  updatedAt: string;
  isDraft: boolean;
  author: GhAuthor;
  labels: GhLabelConnection;
  assignees: GhAssigneeConnection;
  comments: {
    totalCount: number;
    nodes: GhComment[];
  };
  reviews: {
    totalCount: number;
    nodes: GhReview[];
  };
  reviewThreads: {
    totalCount: number;
    nodes: GhReviewThread[];
  };
  files: {
    totalCount: number;
    nodes: GhPrFile[];
  };
  commits: {
    nodes: Array<{
      commit: {
        oid: string;
        statusCheckRollup?: { state: string } | null;
      };
    }>;
  };
};

export type NormalizedReactionCounts = Record<string, number>;

export type NormalizedComment = {
  index: number;
  url: string;
  body: string | null;
  createdAt: string;
  author: string;
  authorAssociation: string | null;
  reactions: NormalizedReactionCounts;
};

export type NormalizedReview = {
  index: number;
  url: string;
  body: string | null;
  state: string;
  submittedAt: string;
  author: string;
  authorAssociation: string | null;
  reactions: NormalizedReactionCounts;
};

export type NormalizedReviewComment = NormalizedComment & {
  path: string | null;
  position: number | null;
  threadIndex: number;
  threadResolved: boolean;
};

export type ItemRelations = {
  mentions: number[];
  mentionedBy: number[];
  possibleDuplicates: number[];
};

export type ActionabilityState =
  | 'ready'
  | 'needs-info'
  | 'needs-decision'
  | 'needs-analysis'
  | 'blocked'
  | 'stale'
  | 'closable';

export type NormalizedIssue = {
  number: number;
  title: string;
  body: string | null;
  url: string;
  createdAt: string;
  updatedAt: string;
  author: string;
  labels: string[];
  assignees: string[];
  commentsTotal: number;
  comments: NormalizedComment[];
  reactionTotals: NormalizedReactionCounts;
  sentimentScore: number;
  participants: string[];
  ageInDays: number;
  daysSinceUpdate: number;
  priorityScore: number;
  actionability: ActionabilityState;
  needsInfoScore: number;
  needsInfoSignals: string[];
  relations: ItemRelations;
  itemType: 'bug' | 'feature' | 'question' | 'support' | 'meta' | 'unknown';
};

export type NormalizedPullRequest = {
  number: number;
  title: string;
  body: string | null;
  url: string;
  createdAt: string;
  updatedAt: string;
  isDraft: boolean;
  author: string;
  labels: string[];
  assignees: string[];
  commentsTotal: number;
  comments: NormalizedComment[];
  reactionTotals: NormalizedReactionCounts;
  sentimentScore: number;
  reviewsTotal: number;
  reviews: NormalizedReview[];
  reviewCommentsTotal: number;
  reviewComments: NormalizedReviewComment[];
  filesTotal: number;
  files: GhPrFile[];
  linesChanged: number;
  statusCheckState: string | null;
  participants: string[];
  ageInDays: number;
  daysSinceUpdate: number;
  priorityScore: number;
  actionability: ActionabilityState;
  needsInfoScore: number;
  needsInfoSignals: string[];
  relations: ItemRelations;
  hasApproval: boolean;
  hasChangesRequested: boolean;
  unresolvedThreads: number;
  linkedIssues: number[];
  linkedIssuePriority: number;
  relationshipScore: number;
  relationshipOverlap: number;
  relationshipQualityAuto: 'strong' | 'medium' | 'weak' | 'none';
  relationshipQualityFinal: 'strong' | 'medium' | 'weak' | 'none';
  touchesTests: boolean;
  implementationScoreAuto: number;
  implementationScoreFinal: number;
  implementationTierAuto: 'strong' | 'medium' | 'weak';
  implementationTierFinal: 'strong' | 'medium' | 'weak';
  agentScore: number;
  agentConfidence: string;
  agentRationale: string;
};

export type ContributorProfile = {
  login: string;
  issuesOpened: number[];
  prsOpened: number[];
  commentsOn: number[];
  firstSeen: string;
  lastSeen: string;
  isFirstTime: boolean;
  associationTypes: Set<string>;
};

export type DeltaChanges = {
  newIssues: number[];
  updatedIssues: number[];
  newPrs: number[];
  updatedPrs: number[];
  closedIssues: number[];
  closedPrs: number[];
};

export type StateSnapshot = {
  schemaVersion: 1;
  lastRunAt: string;
  lastReportDir: string;
  issueHashes: Record<string, string>;
  prHashes: Record<string, string>;
};

export type MaintainerConfig = {
  schemaVersion: 1;
  reportsDir: string;
  stateFile: string;
  noMergeExternalPRs: boolean;
  semantics: {
    intent: {
      bug: string[];
      feature: string[];
      question: string[];
      support: string[];
      meta: string[];
    };
    needsInfo: {
      repro: string[];
      expected: string[];
      actual: string[];
      environment: string[];
      version: string[];
      logs: string[];
      testPlan: string[];
    };
    environmentTokens: string[];
    relationship: {
      linkKeywords: string[];
      duplicateHints: string[];
    };
    errors: {
      signatures: string[];
      keywords: string[];
    };
  };
  heuristics: {
    needsInfo: {
      enabled: boolean;
      threshold: number;
      issueSignals: {
        missingRepro: { enabled: boolean; applyTo: Array<NormalizedIssue['itemType']> };
        missingExpectedActual: { enabled: boolean; applyTo: Array<NormalizedIssue['itemType']> };
        missingEnvironment: { enabled: boolean; applyTo: Array<NormalizedIssue['itemType']> };
        missingVersion: { enabled: boolean; applyTo: Array<NormalizedIssue['itemType']> };
        missingLogs: { enabled: boolean; applyTo: Array<NormalizedIssue['itemType']> };
      };
      prSignals: {
        missingTestPlan: { enabled: boolean };
        missingDescription: { enabled: boolean };
      };
      weights: Record<string, number>;
    };
    duplicates: {
      titleSimilarityThreshold: number;
      overlapThreshold: number;
      requireSharedError: boolean;
    };
    relationshipQuality: {
      strongOverlapThreshold: number;
      mediumOverlapThreshold: number;
      strongWhenExplicit: boolean;
      defaultWhenLinked: 'medium' | 'weak';
    };
  };
  sentiment: {
    positiveWords: string[];
    negativeWords: string[];
  };
  staleDays: {
    issues: number;
    prs: number;
  };
  labels: {
    blocked: string[];
    needsInfo: string[];
    needsDecision: string[];
    closable: string[];
  };
  typeLabels: {
    bug: string[];
    feature: string[];
    question: string[];
    support: string[];
    meta: string[];
  };
  priority: {
    issue: {
      commentWeight: number;
      reactionWeights: Record<string, number>;
      typeBoosts: Record<string, number>;
      stalePenalty: {
        over30: number;
        over60: number;
      };
      ageBoost: {
        over30AndFresh: number;
      };
    };
    pr: {
      commentWeight: number;
      reviewWeight: number;
      approvalBoost: number;
      ciSuccessBoost: number;
      unresolvedThreadsPenalty: number;
      changesRequestedPenalty: number;
      draftPenalty: number;
      stalePenalty: {
        over14: number;
        over30: number;
      };
    };
    labelBoosts: Record<string, number>;
  };
  relationshipScore: {
    overlapWeight: number;
    explicitLinkBoost: number;
    linkedIssuesWeight: number;
    mentionedByWeight: number;
    linkedIssuePriorityWeight: number;
  };
  implementation: {
    commentWeight: number;
    reviewWeight: number;
    reviewCommentWeight: number;
    reactionWeight: number;
    linkedIssuePriorityWeight: number;
    linkedIssueReactionWeight: number;
    linkedIssueSentimentWeight: number;
    relationshipScoreWeight: number;
    relationshipQualityBoosts: {
      strong: number;
      medium: number;
      weak: number;
      none: number;
    };
    touchesTestsBoost: number;
    ciSuccessBoost: number;
    ciFailurePenalty: number;
    changesRequestedPenalty: number;
    unresolvedThreadsPenalty: number;
    draftPenalty: number;
    agePenalty: {
      over14: number;
      over30: number;
      over60: number;
    };
    sizePenalty: {
      filesOver10: number;
      filesOver25: number;
      linesOver500: number;
      linesOver1000: number;
    };
    agentScoreWeight: number;
    agentConfidenceMultipliers: {
      high: number;
      medium: number;
      low: number;
      unset: number;
    };
    scoreFloor: number;
    tierThresholds: {
      strong: number;
      medium: number;
    };
  };
};
