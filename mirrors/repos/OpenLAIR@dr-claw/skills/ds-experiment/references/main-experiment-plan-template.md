# Main Experiment Plan Template

Use this before substantial code edits or the real main run.
Treat it as the implementation-and-execution plan for the selected idea, not just a metadata form.

## 1. Objective

- run id:
- selected idea in `1-2` sentences:
- user's core requirements:
- non-negotiable user constraints:
- research question:
- null hypothesis:
- alternative hypothesis:

## 2. Baseline And Comparability

- baseline id:
- baseline variant:
- dataset / split:
- primary metric:
- required metric keys:
- comparability risks:

## 3. Code Translation Plan

Map the idea into concrete code changes.

| Path | Current role | Planned change | Why this is needed | Risk |
|---|---|---|---|---|
| | | | | |

## 4. Execution Design

- minimal experiment:
- smoke / pilot plan:
- full run plan:
- expected outputs:
- stop condition:
- abandonment condition:
- strongest alternative hypothesis:

## 5. Runtime Strategy

- command for smoke:
- command for main run:
- expected runtime / budget:
- log / artifact locations:
- safe efficiency levers to use first:
- how existing tooling will be used efficiently:

Monitoring and sleep plan:

- wait cadence:
  - `60s`
  - `120s`
  - `300s`
  - `600s`
  - `1800s`
- health signals that justify continuing to monitor:
- conditions that trigger kill / relaunch:

## 6. Fallbacks And Recovery

- if the intended model / endpoint / download path fails:
- if hardware or memory is tighter than expected:
- if the code path is wrong after smoke:
- if the first full run becomes non-comparable:

## 7. Checklist Link

- checklist path:
- next unchecked item:

## 8. Revision Log

| Time | What changed | Why it changed | Impact on comparability or runtime |
|---|---|---|---|
| | | | |
