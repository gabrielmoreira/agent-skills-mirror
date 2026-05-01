---
name: toprank-investigate-drop
description: Investigate an organic traffic drop for one registered site and produce a ranked recovery plan with artifacts.
metadata: { "openclaw": { "emoji": "🚨", "homepage": "https://github.com/nowork-studio/toprank", "requires": { "bins": ["python3"] } } }
---

# Toprank Investigate Drop

1. Read `{baseDir}/../../shared/adapter-rules.md`.
2. Read `{baseDir}/../../shared/artifact-contract.md`.
3. Read `{baseDir}/../../shared/policy.md`.
4. Resolve the target site, load prior audits and latest state, then compare the current problem against the site's recent history before choosing the next recovery action.
5. Read and follow the canonical Toprank skill at `{baseDir}/../../../seo/seo-analysis/SKILL.md`.
6. Convert the investigation into a structured recovery run using `python3 {baseDir}/../../bin/investigate_drop.py <site> --summary "..." --likely-cause "..."`.
7. If the drop points to a specific URL, include `--target-url <url>` so the adaptive layer queues a follow-up page-improvement task.
8. Verify that the run wrote `audit.json`, `action-plan.json`, and `verification.json`, plus any follow-up queue items.
9. If the next action requires editing a site repo, CMS, publishing content, or opening a PR, stop and ask for approval before doing it.

## Wrapper job

Use this when the operator reports a traffic loss or ranking decline.

Your job:
- identify likely causes,
- separate technical issues from content/intent issues,
- rank the fastest and safest recovery actions,
- write `audit.json`, `action-plan.json`, and `verification.json`.

If the drop investigation suggests a page-level fix, queue a follow-up `toprank-improve-page` task.
