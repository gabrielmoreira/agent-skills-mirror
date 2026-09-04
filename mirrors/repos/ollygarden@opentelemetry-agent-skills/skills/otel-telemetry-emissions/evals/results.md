# `prometheusremotewrite-v0159-metrics` harness results

Run on 2026-09-02 with Claude Code 2.1.258 driving `claude-sonnet-5`. Every repetition used a
fresh session, an isolated `CLAUDE_CONFIG_DIR`, an empty working directory outside this
repository, and the same tool access: `Read`, `Glob` and `Grep` only. No arm had network
access, so no arm could read the upstream source. The prompt, the model and the tool set were
identical in all three arms. Only the target skill changed.

The withheld arm removed `otel-telemetry-emissions` alone. The other 170 skills stayed in
place in every arm.

A deterministic grader marked a repetition passing only when all four expectations in
`evals.json` were present in the final answer. No repetition was retried, and no repetition
was excluded.

| Arm | Target-skill revision / state | Cases × reps | Pass | Fail | Unknown |
|---|---|---:|---:|---:|---:|
| Target skill withheld | `Withheld` | 1 × 3 | 0 | 3 | 0 |
| Current `origin/main` skill | `55e1d7e411b5cddefb3ae95f128b220da8354044` | 1 × 3 | 0 | 3 | 0 |
| Proposed PR skill | `029f34324742a15f49eea0e181947efb83e8ae1c` | 1 × 3 | 3 | 0 | 0 |

## Per-attempt grading

`A` is all 16 metric names, `B` is the `wal` condition with the v0.159.0 `exporter` attribute,
`C` is the Remote Write 2.0 gate and config, and `D` is the instrument types and units.

| Attempt | Names found | A | B | C | D | Result |
|---|---:|---|---|---|---|---|
| `withheld-1` | 2/16 | fail | fail | fail | fail | fail |
| `withheld-2` | 0/16 | fail | fail | fail | fail | fail |
| `withheld-3` | 0/16 | fail | fail | fail | fail | fail |
| `current-1` | 0/16 | fail | fail | fail | fail | fail |
| `current-2` | 0/16 | fail | fail | fail | fail | fail |
| `current-3` | 0/16 | fail | fail | fail | fail | fail |
| `proposed-1` | 16/16 | pass | pass | pass | pass | pass |
| `proposed-2` | 16/16 | pass | pass | pass | pass | pass |
| `proposed-3` | 16/16 | pass | pass | pass | pass | pass |

## What differed

**The withheld arm could not do the task.** `withheld-1` gave two generic exporter metrics,
`otelcol_exporter_sent_metric_points` and `otelcol_exporter_send_failed_metric_points`, which
every exporter emits and which the question did not ask for. It then named only two of the 16
component metrics, with no type, unit or attribute. It inferred from the `wal.lag_record_frequency`
config key that a WAL lag metric must exist, and refused to name it. `withheld-2` and
`withheld-3` gave no answer at all. They asked for permission to fetch the upstream source.

**The `origin/main` arm failed correctly.** `current-1` and `current-2` reported that the
component is not in the registry, and refused to guess. This is the behavior that
`SKILL.md` asks for: "If the component or version is not covered at all, say so — do not infer
telemetry from semantic conventions." So these are not defects in the shipping skill. They are
the shipping skill telling the truth about a coverage gap. `current-3` asked to fetch the
source, like the withheld arm.

**The proposed arm answered completely, three times out of three.** Every repetition named all
16 metrics, separated the four unconditional metrics from the nine WAL metrics and the three
Remote Write 2.0 metrics, gave the instrument type and unit for each, and stated that v0.159.0
adds the `exporter` attribute to the WAL metrics that earlier versions emit unattributed. Two
repetitions also gave the histogram bucket boundaries.

**No regression.** The proposed arm did not lose any behavior that the `origin/main` arm had.
The `origin/main` arm gave no component data to lose. The "say so when not covered" rule stays
in the skill and is unchanged by this PR.

## Failing runs kept, and why

All six failures are preserved. None was retried.

- `withheld-2`, `withheld-3` and `current-3` stopped to ask for network permission instead of
  answering. This is a genuine miss, not a harness failure. The agent had no source and would
  not guess. The exit code was 0 in each.
- `withheld-1`, `current-1` and `current-2` gave an answer that failed all four expectations.

## Limitations

- One case, three repetitions per arm. This is the minimum that `CONTRIBUTING.md` asks for.
- One model and one harness. The result may differ on another model.
- `claude -p` prints the final answer only. The saved output holds no tool calls and no
  reasoning, so a reviewer sees what the agent concluded, not how it got there.
- All 170 other skills were present in every arm. Their descriptions add trigger surface. The
  set was identical across arms, so it cannot explain the difference between them.
- The case tests retrieval of one component at one version. It does not test the accuracy of
  the other 5 versions in this PR, and it does not test any other component.

## Transcripts

The nine final answers hold no credentials, no local paths, no customer data and no private
repository content. They were checked for all four before this summary was written.
