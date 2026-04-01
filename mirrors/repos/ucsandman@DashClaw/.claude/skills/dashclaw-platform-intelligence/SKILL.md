---
name: dashclaw-platform-intelligence
description: >
  DashClaw platform expert for integration, troubleshooting, and governance. Use when working
  with DashClaw APIs/SDKs: instrumenting agents, action recording, guard/policy checks, SSE
  real-time events, org/workspace context, auth headers (x-api-key), errors (401/403/429/503),
  building API routes, generating SDK/client methods, bootstrapping agent data, configuring
  evaluations/scorers, prompt templates/versioning, feedback capture, compliance exports, drift
  monitoring, learning analytics/velocity, scoring profiles, risk templates, CLI approval
  channel, terminal approvals, dashclaw approve, dashclaw approvals, dashclaw deny, Claude Code
  hooks, PreToolUse, PostToolUse, governed tool calls, DASHCLAW_HOOK_MODE, terminal governance.
  Trigger on: "instrument my agent", "connect my agent", "403 error", "set up monitoring",
  "evaluate outputs", "manage prompts", "collect feedback", "export compliance", "detect drift",
  "track learning", "approve from terminal", "govern Claude Code".
---

# DashClaw Platform Intelligence (v2.7)

You are a DashClaw platform expert. You know every API route, both SDKs, the security model,
compliance frameworks, evaluation engine, prompt registry, feedback loop, drift detection,
learning analytics, and architectural patterns. You generate code, diagnose issues, design
architectures, and orchestrate complex workflows.

**Zero-dependency philosophy**: All features work without any LLM API key by default. The only
optional LLM feature is the `llm_judge` scorer type in the Evaluation Framework, which degrades
gracefully when no provider is configured.

## Workflow Decision Tree

Determine which workflow to follow:

**Integrating an agent with DashClaw?** --> "Instrument My Agent" below
**Error or unexpected behavior?** --> Read [references/troubleshooting.md](references/troubleshooting.md)
**Adding a new feature to DashClaw itself?** --> "Add a DashClaw Capability" below
**Generating a client in a new language?** --> "Generate Client Code" below
**Setting up policies or guard rules?** --> "Design Policies" below
**Importing an existing agent's data?** --> "Bootstrap Agent" below
**Setting up evaluations or scoring?** --> "Configure Evaluations" below
**Managing prompt templates?** --> "Manage Prompts" below
**Collecting user feedback?** --> "Collect Feedback" below
**Exporting compliance reports?** --> "Export Compliance" below
**Monitoring for behavioral drift?** --> "Monitor Drift" below
**Tracking learning progress?** --> "Track Learning" below
**Defining quality scoring or risk templates?** --> "Configure Scoring" below
**Approving agent actions from the terminal?** --> "CLI Approval Channel" below
**Governing Claude Code tool calls with DashClaw?** --> "Claude Code Hooks" below
**General question about the platform?** --> Read [references/platform-knowledge.md](references/platform-knowledge.md)
**Need the full API surface?** --> Read [references/api-surface.md](references/api-surface.md)

## Instrument My Agent

Full integration of DashClaw into an existing agent codebase.

### 1. Detect language, install SDK

**Node.js (v2 SDK):**
```javascript
import { DashClaw } from 'dashclaw';
const dc = new DashClaw({
  baseUrl: process.env.DASHCLAW_BASE_URL || 'http://localhost:3000',
  apiKey: process.env.DASHCLAW_API_KEY,
  agentId: 'my-agent',
});
```

**Python:**
```python
from dashclaw import DashClaw
dc = DashClaw(
    base_url=os.environ.get("DASHCLAW_BASE_URL", "http://localhost:3000"),
    api_key=os.environ["DASHCLAW_API_KEY"],
    agent_id="my-agent",
)
```

> **v1 Legacy SDK:** For the full 177+ method surface (SSE events, wrapClient, pairing, full policy
> CRUD, full compliance exports, etc.), import from `dashclaw/legacy` instead. See `sdk/legacy/dashclaw-v1.js`.

### 2. Identify decision points in the agent's code

Scan for: tool/API calls (actions), conditional behavior logic (policy-relevant), risk-bearing
operations (guard-worthy).

### 3. Instrument each decision point

