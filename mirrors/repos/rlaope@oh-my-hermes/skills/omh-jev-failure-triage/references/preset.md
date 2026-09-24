# `failure_triage/v1`

OMH owns this question set and its rule ladder (`src/plugin_bundle/omh/jev_presets.py`). The tool
returns Jev's raw answers and, separately, `policy_result` with `computed_by: omh_preset`: the
answers are Jev's and the outcome is OMH's fixed rule. Thresholds: editorial_not_measured.

## What `state` carries, and what leaves the machine

`state` is an object with `error_excerpt`, `last_command`, `earlier_attempts`: the failing command and an excerpt of its error output, plus earlier attempt excerpts when given. All of it is sent to the route's
host with the question text. OMH adds nothing else.

## Questions

| id | shape |
| --- | --- |
| `transient` | noul |
| `missing_dependency` | noul |
| `auth_or_permission` | noul |
| `repeats_without_progress` | noul |

## Outcomes

`ask_user_for_access`, `change_approach`, `retry_once_suggested`, `fix_environment`, `no_signal`, `not_observed`. A non-answer is `not_observed` with `rule: not_answered:<status>`, so it never
reads as Jev's answer. No outcome approves, passes, merges, or declares work done.

The model is pinned to the version the thresholds were written against (`jev-1.13.0`, or
`jev-1.13` on the OpenRouter route).
