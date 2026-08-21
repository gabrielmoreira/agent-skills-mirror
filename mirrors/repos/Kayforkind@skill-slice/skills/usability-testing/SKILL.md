---
name: usability-testing
description: "Plans and runs moderated or unmoderated usability sessions: 5-8 formative or 20-40+ summative recruits, think-aloud, TSR/ToT/SUS, and a severity-coded JSON report. Use when the user asks for a usability test, Maze or Lookback session, SUS score, or prototype validation with participants. Never a discovery-interview synthesizer and not a WCAG-only accessibility audit."
version: 1.0.1
domain: ui-ux
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

# Usability Testing

## When to Use

- **Use this skill when**: Planning, executing, or summarizing usability tests (moderated or unmoderated) for design prototypes, websites, or mobile apps.
- **Trigger keywords**: "usability test", "user testing", "moderated session", "unmoderated study", "SUS score", "task success rate", "think-aloud", "UX research plan", "prototype validation".
- **Route to Research-Ideation (Summarize Interview)**: If reviewing open-ended discovery interviews, user habits, or workflow conversations that do not involve active prototype interaction.
- **Route to Research-Ideation (Product Feedback Synthesizer)**: If analyzing multi-channel product tickets, NPS data, or App Store reviews.

## Prerequisites

- A functional interactive prototype (e.g., Figma link) or staging site URL.
- A usability test plan detailing target tasks, success metrics, and user profiles.
- Consent forms and NDAs prepared for all participants before testing unreleased designs or recording sessions.
- A 20% recruit buffer to account for no-shows.

## Procedure

### 1. Define Objectives and Participant Profile

1. Draft a usability test plan using the template below. Specify 1–3 primary objectives.
2. Identify user segments. Plan for **5–8 participants per distinct segment** for formative (qualitative) studies, or **20–40+ participants** for summative (quantitative) validation.
3. Write screener criteria that match the target demographic (e.g., "Must have completed an online purchase in the last 30 days").

**Usability Test Plan Template:**

```markdown
# Usability Test Plan: [Project Name]

## Objectives
- [Objective 1: e.g., Validate checkout funnel drop-off points]
- [Objective 2: e.g., Evaluate discoverability of the filter panel]

## Participant Profile & Recruitment
- **Target Count**: e.g., 5-8 participants per user segment
- **Key Demographics**: e.g., Online shoppers, active mobile users
- **Screener Criteria**: e.g., Must have completed an online purchase in the last 30 days

## Methodology
- **Format**: [Remote / In-Person]
- **Type**: [Moderated / Unmoderated]
- **Tools**: [e.g., Maze, Figma, Lookback]

## Tasks & Scenarios
1. **Scenario 1: [Context]**
   - *Task*: [Action required]
   - *Success Criteria*: [Expected end state]
   - *Follow-up questions*: [Probe questions]

2. **Scenario 2: [Context]**
   - *Task*: [Action required]
   - *Success Criteria*: [Expected end state]
```

### 2. Choose Methodology

| Method | Best For | Participant Count |
|---|---|---|
| Moderated | Early-stage prototypes, complex B2B workflows, concept evaluation | 5–8 per segment |
| Unmoderated | Finalized consumer flows (checkout, login), large-scale quantitative metrics | 20–40+ |
| Formative (Qualitative) | Finding *why* interfaces fail, understanding mental models | 5–8 per segment |
| Summative (Quantitative) | Validating *how much* design updates improve TSR, SUS, ToT | 20–40+ |

### 3. Prepare Tasks and Scenarios

1. Write each task as a scenario with context, not a directive command. Example: *"You need to buy a gift for a friend under $50. Show me how you'd do that on this site."*
2. Define explicit success criteria for each task (the expected end state).
3. Prepare neutral follow-up probes. Use scripts like: *"What did you expect to happen when you clicked that?"*
4. Prepare a post-test SUS questionnaire (10 standardized items, scored 0–100).

### 4. Set Up Testing Platform

