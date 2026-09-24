# Steward: An Owner Sentence Becomes A Confirmed Team

Status: qualification case. It records what the local steward journey proves on
the workspace today, which beats are still unproven, and how to reproduce both.
It is product guidance, not a new capability, contract or scheduler.

The case is grounded in one deterministic browser scenario
(`examples/personal-workspace-browser/steward-journey.mjs`) that runs on synthetic
data. The fixture substitutes the agent turn; everything the case describes is a
fact the workspace surfaces render, not a claim about a live Goal.

## When This Case Applies

- an owner wants work to start from one sentence instead of a filled-in form;
- the work needs more than one Agent or more than one lane, so staffing is
  itself part of the answer;
- the owner wants to keep confirming, correcting and reading results in one
  place instead of relaying between Agent conversations.

## The Journey

| Beat | What the owner does | What the workspace shows | State |
| --- | --- | --- | --- |
| 1 | Looks at the first screen | Goal board lanes (needs you / running / observing / scheduled), each Goal card naming its Agent and its next sentence | Proven |
| 2 | Asks the steward in the Goal conversation | The steward's bounded prompt row (`询问下一步` / `向 Agent 获取进度报告` / `配置定时检查` / `看阻塞` / `查证据`) sends its message on click and leaves no draft, the ask becomes an accepted Turn, and the admitted team plan card lands in the same conversation | Proven |
| 3 | Reads the card | Per lane: the Agent, the first bounded Todo with priority and action kind, the acceptance signal, and an explicitly unstaffed lane that keeps the work it did not staff; the quota envelope and stop condition; a statement that confirming is what creates the lanes | Proven |
| 4 | Confirms | Exactly one apply and one durable write; the result names each assigned lane and each item left unstaffed with its reason, and says the execution progress is not what this result claims | Proven |
| 5 | Checks who can actually work | — | Gap 1 |
| 6 | Corrects or pauses one lane | — | Gap 2 |
| 7 | Waits for a lane to fail and asks who fixes it / judges completion | — | Gaps 3, 4 |

Beats 5–7 are recorded by the scenario as typed gaps with the probe that looked
for them. They are not "not implemented here" hand-waving: the scenario names
the selectors and phrases it searched for and what it found instead.

## Patterns

1. **Ask for an outcome, not an org chart.** One sentence with the outcome and
   the constraint produces a plan card; naming Agents before the outcome turns
   coordination into the owner's job.
2. **Read four facts before confirming.** Agent, first bounded Todo, acceptance
   signal and staffing gap. A card that cannot show a gap is not yet reviewable.
3. **Treat the gap lane as information, not failure.** An unstaffed lane keeps
   the work it could not staff and names the reason, so the owner can decide to
   drop it, staff it, or accept partial delivery.
4. **Confirmation is a durable write.** Confirming sends exactly one apply and
   performs one durable write; the surface must not claim a lane exists before
   that write, and must say what the write produced afterwards.
5. **Judge delivery by the returned result, not by the conversation.** A reply
   or a message is not a completed lane. Until gap 5 closes, treat the
   conversation as the request channel and the Goal's own state as the truth.
6. **Correct in the conversation the work came from.** Steering an active run is
   supported today; correcting a confirmed lane commitment is not yet, so avoid
   confirming a plan whose lanes may need to be withdrawn.

## Reproduce

```sh
# development surfaces
LOOPX_PERSONAL_WORKSPACE_SCENARIO=steward-journey \
  node examples/personal-workspace-browser-smoke.mjs

# packaged workspace bundle
LOOPX_PERSONAL_WORKSPACE_PACKAGED=1 \
LOOPX_PERSONAL_WORKSPACE_SCENARIO=steward-journey \
  node examples/personal-workspace-browser-smoke.mjs
```

The run writes `steward-journey-report.json` (beats, gaps, probe evidence) and
per-beat screenshots under `output/playwright/personal-workspace/`, which is
gitignored. No live Goal, Agent, credential or local path is read or captured.

## Recorded Gaps And Owners

| # | Gap | Evidence the scenario recorded | Owner surface |
| --- | --- | --- | --- |
| 1 | No per-lane readiness ladder (registered → bound → launchable → executing) | probe: no lane-readiness element or phrase | steward readiness (roadmap R2 / audit F6) |
| 2 | No lane-level correction (pause or supersede a confirmed commitment) | probe: no lane-correction element; only run steering exists | shared alignment (roadmap R4) |
| 3 | A failed lane does not name its blocker owner and next step | probe: no lane-blocker element or phrase | recovery/continuation (roadmap R3) |
| 4 | Completion is not judged by the lane's returned result | probe: no lane-return element or phrase | return delivery (roadmap R3) |

The confirm result used to be gap 1, recorded as "the only outcome sentence is
the generic applied notice". A confirmed plan now reports which work it
assigned, to whom, and what it left unstaffed and why, so the scenario asserts
that contract instead of treating it as a gap: the result must name every
assigned lane and every unstaffed item with its reason. What it still does not
claim is execution — the surface says the assignment is recorded and points at
the Goal for progress, which is why beat 5 remains gap 1 rather than proven.

The steward prompt row used to be gap 1. The scenario now asserts it instead of
probing it: the row must expose the five shipped labels, clicking `看阻塞` must
post its message as an accepted Turn, and the composer must stay empty. A
regression fails with the missing labels named, so it cannot pass silently.

## What This Case Does Not Claim

- It does not qualify a live steward conversation: the fixture substitutes the
  agent turn, so the model/runtime behind the intake stays untested here.
- It does not qualify Lark audiences or any cloud/remote worker.
- It does not turn a passing smoke into product acceptance for a Goal whose
  plan was confirmed with real consequences.
