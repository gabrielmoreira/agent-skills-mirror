import fs from 'node:fs';
import path from 'node:path';

import { MaintainerConfig } from './types';

const DEFAULT_CONFIG: MaintainerConfig = {
  schemaVersion: 1,
  reportsDir: 'reports',
  stateFile: '.github/maintainer/state.json',
  noMergeExternalPRs: true,
  semantics: {
    intent: {
      bug: ['bug', 'crash', 'error', 'exception', 'fails', 'failing', 'broken', 'regression'],
      feature: ['feature', 'enhancement', 'feature request', 'would be nice', 'add support', 'request'],
      question: ['how do i', 'how can i', 'is it possible', 'what does', 'question'],
      support: ['help', 'support', 'troubleshoot', 'configure', 'configuration', 'setup', 'install'],
      meta: ['roadmap', 'governance', 'maintainer', 'community', 'discussion'],
    },
    needsInfo: {
      repro: ['steps to reproduce', 'repro steps', 'reproduction'],
      expected: ['expected behavior', 'expected result'],
      actual: ['actual behavior', 'actual result'],
      environment: ['environment', 'os', 'operating system', 'platform'],
      version: ['version', 'openskills version', 'node version'],
      logs: ['logs', 'stack trace', 'error output'],
      testPlan: ['test plan', 'testing', 'tests run'],
    },
    environmentTokens: ['windows', 'win11', 'win10', 'mac', 'macos', 'linux', 'ubuntu', 'debian', 'node', 'npm', 'pnpm', 'yarn'],
    relationship: {
      linkKeywords: ['fixes', 'closes', 'resolves', 'addresses', 'related to', 'see', 'ref', 'refs', 'linked to'],
      duplicateHints: ['duplicate', 'same issue', 'same error', 'same problem'],
    },
    errors: {
      signatures: [],
      keywords: ['error', 'exception', 'failed', 'failure', 'crash', 'security error'],
    },
  },
  heuristics: {
    needsInfo: {
      enabled: true,
      threshold: 2,
      issueSignals: {
        missingRepro: { enabled: true, applyTo: ['bug', 'unknown'] },
        missingExpectedActual: { enabled: true, applyTo: ['bug', 'unknown'] },
        missingEnvironment: { enabled: true, applyTo: ['bug', 'support', 'question', 'unknown'] },
        missingVersion: { enabled: true, applyTo: ['bug', 'support', 'question', 'unknown'] },
        missingLogs: { enabled: true, applyTo: ['bug', 'support', 'unknown'] },
      },
      prSignals: {
        missingTestPlan: { enabled: true },
        missingDescription: { enabled: true },
      },
      weights: {
        missingRepro: 2,
        missingExpectedActual: 1,
        missingEnvironment: 1,
        missingVersion: 1,
        missingLogs: 1,
        missingTestPlan: 1,
        missingDescription: 1,
      },
    },
    duplicates: {
      titleSimilarityThreshold: 0.6,
      overlapThreshold: 0.35,
      requireSharedError: false,
    },
    relationshipQuality: {
      strongOverlapThreshold: 0.45,
      mediumOverlapThreshold: 0.15,
      strongWhenExplicit: true,
      defaultWhenLinked: 'medium',
    },
  },
  sentiment: {
    positiveWords: [
      'thanks', 'thank', 'great', 'awesome', 'good', 'love', 'like', 'helpful', 'appreciate', 'nice', 'excellent', 'amazing',
      'worked', 'works', 'fixed', 'resolved', 'perfect',
    ],
    negativeWords: [
      'broken', 'fail', 'fails', 'failing', 'error', 'crash', 'crashes', 'bad', 'terrible', 'awful', 'hate', 'bug',
      'regression', 'doesnt', "doesn't", 'cant', "can't", 'worse', 'problem', 'issue',
    ],
  },
  staleDays: {
    issues: 60,
    prs: 30,
  },
  labels: {
    blocked: ['blocked', 'on-hold'],
    needsInfo: ['needs-info', 'needs-more-info', 'waiting-for-response'],
    needsDecision: ['needs-decision'],
    closable: ['duplicate', 'wontfix', 'invalid', 'out-of-scope'],
  },
  typeLabels: {
    bug: ['bug'],
    feature: ['feature', 'enhancement'],
    question: ['question'],
    support: ['support'],
    meta: ['meta', 'governance', 'roadmap'],
  },
  priority: {
    issue: {
      commentWeight: 2,
      reactionWeights: {
        THUMBS_UP: 3,
        THUMBS_DOWN: 2,
        HEART: 2,
      },
      typeBoosts: {
        bug: 10,
        feature: 5,
      },
      stalePenalty: {
        over30: -5,
        over60: -10,
      },
      ageBoost: {
        over30AndFresh: 5,
      },
    },
    pr: {
      commentWeight: 2,
      reviewWeight: 3,
      approvalBoost: 8,
      ciSuccessBoost: 6,
      unresolvedThreadsPenalty: -5,
      changesRequestedPenalty: -5,
      draftPenalty: -8,
      stalePenalty: {
        over14: -5,
        over30: -10,
      },
    },
    labelBoosts: {
      security: 40,
      critical: 25,
      'high-priority': 15,
    },
  },
  relationshipScore: {
    overlapWeight: 30,
    explicitLinkBoost: 8,
    linkedIssuesWeight: 2,
    mentionedByWeight: 2,
    linkedIssuePriorityWeight: 0.15,
  },
  implementation: {
    commentWeight: 1,
    reviewWeight: 2,
    reviewCommentWeight: 1,
    reactionWeight: 1,
    linkedIssuePriorityWeight: 0.6,
    linkedIssueReactionWeight: 0.3,
    linkedIssueSentimentWeight: 0.2,
    relationshipScoreWeight: 0.5,
    relationshipQualityBoosts: {
      strong: 6,
      medium: 3,
      weak: 0,
      none: -2,
    },
    touchesTestsBoost: 5,
    ciSuccessBoost: 6,
    ciFailurePenalty: -6,
    changesRequestedPenalty: -8,
    unresolvedThreadsPenalty: -4,
    draftPenalty: -10,
    agePenalty: {
      over14: -3,
      over30: -7,
      over60: -12,
    },
    sizePenalty: {
      filesOver10: -3,
      filesOver25: -7,
      linesOver500: -8,
      linesOver1000: -12,
    },
    agentScoreWeight: 1,
    agentConfidenceMultipliers: {
      high: 1.5,
      medium: 1,
      low: 0.5,
      unset: 0,
    },
    scoreFloor: 0,
    tierThresholds: {
      strong: 40,
      medium: 20,
    },
  },
};