**Guard check** (before risky operations):
```javascript
const decision = await dc.guard({
  action_type: 'file_write', content: fileContent, risk_score: 60
});
if (decision.decision === 'block') return; // blocked by policy

// The guard response includes learning context when DashClaw has relevant data:
if (decision.learning) {
  console.log(`Recent score avg: ${decision.learning.recent_score_avg}`);
  console.log(`Drift status: ${decision.learning.drift_status}`);
  decision.learning.patterns.forEach(p => console.log(`Pattern: ${p}`));
}
```

**Action recording** (wrap every significant operation):
```javascript
const { action } = await dc.createAction({
  action_type: 'api_call',
  declared_goal: 'Fetch user profile',
  risk_score: 25,
  metadata: { endpoint: '/users/123' }
});
// ... do the work ...
await dc.updateOutcome(action.action_id, {
  status: 'completed',
  output_summary: 'Profile fetched'
});
```

**Assumption tracking:**
```javascript
await dc.recordAssumption({
  action_id: action.action_id,
  assumption: 'User timezone is UTC',
  basis: 'Derived from user profile settings'
});
```

**HITL approval** (for high-risk actions):
```javascript
const { action } = await dc.createAction({
  action_type: 'infrastructure', declared_goal: 'Resize DB cluster', risk_score: 95
});
// waitForApproval polls until approved_by metadata is present
const approved = await dc.waitForApproval(action.action_id);
```

**Open loops** (track ongoing background work):
```javascript
const { loop_id } = await dc.registerOpenLoop(action.action_id, 'background_indexing', 'Indexing docs');
// ... later ...
await dc.resolveOpenLoop(loop_id, 'resolved', 'Indexed 42 files.');
```

**Prompt injection scanning** (on user/tool input before processing):
```javascript
const scan = await dc.scanPromptInjection(userInput, { source: 'user_input' });
if (scan.recommendation === 'block') throw new Error('Prompt injection detected');
```

**Agent messaging** (inter-agent communication):
```javascript
await dc.sendMessage({
  to: 'deploy-bot', type: 'status',
  subject: 'Tests passed', body: 'All 847 tests green. Safe to deploy.',
});
const { messages } = await dc.getInbox({ unread: true });
```

**Session handoffs** (continuity across restarts):
```javascript
await dc.createHandoff({
  sessionDate: new Date().toISOString().slice(0, 10),
  summary: 'Completed migration. 3 tables updated.',
  openTasks: ['Verify row counts'],
  decisions: ['Used batch inserts'],
});
// On next startup:
const { handoff } = await dc.getLatestHandoff();
```

**User feedback** (capture end-user ratings):
```javascript
await dc.submitFeedback({
  action_id: action.action_id,
  rating: 4,
  comment: 'Fast and accurate response',
});
```

**Context threads** (reasoning trails):
```javascript
const { thread } = await dc.createThread({ name: 'Deploy analysis', summary: 'Evaluating deploy safety' });
await dc.addThreadEntry(thread.thread_id, 'Checked staging health: all green', 'observation');
await dc.addThreadEntry(thread.thread_id, 'Production deploy is safe', 'conclusion');
await dc.closeThread(thread.thread_id, 'Deploy approved after staging check');
```

### 4. Add quality scoring (recommended)

After instrumenting actions, add evaluation scoring to track output quality:

```javascript
// Create a scorer (one-time setup) — positional args: name, scorer_type, config, description
const scorer = await dc.createScorer(
  'output-quality',
  'contains',
  { keywords: ['success', 'completed'], case_sensitive: false },
  'Checks for success keywords in output'
);
```

### 5. Add env vars, validate

```bash
# .env
DASHCLAW_BASE_URL=http://localhost:3000
DASHCLAW_API_KEY=oc_live_...
```

Validate the integration:
```bash
node .claude/skills/dashclaw-platform-intelligence/scripts/validate-integration.mjs \
  --base-url http://localhost:3000 --api-key $DASHCLAW_API_KEY --full
```

## Configure Evaluations

Set up the evaluation framework to score agent outputs.

### Scorer Types

5 built-in scorer types. All work without an LLM except `llm_judge`:

| Type | Config | LLM Required |
|------|--------|-------------|
| `regex` | `{ pattern, flags }` | No |
| `contains` | `{ keywords, case_sensitive }` | No |
| `numeric_range` | `{ field, min, max }` | No |
| `custom_function` | `{ function_body }` | No |
| `llm_judge` | `{ prompt, model }` | Yes (optional) |

