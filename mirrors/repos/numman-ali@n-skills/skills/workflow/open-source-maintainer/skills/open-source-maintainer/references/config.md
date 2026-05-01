# Maintainer Config

## At a glance

- **Purpose:** Control triage scoring, stale policy, label mapping, and derived metrics.
- **Use when:** Scoring/actionability feels “off,” you want different prioritization, or you’re changing automation policy.
- **Output:** Proposed edits to `.github/maintainer/config.json` with a short rationale.
- **Do not:** Manually edit `.github/maintainer/semantics.generated.json` (it is auto-managed).

Machine-readable configuration file for the maintainer workflow.

Place it at:

```
.github/maintainer/config.json
```

The triage script reads this file to drive scoring, labels, and stale policy. If it is missing, the script falls back to built-in defaults and prints a warning.

## Config Template

```json
{
  "schemaVersion": 1,
  "reportsDir": "reports",
  "stateFile": ".github/maintainer/state.json",
  "noMergeExternalPRs": true,
  "semantics": {
    "intent": {
      "bug": ["bug", "crash", "error", "exception"],
      "feature": ["feature request", "enhancement"],
      "question": ["how do i", "question"],
      "support": ["help", "support"],
      "meta": ["roadmap", "governance"]
    },
    "needsInfo": {
      "repro": ["steps to reproduce", "repro steps"],
      "expected": ["expected behavior"],
      "actual": ["actual behavior"],
      "environment": ["environment", "os"],
      "version": ["version", "node version"],
      "logs": ["logs", "stack trace"],
      "testPlan": ["test plan", "testing"]
    },
    "environmentTokens": ["windows", "macos", "linux", "node", "npm"],
    "relationship": {
      "linkKeywords": ["fixes", "closes", "resolves", "addresses"],
      "duplicateHints": ["duplicate", "same issue"]
    },
    "errors": {
      "signatures": [],
      "keywords": ["error", "exception", "failed", "crash"]
    }
  },
  "heuristics": {
    "needsInfo": {
      "enabled": true,
      "threshold": 2,
      "issueSignals": {
        "missingRepro": { "enabled": true, "applyTo": ["bug", "unknown"] },
        "missingExpectedActual": { "enabled": true, "applyTo": ["bug", "unknown"] },
        "missingEnvironment": { "enabled": true, "applyTo": ["bug", "support", "question", "unknown"] },
        "missingVersion": { "enabled": true, "applyTo": ["bug", "support", "question", "unknown"] },
        "missingLogs": { "enabled": true, "applyTo": ["bug", "support", "unknown"] }
      },
      "prSignals": {
        "missingTestPlan": { "enabled": true },
        "missingDescription": { "enabled": true }
      },
      "weights": {
        "missingRepro": 2,
        "missingExpectedActual": 1,
        "missingEnvironment": 1,
        "missingVersion": 1,
        "missingLogs": 1,
        "missingTestPlan": 1,
        "missingDescription": 1
      }
    },
    "duplicates": {
      "titleSimilarityThreshold": 0.6,
      "overlapThreshold": 0.35,
      "requireSharedError": false
    },
    "relationshipQuality": {
      "strongOverlapThreshold": 0.45,
      "mediumOverlapThreshold": 0.15,
      "strongWhenExplicit": true,
      "defaultWhenLinked": "medium"
    }
  },
  "sentiment": {
    "positiveWords": ["thanks", "great", "helpful", "fixed"],
    "negativeWords": ["broken", "error", "crash", "fail"]
  },
  "staleDays": {
    "issues": 60,
    "prs": 30
  },
  "labels": {
    "blocked": ["blocked", "on-hold"],
    "needsInfo": ["needs-info", "needs-more-info", "waiting-for-response"],
    "needsDecision": ["needs-decision"],
    "closable": ["duplicate", "wontfix", "invalid", "out-of-scope"]
  },
  "typeLabels": {
    "bug": ["bug"],
    "feature": ["feature", "enhancement"],
    "question": ["question"],
    "support": ["support"],
    "meta": ["meta", "governance", "roadmap"]
  },
  "priority": {
    "issue": {
      "commentWeight": 2,
      "reactionWeights": {
        "THUMBS_UP": 3,
        "THUMBS_DOWN": 2,
        "HEART": 2
      },
      "typeBoosts": {
        "bug": 10,
        "feature": 5
      },
      "stalePenalty": {
        "over30": -5,
        "over60": -10
      },
      "ageBoost": {
        "over30AndFresh": 5
      }
    },
    "pr": {
      "commentWeight": 2,
      "reviewWeight": 3,
      "approvalBoost": 8,
      "ciSuccessBoost": 6,
      "unresolvedThreadsPenalty": -5,
      "changesRequestedPenalty": -5,
      "draftPenalty": -8,
      "stalePenalty": {
        "over14": -5,
        "over30": -10
      }
    },
    "labelBoosts": {
      "security": 40,
      "critical": 25,
      "high-priority": 15
    }
  },
  "relationshipScore": {
    "overlapWeight": 30,
    "explicitLinkBoost": 8,
    "linkedIssuesWeight": 2,
    "mentionedByWeight": 2,
    "linkedIssuePriorityWeight": 0.15
  },
  "implementation": {
    "commentWeight": 1,
    "reviewWeight": 2,
    "reviewCommentWeight": 1,
    "reactionWeight": 1,
    "linkedIssuePriorityWeight": 0.6,
    "linkedIssueReactionWeight": 0.3,
    "linkedIssueSentimentWeight": 0.2,
    "relationshipScoreWeight": 0.5,
    "relationshipQualityBoosts": {
      "strong": 6,
      "medium": 3,
      "weak": 0,
      "none": -2
    },
    "touchesTestsBoost": 5,
    "ciSuccessBoost": 6,
    "ciFailurePenalty": -6,
    "changesRequestedPenalty": -8,
    "unresolvedThreadsPenalty": -4,
    "draftPenalty": -10,
    "agePenalty": {
      "over14": -3,
      "over30": -7,
      "over60": -12
    },
    "sizePenalty": {
      "filesOver10": -3,
      "filesOver25": -7,
      "linesOver500": -8,
      "linesOver1000": -12
    },
    "agentScoreWeight": 1,
    "agentConfidenceMultipliers": {
      "high": 1.5,
      "medium": 1,
      "low": 0.5,
      "unset": 0
    },
    "scoreFloor": 0,
    "tierThresholds": {
      "strong": 40,
      "medium": 20
    }
  }
}
```

## Notes

- All label names are matched case-insensitively.
- `labelBoosts` apply to both issues and PRs.
- `noMergeExternalPRs` is a policy guardrail used by docs and agent workflow.
- `stateFile` stores the last run and hashes for delta reports.
- `sentiment` uses a small lexicon; extend for non-English repos if needed.
- `implementation` weights tune the auto score; agent adjustments are recorded in `.github/maintainer/notes/`.
- `semantics` and `heuristics` drive all derived metrics (type classification, actionability, duplicates, relationship quality).
- `relationshipScore` weights control PR-to-issue relationship scoring.
- `.github/maintainer/semantics.generated.json` is auto-managed by the agent and merged each run.