function normalizeLabels(list: string[] | undefined): string[] {
  return (list ?? [])
    .map((label) => label.toLowerCase().trim())
    .filter(Boolean);
}

function normalizePhrases(list: string[] | undefined): string[] {
  return (list ?? [])
    .map((phrase) => phrase.toLowerCase().trim())
    .filter(Boolean);
}

function normalizeWords(list: string[] | undefined): string[] {
  return (list ?? [])
    .map((word) => word.toLowerCase().trim())
    .filter(Boolean);
}

function normalizeBoosts(map: Record<string, number> | undefined): Record<string, number> {
  const result: Record<string, number> = {};
  if (!map) return result;
  for (const [key, value] of Object.entries(map)) {
    result[key.toLowerCase().trim()] = value;
  }
  return result;
}

function mergeConfig(overrides: Partial<MaintainerConfig>): MaintainerConfig {
  return {
    ...DEFAULT_CONFIG,
    ...overrides,
    reportsDir: overrides.reportsDir ?? DEFAULT_CONFIG.reportsDir,
    stateFile: overrides.stateFile ?? DEFAULT_CONFIG.stateFile,
    noMergeExternalPRs: overrides.noMergeExternalPRs ?? DEFAULT_CONFIG.noMergeExternalPRs,
    semantics: {
      intent: {
        bug: normalizePhrases(overrides.semantics?.intent?.bug ?? DEFAULT_CONFIG.semantics.intent.bug),
        feature: normalizePhrases(overrides.semantics?.intent?.feature ?? DEFAULT_CONFIG.semantics.intent.feature),
        question: normalizePhrases(overrides.semantics?.intent?.question ?? DEFAULT_CONFIG.semantics.intent.question),
        support: normalizePhrases(overrides.semantics?.intent?.support ?? DEFAULT_CONFIG.semantics.intent.support),
        meta: normalizePhrases(overrides.semantics?.intent?.meta ?? DEFAULT_CONFIG.semantics.intent.meta),
      },
      needsInfo: {
        repro: normalizePhrases(overrides.semantics?.needsInfo?.repro ?? DEFAULT_CONFIG.semantics.needsInfo.repro),
        expected: normalizePhrases(overrides.semantics?.needsInfo?.expected ?? DEFAULT_CONFIG.semantics.needsInfo.expected),
        actual: normalizePhrases(overrides.semantics?.needsInfo?.actual ?? DEFAULT_CONFIG.semantics.needsInfo.actual),
        environment: normalizePhrases(overrides.semantics?.needsInfo?.environment ?? DEFAULT_CONFIG.semantics.needsInfo.environment),
        version: normalizePhrases(overrides.semantics?.needsInfo?.version ?? DEFAULT_CONFIG.semantics.needsInfo.version),
        logs: normalizePhrases(overrides.semantics?.needsInfo?.logs ?? DEFAULT_CONFIG.semantics.needsInfo.logs),
        testPlan: normalizePhrases(overrides.semantics?.needsInfo?.testPlan ?? DEFAULT_CONFIG.semantics.needsInfo.testPlan),
      },
      environmentTokens: normalizeWords(overrides.semantics?.environmentTokens ?? DEFAULT_CONFIG.semantics.environmentTokens),
      relationship: {
        linkKeywords: normalizePhrases(overrides.semantics?.relationship?.linkKeywords ?? DEFAULT_CONFIG.semantics.relationship.linkKeywords),
        duplicateHints: normalizePhrases(overrides.semantics?.relationship?.duplicateHints ?? DEFAULT_CONFIG.semantics.relationship.duplicateHints),
      },
      errors: {
        signatures: normalizePhrases(overrides.semantics?.errors?.signatures ?? DEFAULT_CONFIG.semantics.errors.signatures),
        keywords: normalizePhrases(overrides.semantics?.errors?.keywords ?? DEFAULT_CONFIG.semantics.errors.keywords),
      },
    },
    heuristics: {
      needsInfo: {
        enabled: overrides.heuristics?.needsInfo?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.enabled,
        threshold: overrides.heuristics?.needsInfo?.threshold ?? DEFAULT_CONFIG.heuristics.needsInfo.threshold,
        issueSignals: {
          missingRepro: {
            enabled: overrides.heuristics?.needsInfo?.issueSignals?.missingRepro?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingRepro.enabled,
            applyTo: overrides.heuristics?.needsInfo?.issueSignals?.missingRepro?.applyTo ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingRepro.applyTo,
          },
          missingExpectedActual: {
            enabled: overrides.heuristics?.needsInfo?.issueSignals?.missingExpectedActual?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingExpectedActual.enabled,
            applyTo: overrides.heuristics?.needsInfo?.issueSignals?.missingExpectedActual?.applyTo ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingExpectedActual.applyTo,
          },
          missingEnvironment: {
            enabled: overrides.heuristics?.needsInfo?.issueSignals?.missingEnvironment?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingEnvironment.enabled,
            applyTo: overrides.heuristics?.needsInfo?.issueSignals?.missingEnvironment?.applyTo ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingEnvironment.applyTo,
          },
          missingVersion: {
            enabled: overrides.heuristics?.needsInfo?.issueSignals?.missingVersion?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingVersion.enabled,
            applyTo: overrides.heuristics?.needsInfo?.issueSignals?.missingVersion?.applyTo ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingVersion.applyTo,
          },
          missingLogs: {
            enabled: overrides.heuristics?.needsInfo?.issueSignals?.missingLogs?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingLogs.enabled,
            applyTo: overrides.heuristics?.needsInfo?.issueSignals?.missingLogs?.applyTo ?? DEFAULT_CONFIG.heuristics.needsInfo.issueSignals.missingLogs.applyTo,
          },
        },
        prSignals: {
          missingTestPlan: {
            enabled: overrides.heuristics?.needsInfo?.prSignals?.missingTestPlan?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.prSignals.missingTestPlan.enabled,
          },
          missingDescription: {
            enabled: overrides.heuristics?.needsInfo?.prSignals?.missingDescription?.enabled ?? DEFAULT_CONFIG.heuristics.needsInfo.prSignals.missingDescription.enabled,
          },
        },
        weights: {
          ...DEFAULT_CONFIG.heuristics.needsInfo.weights,
          ...(overrides.heuristics?.needsInfo?.weights ?? {}),
        },
      },
      duplicates: {
        titleSimilarityThreshold: overrides.heuristics?.duplicates?.titleSimilarityThreshold ?? DEFAULT_CONFIG.heuristics.duplicates.titleSimilarityThreshold,
        overlapThreshold: overrides.heuristics?.duplicates?.overlapThreshold ?? DEFAULT_CONFIG.heuristics.duplicates.overlapThreshold,
        requireSharedError: overrides.heuristics?.duplicates?.requireSharedError ?? DEFAULT_CONFIG.heuristics.duplicates.requireSharedError,
      },
      relationshipQuality: {
        strongOverlapThreshold: overrides.heuristics?.relationshipQuality?.strongOverlapThreshold ?? DEFAULT_CONFIG.heuristics.relationshipQuality.strongOverlapThreshold,
        mediumOverlapThreshold: overrides.heuristics?.relationshipQuality?.mediumOverlapThreshold ?? DEFAULT_CONFIG.heuristics.relationshipQuality.mediumOverlapThreshold,
        strongWhenExplicit: overrides.heuristics?.relationshipQuality?.strongWhenExplicit ?? DEFAULT_CONFIG.heuristics.relationshipQuality.strongWhenExplicit,
        defaultWhenLinked: overrides.heuristics?.relationshipQuality?.defaultWhenLinked ?? DEFAULT_CONFIG.heuristics.relationshipQuality.defaultWhenLinked,
      },
    },
    sentiment: {
      positiveWords: normalizeWords(overrides.sentiment?.positiveWords ?? DEFAULT_CONFIG.sentiment.positiveWords),
      negativeWords: normalizeWords(overrides.sentiment?.negativeWords ?? DEFAULT_CONFIG.sentiment.negativeWords),
    },
    staleDays: {
      issues: overrides.staleDays?.issues ?? DEFAULT_CONFIG.staleDays.issues,
      prs: overrides.staleDays?.prs ?? DEFAULT_CONFIG.staleDays.prs,
    },
    labels: {
      blocked: normalizeLabels(overrides.labels?.blocked ?? DEFAULT_CONFIG.labels.blocked),
      needsInfo: normalizeLabels(overrides.labels?.needsInfo ?? DEFAULT_CONFIG.labels.needsInfo),
      needsDecision: normalizeLabels(overrides.labels?.needsDecision ?? DEFAULT_CONFIG.labels.needsDecision),
      closable: normalizeLabels(overrides.labels?.closable ?? DEFAULT_CONFIG.labels.closable),
    },
    typeLabels: {
      bug: normalizeLabels(overrides.typeLabels?.bug ?? DEFAULT_CONFIG.typeLabels.bug),
      feature: normalizeLabels(overrides.typeLabels?.feature ?? DEFAULT_CONFIG.typeLabels.feature),
      question: normalizeLabels(overrides.typeLabels?.question ?? DEFAULT_CONFIG.typeLabels.question),
      support: normalizeLabels(overrides.typeLabels?.support ?? DEFAULT_CONFIG.typeLabels.support),
      meta: normalizeLabels(overrides.typeLabels?.meta ?? DEFAULT_CONFIG.typeLabels.meta),
    },
    priority: {
      issue: {
        ...DEFAULT_CONFIG.priority.issue,
        ...(overrides.priority?.issue ?? {}),
        reactionWeights: {
          ...DEFAULT_CONFIG.priority.issue.reactionWeights,
          ...(overrides.priority?.issue?.reactionWeights ?? {}),
        },
        typeBoosts: {
          ...DEFAULT_CONFIG.priority.issue.typeBoosts,
          ...(overrides.priority?.issue?.typeBoosts ?? {}),
        },
        stalePenalty: {
          ...DEFAULT_CONFIG.priority.issue.stalePenalty,
          ...(overrides.priority?.issue?.stalePenalty ?? {}),
        },
        ageBoost: {
          ...DEFAULT_CONFIG.priority.issue.ageBoost,
          ...(overrides.priority?.issue?.ageBoost ?? {}),
        },
      },
      pr: {
        ...DEFAULT_CONFIG.priority.pr,
        ...(overrides.priority?.pr ?? {}),
        stalePenalty: {
          ...DEFAULT_CONFIG.priority.pr.stalePenalty,
          ...(overrides.priority?.pr?.stalePenalty ?? {}),
        },
      },
      labelBoosts: {
        ...DEFAULT_CONFIG.priority.labelBoosts,
        ...normalizeBoosts(overrides.priority?.labelBoosts),
      },
    },
    relationshipScore: {
      overlapWeight: overrides.relationshipScore?.overlapWeight ?? DEFAULT_CONFIG.relationshipScore.overlapWeight,
      explicitLinkBoost: overrides.relationshipScore?.explicitLinkBoost ?? DEFAULT_CONFIG.relationshipScore.explicitLinkBoost,
      linkedIssuesWeight: overrides.relationshipScore?.linkedIssuesWeight ?? DEFAULT_CONFIG.relationshipScore.linkedIssuesWeight,
      mentionedByWeight: overrides.relationshipScore?.mentionedByWeight ?? DEFAULT_CONFIG.relationshipScore.mentionedByWeight,
      linkedIssuePriorityWeight: overrides.relationshipScore?.linkedIssuePriorityWeight ?? DEFAULT_CONFIG.relationshipScore.linkedIssuePriorityWeight,
    },
    implementation: {
      ...DEFAULT_CONFIG.implementation,
      ...(overrides.implementation ?? {}),
      relationshipQualityBoosts: {
        ...DEFAULT_CONFIG.implementation.relationshipQualityBoosts,
        ...(overrides.implementation?.relationshipQualityBoosts ?? {}),
      },
      agePenalty: {
        ...DEFAULT_CONFIG.implementation.agePenalty,
        ...(overrides.implementation?.agePenalty ?? {}),
      },
      sizePenalty: {
        ...DEFAULT_CONFIG.implementation.sizePenalty,
        ...(overrides.implementation?.sizePenalty ?? {}),
      },
      agentConfidenceMultipliers: {
        ...DEFAULT_CONFIG.implementation.agentConfidenceMultipliers,
        ...(overrides.implementation?.agentConfidenceMultipliers ?? {}),
      },
      tierThresholds: {
        ...DEFAULT_CONFIG.implementation.tierThresholds,
        ...(overrides.implementation?.tierThresholds ?? {}),
      },
    },
  };
}