```javascript
// Regex scorer — positional args: (name, scorer_type, config, description)
const regex = await dc.createScorer(
  'json-format', 'regex',
  { pattern: '^\\{.*\\}$', flags: 's' },
  'Validates JSON format'
);

// Numeric range (scores metadata fields)
const range = await dc.createScorer(
  'confidence-check', 'numeric_range',
  { field: 'confidence', min: 70, max: 100 },
  'Checks confidence is in range'
);

// Custom function (full JS logic)
const custom = await dc.createScorer(
  'length-and-format', 'custom_function',
  { function_body: 'return output.length > 50 && output.includes("##") ? 1 : 0;' },
  'Checks length and markdown headers'
);
```

### Batch Evaluation Runs

> **Requires v1 SDK:** `createEvalRun` is available via `import { DashClaw } from 'dashclaw/legacy'`.

```javascript
const run = await dc.createEvalRun({
  name: 'weekly-quality-audit',
  scorer_ids: [regex.id, range.id],
  dataset: outputs.map(o => ({ output: o.text, metadata: o.meta })),
});
console.log(`Avg score: ${run.avg_score}`);
```

## Manage Prompts

Version-controlled prompt templates with mustache variable rendering.

> **Requires v1 SDK:** Template CRUD (`createTemplate`, `createVersion`, `activateVersion`, `getPromptStats`)
> is available via `import { DashClaw } from 'dashclaw/legacy'`. The v2 SDK has `renderPrompt()` for consuming templates.

```javascript
// Create template
const tmpl = await dc.createTemplate({
  name: 'deploy-check',
  content: 'Verify {{service}} deployment to {{environment}} is healthy. Check {{metric}}.',
  variables: ['service', 'environment', 'metric'],
});

// Render with variables (server-side, no LLM)
const { rendered } = await dc.renderTemplate(tmpl.id, {
  service: 'auth-api', environment: 'production', metric: 'p99 latency',
});
// "Verify auth-api deployment to production is healthy. Check p99 latency."

// Create new version
await dc.createVersion(tmpl.id, {
  content: 'Verify {{service}} on {{environment}}. Check {{metric}} and {{threshold}}.',
  change_note: 'Added threshold variable',
});

// Rollback to previous version
await dc.activateVersion(tmpl.id, 'pv_version001');

// Usage analytics
const stats = await dc.getPromptStats({ template_id: tmpl.id });
```

## Collect Feedback

Structured user feedback with auto-sentiment detection and auto-tagging.
`submitFeedback()` is in the v2 SDK. Querying and managing feedback requires v1.

> **v1 SDK methods:** `listFeedback`, `resolveFeedback`, `getFeedbackStats` require `import { DashClaw } from 'dashclaw/legacy'`.

```javascript
// Submit feedback linked to an action (v2 SDK)
const fb = await dc.submitFeedback({
  rating: 2,
  comment: 'Response was slow and inaccurate',
  action_id: 'act_xyz789',
  agent_id: 'research-bot',
});
console.log(fb.sentiment); // 'negative' (auto-detected, rule-based)
console.log(fb.tags);      // ['performance', 'accuracy'] (auto-tagged)

// Query unresolved negative feedback
const { feedback } = await dc.listFeedback({
  sentiment: 'negative', resolved: false,
});

// Resolve with note
await dc.resolveFeedback(fb.id, 'Fixed latency issue in v2.3');

// Analytics
const stats = await dc.getFeedbackStats();
// { avg_rating, sentiment_breakdown, top_tags, rating_distribution }
```

**Auto-tag categories**: performance, accuracy, cost, security, reliability, ux

## Export Compliance

> **Requires v1 SDK:** All compliance export methods require `import { DashClaw } from 'dashclaw/legacy'`.

Generate multi-framework compliance bundles with evidence packaging.

```javascript
// Generate export bundle
const exp = await dc.createComplianceExport({
  frameworks: ['soc2', 'nist-ai-rmf'],
  name: 'Q1 2026 Audit',
  window_days: 90,
  include_evidence: true, // includes guard decisions + action records
});

// Schedule recurring exports
await dc.createComplianceSchedule({
  frameworks: ['soc2'],
  cron: '0 6 1 * *', // Monthly on 1st at 6am
  name: 'Monthly SOC 2 Report',
});

// Track coverage trends
const { trends } = await dc.getComplianceTrends({ framework: 'soc2' });
trends.forEach(t => console.log(`${t.created_at}: ${t.coverage_percentage}%`));

// Download export (browser-native)
await dc.downloadComplianceExport(exp.id);
```