- **Remote unmoderated**: Use [Maze](https://www.maze.co), [UXtweak](https://www.uxtweak.com), or [PlaybookUX](https://www.playbookux.com). These support native Figma prototype syncing and heatmaps.
- **Remote moderated**: Use Lookback or Zoom with screen sharing.
- **AI-moderated**: Platforms like **Koji** and **CleverX** deploy autonomous AI moderators to probe users, bridging unmoderated scale with moderated depth.
- Ensure prototype links support mobile web previews and offline fallback layouts for users on low-bandwidth networks.

### 5. Facilitate Sessions (Moderated)

1. **Establish comfort**: Begin by stating: *"We are testing the product, not you. There are no right or wrong answers."*
2. **Encourage think-aloud**: Remind the participant to verbalize thoughts, doubts, and emotions as they navigate.
3. **Avoid leading questions**: Never ask *"Was that easy?"* Ask instead: *"How was that experience for you?"*
4. **Avoid intervention**: If a participant gets stuck, resist the urge to help immediately. Observe how they attempt to resolve the issue.
5. Record timestamps for every observed blocker, error, or moment of confusion.

### 6. Collect Metrics

Track the following for each task:

- **Task Success Rate (TSR)**: Percentage of participants who successfully complete the task.
- **Time-on-Task (ToT)**: Average duration required to complete the task.
- **Error Rate**: Average number of errors or incorrect clicks per participant per task.
- **System Usability Scale (SUS)**: Standardized 10-item questionnaire yielding a score from 0 to 100.
- **Critical blockers**: Any issue that prevents task completion entirely.

### 7. Analyze and Report

1. Categorize every observed blocker by severity: **Critical**, **Major**, or **Minor**.
2. Reference timestamped recording clips for every documented issue.
3. Verify whether keyboard-only or screen-reader users encountered blockers (WCAG 2.2 accessibility checks).
4. Produce the output report conforming to the JSON schema below.

**Usability Metrics JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UsabilityTestingReport",
  "type": "object",
  "properties": {
    "testId": { "type": "string" },
    "methodology": { "type": "string", "enum": ["moderated", "unmoderated"] },
    "totalParticipants": { "type": "integer" },
    "taskMetrics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "taskId": { "type": "string" },
          "description": { "type": "string" },
          "successRatePercent": { "type": "number", "minimum": 0, "maximum": 100 },
          "averageTimeSeconds": { "type": "number" },
          "criticalBlockers": {
            "type": "array",
            "items": { "type": "string" }
          }
        },
        "required": ["taskId", "description", "successRatePercent", "averageTimeSeconds", "criticalBlockers"]
      }
    },
    "systemUsabilityScaleScore": { "type": "number", "minimum": 0, "maximum": 100 }
  },
  "required": ["testId", "methodology", "totalParticipants", "taskMetrics"]
}
```

## Pitfalls

- **Leading the participant**: Providing hints or explaining how a feature works during a testing session invalidates behavioral data. Never intervene unless the participant is completely blocked and has given up.
- **Over-modifying prototypes mid-study**: Making changes to Figma designs between sessions invalidates comparisons across participants. Lock the prototype before the first session.
- **Focusing on opinions over behavior**: Prioritizing participant statements like *"I like this blue"* over their actual interaction behaviors (e.g., failing to click the blue button). Always weight observed action above self-reported preference.
- **Insufficient sample size**: Running formative studies with fewer than 5 users per segment risks missing critical issues. Running quantitative validation with fewer than 20 participants produces statistically inconclusive results.
- **Recording sensitive data**: Do not record password input screens or display personal account details in shared reports. Protect participant privacy.
- **Skipping accessibility checks**: Modern usability testing protocols require verifying WCAG 2.2 accessibility parameters — interactive components must support screen reader cues and keyboard focus mapping.
- **No backup plan for prototype failures**: If a Figma link fails or runs slowly during a session, switch immediately to a backup static layout deck and document the tech issue.

## Verification

Before finalizing any usability test report, confirm:

1. **Every blocker is categorized**: No unresolved blockers remain. Each is labeled Critical, Major, or Minor.
2. **Video grounding exists**: Every documented issue references a timestamped recording clip.
3. **Accessibility verified**: Report states whether keyboard-only or screen-reader users encountered blockers.
4. **SUS score computed**: If summative, the System Usability Scale score (0–100) is present and calculated per the standard methodology.
5. **JSON schema conformance**: The output report validates against the `UsabilityTestingReport` JSON schema above.
6. **Consent and NDA on file**: All participants signed consent forms before the session began.

**Quick validation checklist:**

- [ ] Test plan defines objectives, participant profile, and success criteria
- [ ] Prototype link tested and functional before first session
- [ ] 5–8 users per segment (formative) or 20–40+ (summative) recruited
- [ ] 20% no-show buffer applied to recruitment
- [ ] Facilitator script uses neutral, non-leading language
- [ ] All sessions recorded with timestamps
- [ ] Blockers categorized by severity
- [ ] Accessibility checks performed and documented
- [ ] Report conforms to JSON output schema

## Related Skills

- **research-ideation**: Use for open-ended discovery interviews, workflow conversations, or multi-channel product feedback synthesis that does not involve active prototype interaction.
- **accessibility-audit**: Use for systematic WCAG 2.2 conformance testing separate from user-session-based usability testing.

## Source Anchors

- [Nielsen Norman Group Usability Testing 101](https://www.nngroup.com/articles/usability-testing-101/)
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)
- [Maze Usability Testing Suite](https://maze.co/)
- [UXtweak Remote Testing Platform](https://www.uxtweak.com/)
- [PlaybookUX Research Platform](https://www.playbookux.com/)

## Changelog

- **2026-05-30**: Modernized skill file created. Updated frontmatter, corrected second-person phrasing, removed boilerplate, and added Maze, UXtweak, and AI-moderation details.
- **2026-05-31**: Production-grade rewrite with progressive disclosure structure, explicit procedure steps, JSON schema, and verification checklist.
