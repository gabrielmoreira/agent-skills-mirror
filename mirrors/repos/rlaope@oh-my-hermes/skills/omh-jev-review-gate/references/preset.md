# `review_flags/v1`

OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). The tool
returns Jev's raw answers and, separately, `policy_result` with `computed_by: omh_preset`: the
answers are Jev's and the outcome is OMH's fixed rule. Thresholds: editorial_not_measured.

## What `state` carries, and what leaves the machine

`state` is an object with `file`, `diff`: one file path and that file's source diff. All of it is sent to the route's
host with the question text. OMH adds nothing else.

## Questions

| id | shape |
| --- | --- |
| `touches_auth_or_permissions` | noul |
| `changes_stored_data_shape` | noul |
| `tests_cover_the_change` | noul |
| `introduces_secret_or_key` | noul |
| `senior_would_block` | noul |
| `severity` | score: 4 levels |

## Outcomes

`flags_raised`, `no_flags`, `not_observed`. A non-answer is `not_observed` with `rule: not_answered:<status>`, so it never
reads as Jev's answer. No outcome approves, passes, merges, or declares work done.

The model is pinned to the version the thresholds were written against (`jev-1.13.0`, or
`jev-1.13` on the OpenRouter route).