## Monitor Drift

> **Requires v1 SDK:** All drift detection methods require `import { DashClaw } from 'dashclaw/legacy'`.

Statistical behavioral drift detection using z-score analysis. Pure math, no LLM.

**6 tracked metrics**: risk_score, confidence, duration_ms, cost_estimate, tokens_total, learning_score

```javascript
// Step 1: Compute baselines from historical data
await dc.computeDriftBaselines({ lookback_days: 30 });

// Step 2: Detect drift (compare recent window to baselines)
const { alerts } = await dc.detectDrift({ window_days: 7 });
for (const a of alerts) {
  console.log(`[${a.severity}] ${a.metric} for ${a.agent_id}: z=${a.z_score}`);
}
// [warning] risk_score for deploy-bot: z=2.3
// [critical] cost_estimate for research-bot: z=3.8

// Severity thresholds:
// z >= 1.5 = info
// z >= 2.0 = warning
// z >= 3.0 = critical

// List unacknowledged critical alerts
const critical = await dc.listDriftAlerts({ severity: 'critical', acknowledged: false });

// Acknowledge after investigation
await dc.acknowledgeDriftAlert(alert.id);

// Stats overview
const stats = await dc.getDriftStats();
console.log(`${stats.overall.critical_count} critical, ${stats.overall.warning_count} warnings`);
```

## Track Learning

Learning analytics with velocity tracking, maturity classification, and per-skill learning curves.
**This is DashClaw's unique moat -- no other platform tracks agent learning velocity.**

> **v2 SDK:** `getLearningVelocity(lookbackDays)` and `getLearningCurves(lookbackDays)` are in v2 for read access.
> Compute methods (`computeLearningVelocity`, `computeLearningCurves`, `getLearningAnalyticsSummary`) require v1.

### Maturity Model

6 levels based on episode count, success rate, and average score:

| Level | Episodes | Success Rate | Avg Score |
|-------|----------|-------------|-----------|
| Novice | 0+ | any | any |
| Developing | 10+ | 40%+ | 40+ |
| Competent | 50+ | 60%+ | 55+ |
| Proficient | 150+ | 75%+ | 65+ |
| Expert | 500+ | 85%+ | 75+ |
| Master | 1000+ | 92%+ | 85+ |

```javascript
// Compute learning velocity (linear regression slope of scores over time)
const { results } = await dc.computeLearningVelocity({ lookback_days: 30 });
for (const r of results) {
  console.log(`${r.agent_id}: velocity=${r.velocity} pts/day, maturity=${r.maturity.level}`);
}
// deploy-bot: velocity=0.8 pts/day, maturity=proficient
// research-bot: velocity=-0.2 pts/day, maturity=competent  <-- degrading!

// Compute per-skill learning curves
await dc.computeLearningCurves({ lookback_days: 60 });
const { curves } = await dc.getLearningCurves({
  agent_id: 'deploy-bot', action_type: 'deploy',
});
curves.forEach(c => console.log(`Week of ${c.window_start}: avg=${c.avg_score}`));

// Comprehensive summary (the dashboard API — requires v1)
const summary = await dc.getLearningAnalyticsSummary();
console.log(`${summary.overall.total_episodes} episodes`);
console.log(`Top agent: ${summary.by_agent[0].agent_id} (${summary.by_agent[0].maturity_level})`);
console.log(`Velocity: ${summary.by_agent[0].velocity} pts/day`);
```

**Fetch consolidated lessons (v2 SDK):**
```javascript
// What has DashClaw learned from this agent's scored outcomes?
const { lessons, drift_warnings } = await dc.getLessons({ actionType: 'deploy' });
for (const lesson of lessons) {
  console.log(`[${lesson.action_type}] ${lesson.guidance} (confidence: ${lesson.confidence})`);
  console.log(`  Hints: risk_cap=${lesson.hints.risk_cap}, prefer_reversible=${lesson.hints.prefer_reversible}`);
}
drift_warnings.forEach(w => console.log(`[DRIFT] ${w.metric}: z=${w.z_score} (${w.severity})`));
```

## Action Context (v2.7.0)

The SDK now provides `actionContext()` (Node.js) / `action_context()` (Python) for automatic message-action correlation:

### Node.js
```javascript
const action = await claw.createAction({ action_type: 'deploy', declared_goal: 'Deploy v2' });
const ctx = claw.actionContext(action.action_id);
await ctx.sendMessage({ to: 'ops-agent', type: 'status', body: 'Deploying...' });
await ctx.recordAssumption({ assumption: 'Tests passed' });
await ctx.updateOutcome({ status: 'completed' });
```

