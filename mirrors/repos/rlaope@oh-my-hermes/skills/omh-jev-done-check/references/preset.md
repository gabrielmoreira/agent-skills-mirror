# `done_check/v1`

OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). The tool
returns Jev's raw answers and, separately, `policy_result` with `computed_by: omh_preset`: the
answers are Jev's and the outcome is OMH's fixed rule. Thresholds: editorial_not_measured.

## What `state` carries, and what leaves the machine

`state` is an object with `claim`, `evidence_excerpt`, `goal`: one completion claim, an excerpt of test or command output, and the goal. All of it is sent to the route's
host with the question text. OMH adds nothing else.

## Questions

| id | shape |
| --- | --- |
| `evidence_relation` | choice: `supports`, `contradicts`, `says_nothing` |
| `addresses_stated_goal` | noul |

## Outcomes

`objection_contradicted`, `objection_unsupported`, `objection_off_goal`, `no_objection`, `not_observed`. A non-answer is `not_observed` with `rule: not_answered:<status>`, so it never
reads as Jev's answer. No outcome approves, passes, merges, or declares work done.

The model is pinned to the version the thresholds were written against (`jev-1.13.0`, or
`jev-1.13` on the OpenRouter route).
