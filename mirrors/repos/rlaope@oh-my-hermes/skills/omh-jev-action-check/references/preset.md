# `action_check/v1`

OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). The tool
returns Jev's raw answers and, separately, `policy_result` with `computed_by: omh_preset`: the
answers are Jev's and the outcome is OMH's fixed rule. Thresholds: editorial_not_measured; cuts 0.6, 0.7, 0.7, 0.55 and the rule order adopted from hermes-jev-approvals@530fdb0 jev-approval-rules/1 (MIT; blast 1.5 here, 1.6 there); calibration does not transfer because every question was rewritten.

## What `state` carries, and what leaves the machine

`state` is an object with `command`, `cwd`, `stated_task`: the command or write, the working directory path, and the task the user stated. All of it is sent to the route's
host with the question text. OMH adds nothing else.

## Questions

| id | shape |
| --- | --- |
| `recommendation` | choice: `run_normally`, `hold_for_human`, `refuse` |
| `scope_covers_it` | noul |
| `reads_credentials` | noul |
| `sends_data_off_machine` | noul |
| `text_argues_for_itself` | noul |
| `blast_radius` | score: 3 levels |

## Outcomes

`hold`, `refuse_recommended`, `no_extra_hold`. A non-answer is `hold` with `rule: not_answered:<status>`, so it never
reads as Jev's answer. No outcome approves, passes, merges, or declares work done.

The model is pinned to the version the thresholds were written against (`jev-1.13.0`, or
`jev-1.13` on the OpenRouter route).