### Python
```python
action = claw.create_action(action_type="deploy", declared_goal="Deploy v2")
with claw.action_context(action["action_id"]) as ctx:
    ctx.send_message("Deploying...", to="ops-agent")
    ctx.record_assumption({"assumption": "Tests passed"})
    ctx.update_outcome(status="completed")
```

Messages and assumptions sent through the context are automatically tagged with `action_id`, appearing in the decision timeline at `/decisions/{actionId}`.

## Add a DashClaw Capability

Full-stack scaffold when adding a new API route to the DashClaw platform.

### Files to create/modify (in order)

1. **Migration** `scripts/migrate-<domain>.mjs` -- create tables with TEXT PKs, crypto-random IDs
2. **Repository** `app/lib/repositories/<domain>.repository.js` -- all SQL here
3. **Lib module** `app/lib/<domain>.js` -- business logic (pure functions where possible)
4. **Route handler** `app/api/<domain>/route.js` -- imports from repository, never inline SQL
5. **Demo fixtures** `app/lib/demo/demoFixtures.js` (if route needs demo mode)
6. **Demo middleware** handler in `middleware.js` (if route needs demo mode)
7. **Node SDK** method in `sdk/dashclaw.js` (camelCase)
8. **Python SDK** method in `sdk-python/dashclaw/client.py` (snake_case)
9. **Docs page** navItems entry + MethodEntry in `app/docs/page.js`
10. **Node README** section in `sdk/README.md`
11. **Python README** section in `sdk-python/README.md`
12. **Parity matrix** counts in `docs/sdk-parity.md`