function mergeStringArray(base: string[], overrides: string[] | undefined): string[] {
  const result = new Set(base);
  for (const entry of overrides ?? []) result.add(entry);
  return Array.from(result);
}

export function mergeWithBase(base: MaintainerConfig, overrides: Partial<MaintainerConfig>): MaintainerConfig {
  return {
    ...base,
    ...overrides,
    reportsDir: overrides.reportsDir ?? base.reportsDir,
    stateFile: overrides.stateFile ?? base.stateFile,
    noMergeExternalPRs: overrides.noMergeExternalPRs ?? base.noMergeExternalPRs,
    semantics: {
      intent: {
        bug: mergeStringArray(base.semantics.intent.bug, overrides.semantics?.intent?.bug),
        feature: mergeStringArray(base.semantics.intent.feature, overrides.semantics?.intent?.feature),
        question: mergeStringArray(base.semantics.intent.question, overrides.semantics?.intent?.question),
        support: mergeStringArray(base.semantics.intent.support, overrides.semantics?.intent?.support),
        meta: mergeStringArray(base.semantics.intent.meta, overrides.semantics?.intent?.meta),
      },
      needsInfo: {
        repro: mergeStringArray(base.semantics.needsInfo.repro, overrides.semantics?.needsInfo?.repro),
        expected: mergeStringArray(base.semantics.needsInfo.expected, overrides.semantics?.needsInfo?.expected),
        actual: mergeStringArray(base.semantics.needsInfo.actual, overrides.semantics?.needsInfo?.actual),
        environment: mergeStringArray(base.semantics.needsInfo.environment, overrides.semantics?.needsInfo?.environment),
        version: mergeStringArray(base.semantics.needsInfo.version, overrides.semantics?.needsInfo?.version),
        logs: mergeStringArray(base.semantics.needsInfo.logs, overrides.semantics?.needsInfo?.logs),
        testPlan: mergeStringArray(base.semantics.needsInfo.testPlan, overrides.semantics?.needsInfo?.testPlan),
      },
      environmentTokens: mergeStringArray(base.semantics.environmentTokens, overrides.semantics?.environmentTokens),
      relationship: {
        linkKeywords: mergeStringArray(base.semantics.relationship.linkKeywords, overrides.semantics?.relationship?.linkKeywords),
        duplicateHints: mergeStringArray(base.semantics.relationship.duplicateHints, overrides.semantics?.relationship?.duplicateHints),
      },
      errors: {
        signatures: mergeStringArray(base.semantics.errors.signatures, overrides.semantics?.errors?.signatures),
        keywords: mergeStringArray(base.semantics.errors.keywords, overrides.semantics?.errors?.keywords),
      },
    },
    heuristics: {
      needsInfo: {
        ...base.heuristics.needsInfo,
        ...(overrides.heuristics?.needsInfo ?? {}),
        issueSignals: {
          ...base.heuristics.needsInfo.issueSignals,
          ...(overrides.heuristics?.needsInfo?.issueSignals ?? {}),
        },
        prSignals: {
          ...base.heuristics.needsInfo.prSignals,
          ...(overrides.heuristics?.needsInfo?.prSignals ?? {}),
        },
        weights: {
          ...base.heuristics.needsInfo.weights,
          ...(overrides.heuristics?.needsInfo?.weights ?? {}),
        },
      },
      duplicates: {
        ...base.heuristics.duplicates,
        ...(overrides.heuristics?.duplicates ?? {}),
      },
      relationshipQuality: {
        ...base.heuristics.relationshipQuality,
        ...(overrides.heuristics?.relationshipQuality ?? {}),
      },
    },
    sentiment: {
      positiveWords: mergeStringArray(base.sentiment.positiveWords, overrides.sentiment?.positiveWords),
      negativeWords: mergeStringArray(base.sentiment.negativeWords, overrides.sentiment?.negativeWords),
    },
    staleDays: {
      issues: overrides.staleDays?.issues ?? base.staleDays.issues,
      prs: overrides.staleDays?.prs ?? base.staleDays.prs,
    },
    labels: {
      blocked: mergeStringArray(base.labels.blocked, overrides.labels?.blocked),
      needsInfo: mergeStringArray(base.labels.needsInfo, overrides.labels?.needsInfo),
      needsDecision: mergeStringArray(base.labels.needsDecision, overrides.labels?.needsDecision),
      closable: mergeStringArray(base.labels.closable, overrides.labels?.closable),
    },
    typeLabels: {
      bug: mergeStringArray(base.typeLabels.bug, overrides.typeLabels?.bug),
      feature: mergeStringArray(base.typeLabels.feature, overrides.typeLabels?.feature),
      question: mergeStringArray(base.typeLabels.question, overrides.typeLabels?.question),
      support: mergeStringArray(base.typeLabels.support, overrides.typeLabels?.support),
      meta: mergeStringArray(base.typeLabels.meta, overrides.typeLabels?.meta),
    },
    priority: {
      issue: {
        ...base.priority.issue,
        ...(overrides.priority?.issue ?? {}),
        reactionWeights: {
          ...base.priority.issue.reactionWeights,
          ...(overrides.priority?.issue?.reactionWeights ?? {}),
        },
        typeBoosts: {
          ...base.priority.issue.typeBoosts,
          ...(overrides.priority?.issue?.typeBoosts ?? {}),
        },
        stalePenalty: {
          ...base.priority.issue.stalePenalty,
          ...(overrides.priority?.issue?.stalePenalty ?? {}),
        },
        ageBoost: {
          ...base.priority.issue.ageBoost,
          ...(overrides.priority?.issue?.ageBoost ?? {}),
        },
      },
      pr: {
        ...base.priority.pr,
        ...(overrides.priority?.pr ?? {}),
        stalePenalty: {
          ...base.priority.pr.stalePenalty,
          ...(overrides.priority?.pr?.stalePenalty ?? {}),
        },
      },
      labelBoosts: {
        ...base.priority.labelBoosts,
        ...normalizeBoosts(overrides.priority?.labelBoosts),
      },
    },
    relationshipScore: {
      ...base.relationshipScore,
      ...(overrides.relationshipScore ?? {}),
    },
    implementation: {
      ...base.implementation,
      ...(overrides.implementation ?? {}),
      relationshipQualityBoosts: {
        ...base.implementation.relationshipQualityBoosts,
        ...(overrides.implementation?.relationshipQualityBoosts ?? {}),
      },
      agePenalty: {
        ...base.implementation.agePenalty,
        ...(overrides.implementation?.agePenalty ?? {}),
      },
      sizePenalty: {
        ...base.implementation.sizePenalty,
        ...(overrides.implementation?.sizePenalty ?? {}),
      },
      agentConfidenceMultipliers: {
        ...base.implementation.agentConfidenceMultipliers,
        ...(overrides.implementation?.agentConfidenceMultipliers ?? {}),
      },
      tierThresholds: {
        ...base.implementation.tierThresholds,
        ...(overrides.implementation?.tierThresholds ?? {}),
      },
    },
  };
}