### Route handler pattern
```javascript
import { getSql } from '../../lib/db.js';
import { getOrgId } from '../../lib/org.js';
import { listThings } from '../../lib/repositories/<domain>.repository.js';

export async function GET(request) {
  try {
    const sql = getSql();
    const orgId = getOrgId(request);
    const result = await listThings(sql, orgId, {});
    return Response.json(result);
  } catch (err) {
    console.error('[DOMAIN] GET error:', err.message);
    return Response.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

### Post-scaffold commands (mandatory)
```bash
npm run openapi:generate && npm run api:inventory:generate
npm run docs:check && npm run route-sql:check
npm run openapi:check && npm run api:inventory:check
npm run lint && npm run build
```

## Generate Client Code

Generate a DashClaw client in any language from the API contracts.

1. Read OpenAPI spec: `docs/openapi/critical-stable.openapi.json`
2. Read both SDKs for patterns: `sdk/dashclaw.js` (v2, 45 methods), `sdk-python/dashclaw/client.py`
3. Constructor (v2): `baseUrl`, `apiKey`, `agentId`
4. Auth: `x-api-key` header on every request
5. Error types: `GuardBlockedError`, `ApprovalDeniedError`
6. Minimum viable methods (v2): `guard`, `createAction`, `updateOutcome`, `recordAssumption`, `waitForApproval`, `sendMessage`, `createHandoff`, `scanPromptInjection`, `submitFeedback`

For the full 130+ route API surface with method mappings, read [references/api-surface.md](references/api-surface.md).

## Configure Scoring

Set up user-defined quality profiles and risk templates:

### Step 1: Auto-calibrate from your real data

```javascript
// Analyze your historical actions to get suggested thresholds
const calibration = await dc.autoCalibrate({
  action_type: 'deploy',
  lookback_days: 30,
});
// Returns percentile-based suggestions for each metric
// calibration.suggestions[0] = {
//   metric: 'duration_ms', distribution: { p25: 3000, p50: 8000, p75: 20000 },
//   suggested_scale: [{ label: 'excellent', operator: 'lte', value: 3000, score: 100 }, ...]
// }
```

```python
calibration = dc.auto_calibrate(action_type="deploy", lookback_days=30)
```

### Step 2: Create a scoring profile with weighted dimensions

```javascript
const profile = await dc.createScoringProfile({
  name: 'deploy-quality',
  action_type: 'deploy',
  composite_method: 'weighted_average', // or 'minimum', 'geometric_mean'
  dimensions: [
    {
      name: 'Speed', data_source: 'duration_ms', weight: 0.3,
      scale: [
        { label: 'excellent', operator: 'lt', value: 30000, score: 100 },
        { label: 'good', operator: 'lt', value: 60000, score: 75 },
        { label: 'acceptable', operator: 'lt', value: 120000, score: 50 },
        { label: 'poor', operator: 'gte', value: 120000, score: 20 },
      ],
    },
    {
      name: 'Reliability', data_source: 'confidence', weight: 0.4,
      scale: [
        { label: 'excellent', operator: 'gte', value: 0.9, score: 100 },
        { label: 'good', operator: 'gte', value: 0.7, score: 75 },
        { label: 'poor', operator: 'lt', value: 0.7, score: 25 },
      ],
    },
    {
      name: 'Cost', data_source: 'cost_estimate', weight: 0.3,
      scale: [
        { label: 'excellent', operator: 'lt', value: 0.01, score: 100 },
        { label: 'good', operator: 'lt', value: 0.05, score: 75 },
        { label: 'poor', operator: 'gte', value: 0.05, score: 30 },
      ],
    },
  ],
});
```

```python
profile = dc.create_scoring_profile(
    name="deploy-quality",
    action_type="deploy",
    composite_method="weighted_average",
    dimensions=[
        {"name": "Speed", "data_source": "duration_ms", "weight": 0.3,
         "scale": [
             {"label": "excellent", "operator": "lt", "value": 30000, "score": 100},
             {"label": "good", "operator": "lt", "value": 60000, "score": 75},
             {"label": "poor", "operator": "gte", "value": 60000, "score": 20},
         ]},
        {"name": "Reliability", "data_source": "confidence", "weight": 0.4,
         "scale": [
             {"label": "excellent", "operator": "gte", "value": 0.9, "score": 100},
             {"label": "poor", "operator": "lt", "value": 0.7, "score": 25},
         ]},
        {"name": "Cost", "data_source": "cost_estimate", "weight": 0.3,
         "scale": [
             {"label": "excellent", "operator": "lt", "value": 0.01, "score": 100},
             {"label": "poor", "operator": "gte", "value": 0.05, "score": 30},
         ]},
    ],
)
```

**Data sources**: `duration_ms`, `cost_estimate`, `tokens_total`, `risk_score`, `confidence`, `eval_score`, `metadata_field` (dot-path), `custom_function` (arbitrary JS).

**Composite methods**: `weighted_average` (default -- sum of score x weight), `minimum` (strictest -- one bad dimension tanks the whole score), `geometric_mean` (balanced -- heavily penalizes zeros).

### Step 3: Score actions against your profile

```javascript
// Single action
const result = await dc.scoreWithProfile(profile.id, {
  duration_ms: 25000,
  confidence: 0.95,
  cost_estimate: 0.008,
});
// result.composite_score = 92.5
// result.dimensions = [{ dimension_name: 'Speed', score: 100, label: 'excellent' }, ...]

// Batch scoring
const batch = await dc.batchScoreWithProfile(profile.id, [
  { duration_ms: 500, confidence: 0.98 },
  { duration_ms: 10000, confidence: 0.5 },
]);
// batch.summary = { total: 2, scored: 2, avg_score: 72.3 }
```

```python
result = dc.score_with_profile(profile["id"], {
    "duration_ms": 25000, "confidence": 0.95, "cost_estimate": 0.008,
})

batch = dc.batch_score_with_profile(profile["id"], [
    {"duration_ms": 500, "confidence": 0.98},
    {"duration_ms": 10000, "confidence": 0.5},
])
```

### Step 4: Set up risk templates (replaces hardcoded risk numbers)

```javascript
// Instead of agents guessing riskScore: 40, DashClaw computes it:
const template = await dc.createRiskTemplate({
  name: 'Production Safety',
  base_risk: 20,
  rules: [
    { condition: "metadata.environment == 'production'", add: 25 },
    { condition: "metadata.modifies_data == true", add: 15 },
    { condition: "metadata.irreversible == true", add: 30 },
  ],
});
// Production data-modifying deploy: 20 + 25 + 15 = 60 risk
// Staging read-only query: 20 + 0 + 0 = 20 risk
```

```python
template = dc.create_risk_template(
    name="Production Safety",
    base_risk=20,
    rules=[
        {"condition": "metadata.environment == 'production'", "add": 25},
        {"condition": "metadata.modifies_data == true", "add": 15},
        {"condition": "metadata.irreversible == true", "add": 30},
    ],
)
```

**Condition operators**: `==`, `!=`, `>`, `>=`, `<`, `<=`, `contains`. Supports nested paths like `metadata.deploy.target`.

**ID prefixes**: `sp_` (profiles), `sd_` (dimensions), `ps_` (profile scores), `rt_` (risk templates).

## Design Policies

> **Requires v1 SDK:** Policy CRUD (`importPolicies`, `createPolicy`, `testPolicies`) requires
> `import { DashClaw } from 'dashclaw/legacy'`. The v2 SDK has `guard()` for runtime policy checks.

Set up behavior guard policies for agent governance.

**Guard modes:** `off` (no checks), `warn` (log but allow), `enforce` (block on policy match)

**Common patterns:**
- Cost ceiling: block when `cost_estimate > threshold`
- Risk threshold: require approval when `risk_score >= 70`
- Action type allowlist: block unknown action types
- Content filter: guard against sensitive data in outputs

**YAML policy example:**
```yaml
name: production-safety
policy_type: risk_threshold
rules:
  max_risk_without_approval: 60
  blocked_action_types: [delete_database, modify_production]
  require_approval_for: [deploy, infrastructure_change]
```

```javascript
// Import a policy pack
await dc.importPolicies({ pack: 'production' });

// Custom policy
await dc.createPolicy({
  name: 'cost-ceiling',
  policy_type: 'cost_limit',
  rules: { max_cost_per_action: 5.00, max_daily_spend: 100.00 },
});

// Test policies without enforcing
const results = await dc.testPolicies();
console.log(`${results.passed} passed, ${results.failed} failed`);

// Generate compliance proof report
const proof = await dc.getProofReport({ format: 'json' });
```

## CLI Approval Channel

The DashClaw CLI lets operators approve, deny, and monitor agent actions from the terminal without opening a browser. This is the primary interface for developers using Claude Code, Codex, Gemini CLI, or any terminal-first workflow.

### Package

The CLI is published as `@dashclaw/cli` and installed globally:

```bash
npm install -g @dashclaw/cli
```

### Required environment variables

```bash
export DASHCLAW_BASE_URL=https://your-dashclaw-instance.com
export DASHCLAW_API_KEY=your_operator_api_key
export DASHCLAW_AGENT_ID=cli-operator  # optional, default is "cli-operator"
```

### Commands

**Interactive approval inbox:**
```bash
dashclaw approvals
```
Opens a live terminal inbox showing all pending actions. Navigate with arrow keys. Press A to approve, D to deny, R to open the replay URL in a browser, Q to quit. The browser dashboard updates in real time via SSE when you approve or deny from the terminal.

**Non-interactive single approval:**
```bash
dashclaw approve <actionId> [--reason "Reviewed and safe to proceed"]
```
Approves a specific action and prints the replay URL to stdout.

**Non-interactive denial:**
```bash
dashclaw deny <actionId> [--reason "Outside approved change window"]
```

### Terminal approval output block

When an agent calls `waitForApproval()`, the Node SDK prints a structured block to stdout immediately before blocking:

```
+== DashClaw Approval Required =====================+
  Action ID:   act_01j9z7k2m8n3p4q5r6s7t8u9v0
  Agent:       deploy-bot
  Action:      deploy
  Policy:      require_approval
  Risk Score:  85
  Goal:        Deploy auth service v2 to production

  Replay:      https://your-instance.com/replay/act_01j9z...

  Waiting for approval... (Ctrl+C to abort)
+===================================================+
```

The agent process blocks until an operator approves or denies from any channel (terminal or browser). The SSE stream syncs the decision instantly across all connected clients.

### How approval sync works

The approval flows through a single path regardless of channel:

1. Agent calls `waitForApproval(actionId)` and blocks
2. Operator approves via `dashclaw approve <id>` or the /approvals dashboard
3. `POST /api/actions/:id/approve` commits the decision to Postgres
4. An `action.updated` event is published to the Redis SSE stream
5. The SDK's SSE listener unblocks the agent within milliseconds
6. The browser dashboard reflects the change on the next SSE heartbeat

### Replay links

Every governed action has a permanent replay URL:
```
<DASHCLAW_BASE_URL>/replay/<actionId>
```

This URL is printed in the terminal approval block, in the `dashclaw approve` output, and in the `dashclaw approvals` inbox. It opens a full decision evidence page showing the policy that triggered the gate, the agent's declared goal, assumptions, risk score, and outcome.

## Claude Code Hooks

The DashClaw hooks for Claude Code intercept tool calls before and after execution, enforcing guard policies without any SDK instrumentation in your agent code. Drop two Python scripts into `.claude/hooks/` and every Bash, Edit, Write, and MultiEdit call Claude makes is governed by your DashClaw policies.

### Files

```
hooks/
  dashclaw_pretool.py    # PreToolUse hook: guard check + block/approve
  dashclaw_posttool.py   # PostToolUse hook: record outcome as evidence
  settings.json          # Snippet to merge into .claude/settings.json
  README.md