export type ConfigLoadResult = {
  config: MaintainerConfig;
  path: string;
  usedDefault: boolean;
  warnings: string[];
};

export function loadConfig(configPath: string): ConfigLoadResult {
  const resolvedPath = path.resolve(configPath);
  const warnings: string[] = [];

  if (!fs.existsSync(resolvedPath)) {
    try {
      const dir = path.dirname(resolvedPath);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(resolvedPath, `${JSON.stringify(getDefaultConfig(), null, 2)}\n`, 'utf8');
      warnings.push(`Config not found; wrote defaults to ${resolvedPath}.`);
    } catch {
      warnings.push(`Config not found at ${resolvedPath}; using defaults.`);
    }
    return {
      config: mergeConfig({}),
      path: resolvedPath,
      usedDefault: true,
      warnings,
    };
  }

  try {
    const raw = fs.readFileSync(resolvedPath, 'utf8');
    const parsed = JSON.parse(raw) as Partial<MaintainerConfig>;
    return {
      config: mergeConfig(parsed),
      path: resolvedPath,
      usedDefault: false,
      warnings,
    };
  } catch (error) {
    warnings.push(`Failed to parse config at ${resolvedPath}; using defaults.`);
    return {
      config: mergeConfig({}),
      path: resolvedPath,
      usedDefault: true,
      warnings,
    };
  }
}

export function getDefaultConfig(): MaintainerConfig {
  return mergeConfig({});
}