```

Download from the DashClaw repo at `hooks/` in the root directory.

### Installation

1. Copy `dashclaw_pretool.py` and `dashclaw_posttool.py` to `.claude/hooks/` in your project
2. Merge the `hooks` block from `hooks/settings.json` into your `.claude/settings.json`
3. Set the three required environment variables:
   ```bash
   export DASHCLAW_BASE_URL=https://your-dashclaw-instance.com
   export DASHCLAW_API_KEY=your_operator_api_key
   export DASHCLAW_HOOK_MODE=enforce  # or "observe" to log only
   ```

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| DASHCLAW_BASE_URL | Yes | none | Your DashClaw instance URL |
| DASHCLAW_API_KEY | Yes | none | Operator API key |
| DASHCLAW_AGENT_ID | No | claude-code | Agent ID recorded in decisions |
| DASHCLAW_HOOK_MODE | No | enforce | enforce blocks on policy violations; observe logs only |
| DASHCLAW_RISK_THRESHOLD | No | 60 | Base risk threshold for elevated scoring |

### Governed tools

The hooks intercept: `Bash`, `Edit`, `Write`, `MultiEdit`. All other tools pass through ungoverned.

### Decision behavior

| Guard Decision | enforce mode | observe mode |
|---|---|---|
| allow | Tool proceeds silently | Tool proceeds silently |
| warn | Warning printed to stderr, tool proceeds | Same |
| block | Tool blocked (exit 2), reason shown | Warning only, tool proceeds |
| require_approval | Action created as pending, polls for 30s, blocks if not approved | Warning only |

### Action type mapping

The hooks map tool calls to DashClaw action types automatically:

**Bash commands:**
- `git push`, `git merge`, `git rebase` -> `deploy`, risk 80, irreversible
- `npm run deploy`, `vercel`, `kubectl`, `terraform` -> `deploy`, risk 75-85, irreversible
- `rm -rf`, `DROP TABLE`, `DELETE FROM` -> `security`, risk 90, irreversible
- `curl`, `wget` -> `api`, risk 40
- default -> `other`, risk 20

**File edits (Edit/Write/MultiEdit):**
- Path matches `.env`, `secret`, `credential`, `private_key` -> `security`, risk 85
- Path matches `migration`, `schema` -> `migrate`, risk 70, irreversible
- Path matches `deploy`, `terraform`, `kubernetes` -> `deploy`, risk 75
- Path matches `auth`, `jwt`, `token`, `password` -> `security`, risk 75
- default -> `other`, risk 15

### Failure safety

If `DASHCLAW_BASE_URL` or `DASHCLAW_API_KEY` are not set, both scripts exit 0 silently. If the DashClaw API is unreachable (timeout, network error), the hooks exit 0 and print `[DashClaw] Guard unavailable, proceeding` to stderr. Claude Code is never blocked because DashClaw is down.

### Approving from the terminal

When a hook enters approval-required state, it prints the action ID and replay URL. Approve from a second terminal:

```bash
dashclaw approve act_01j9z7k2m8n3p4q5r6s7t8u9v0 --reason "Reviewed, safe to proceed"
```

The hook polling loop detects the approval within 3 seconds and unblocks Claude Code.

### Evidence trail

After every governed tool execution, `dashclaw_posttool.py` records the outcome as a DashClaw action. This means every file edit and bash command Claude runs in your project becomes a replayable evidence record at `<DASHCLAW_BASE_URL>/replay/<actionId>`.

## Bootstrap Agent

Import an existing agent's workspace data into DashClaw:

```bash
node .claude/skills/dashclaw-platform-intelligence/scripts/bootstrap-agent-quick.mjs \
  --dir "/path/to/agent/workspace" \
  --agent-id "my-agent" \
  --validate
```

The bootstrap scanner auto-discovers: decisions, lessons, goals, context threads, relationships,
memory files, and preferences from common agent directory structures.

For full options: `node scripts/bootstrap-agent-quick.mjs --help`
