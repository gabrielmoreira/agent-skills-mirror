---
name: android-performance
description: "Captures Android performance evidence on an adb target: Simpleperf CPU samples, Perfetto/Compose traces, gfxinfo framestats, dumpsys meminfo, Java heap dumps, and native heapprofd allocations. Use when profiling a focused Android app flow, diagnosing jank or startup stalls, ranking CPU hotspots, or gathering leak artifacts. Not for unfocused soak captures, installing/driving the UI, or treating empty Simpleperf output on a non-profileable build as proof."
version: 1.0.1
---

# Android Performance

Capture and interpret Android performance evidence for adb-installable apps. CPU sampling usually requires a debuggable or profileable build; frame stats, Perfetto, and logcat can still help when an app cannot be sampled. Compose with `../android-emulator-qa/SKILL.md` for device selection, build/install/launch, UI driving, screenshots, UI trees, and logcat capture.

## When to Use

Use this skill when any of the following come up:

- "Profile this Android app flow" or "what functions are taking CPU time?"
- Diagnosing jank, missed frames, slow startup, or main-thread stalls
- Capturing frame timing or scheduler/binder/lock evidence
- Comparing before/after performance of a code change
- Gathering memory snapshots, Java heap dumps, or native allocation traces
- Explaining what code is taking time during a user-visible flow

Do **not** use for broad "use the app for a while" captures — they make traces hard to attribute and hide the functions that matter. Always pick one focused user-visible flow.

## Prerequisites

- A local adb target (device or emulator) with the app installed and reachable via `adb -s <serial>`.
- For Simpleperf CPU sampling: the installed package must be **debuggable** or **profileable from shell**. Frame stats, Perfetto, and logcat work regardless.
- `ARTIFACT_DIR` — a run-specific output folder **outside** the skill directory. The skill folder is for bundled instructions and scripts, not run artifacts.
- Optional: Shark CLI for Java heap dump analysis; `trace_processor_shell` for Perfetto native allocation analysis.
- Windows host is primary (PowerShell). When running bash snippets on Windows, use Git Bash, WSL, or an equivalent bash shell. Keep Windows path notes in mind when constructing `SKILL_DIR` paths.

## Procedure

### 0. Set up artifact directory

```bash
if [ -z "${ARTIFACT_DIR:-}" ]; then
  ARTIFACT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-android-perf.XXXXXX")"
fi
mkdir -p "$ARTIFACT_DIR"
```

> **HARD RULE:** Do not put `ARTIFACT_DIR` under `SKILL_DIR`. The skill folder is for bundled instructions and scripts only.

### 1. Choose a trace type

| Question | Trace type |
|---|---|
| What functions are taking CPU time? | **Simpleperf** |
| Frame timing, startup timeline, scheduler gaps, binder, locks, main-thread stalls, Compose recomposition, jank | **Perfetto** |
| Quick manual frame/jank snapshot | **gfxinfo framestats** (pair with Perfetto for root cause) |
| Retained Java/Kotlin objects, PSS, native heap, object counts | **meminfo / heap dumps** |

### 2. Simpleperf CPU Profiles

#### 2a. Preflight — verify debuggable/profileable

```bash
SERIAL="<adb-serial>"
PACKAGE="<app package>"

adb -s "$SERIAL" shell dumpsys package "$PACKAGE" | grep -Ei 'DEBUGGABLE|profileable|isProfileable' || true
```

If the package is not debuggable/profileable and `simpleperf record --app` fails, install a debug/profileable build when possible. If that is not possible, use Perfetto or `gfxinfo` instead of treating missing CPU samples as evidence.

#### 2b. Start recording

```bash
MAX_DURATION_SECONDS=60

adb -s "$SERIAL" shell rm -f /data/local/tmp/perf.data
adb -s "$SERIAL" logcat -c

adb -s "$SERIAL" shell simpleperf record \
  --app "$PACKAGE" \
  -o /data/local/tmp/perf.data \
  -e cpu-clock -f 4000 -g \
  --duration "$MAX_DURATION_SECONDS"
```

While that command is running, perform exactly one focused flow with adb input, UI automation, or `android-emulator-qa`.

#### 2c. Stop recording

```bash
adb -s "$SERIAL" shell 'pid="$(pidof simpleperf 2>/dev/null || true)"; [ -n "$pid" ] && kill -INT $pid'
```

If that returns `Operation not permitted`, send Ctrl-C to the original `adb shell simpleperf record` command session and wait for it to exit.

#### 2d. Pull and report

```bash
adb -s "$SERIAL" pull /data/local/tmp/perf.data "$ARTIFACT_DIR/perf.data"
adb -s "$SERIAL" logcat -d > "$ARTIFACT_DIR/logcat.txt"

SKILL_DIR="<absolute path to this loaded skill folder>"
FIRST_PARTY_REGEX="$(printf '%s' "$PACKAGE" | sed 's/\./\\./g')"
"$SKILL_DIR/scripts/simpleperf_hotspots.sh" \
  "$ARTIFACT_DIR/perf.data" \
  "$ARTIFACT_DIR" \
  --serial "$SERIAL" \
  --first-party-regex "$FIRST_PARTY_REGEX"
```

> **HARD RULE:** Do not derive `SKILL_DIR` from the target app repo's `pwd`; installed plugins usually live outside the app being profiled.

> **HARD RULE:** Keep `FIRST_PARTY_REGEX` scoped to the app's package or app-owned module prefixes. Avoid broad framework patterns such as `kotlin`, `Compose`, or `androidx.compose` when reporting app-owned rows.

The helper writes:

- `$ARTIFACT_DIR/simpleperf-self.txt`
- `$ARTIFACT_DIR/simpleperf-children.txt`
- `$ARTIFACT_DIR/simpleperf.csv` when supported by the installed Simpleperf

If host Simpleperf is not installed, the helper searches Android Studio and Android SDK/NDK locations. If unavailable, it falls back to device-side `adb shell simpleperf report` when the device still has `/data/local/tmp/perf.data`.

#### 2e. Reading Simpleperf reports

Simpleperf reports **sampled CPU execution**. It does not directly measure suspended coroutines, network latency, lock wait time, or other wall-clock waits. If a flow feels slow but Simpleperf shows little app CPU, capture Perfetto.

- **Self/Overhead**: samples where the function itself was executing. Use for hot leaf work — parsing, formatting, diffing, sorting, allocation-heavy iteration, JSON/protobuf processing.
- **Children/inclusive**: samples in the function and its callees. Use for expensive entry points — repositories, use cases, view models, Composables, startup initializers, feature coordinators.
- **Shared Object / Symbol**: prefer app-owned package frames, feature modules, domain/data/UI modules, and generated app code. Treat Android framework, Kotlin runtime, Compose, and native/runtime frames as context unless the app-owned caller is visible.
- **Percentages**: useful for ranking functions inside one capture. For user-facing timing claims, pair with Perfetto, `gfxinfo`, or repeated wall-clock measurements.

When interpreting a hotspot, note: symbol/function name, self or inclusive percentage, approximate sampled CPU time when available, caller stack or owning source file, flow steps, artifact paths, and whether the capture is single-run or repeated.

### 3. Perfetto / Compose Trace

If the app repo already documents a Perfetto/System Trace command for that project, use it. Otherwise use the light command below. It captures scheduler/frequency/Android atrace categories and app `Trace` sections for `PACKAGE`; it is **not** a substitute for a full project-specific Perfetto config when you need detailed frame timeline or Compose runtime internals.

#### 3a. Start Perfetto

```bash
TRACE_DURATION_SECONDS=30
TRACE_BASENAME="app-flow-$(date +%Y%m%d-%H%M%S).pftrace"
TRACE_DEVICE="/data/misc/perfetto-traces/$TRACE_BASENAME"

PERFETTO_PID="$(adb -s "$SERIAL" shell perfetto \
  --background-wait \
  -o "$TRACE_DEVICE" \
  -t "${TRACE_DURATION_SECONDS}s" \
  --app "$PACKAGE" \
  sched freq idle am wm gfx view binder_driver hal dalvik | tr -d '\r' | tail -n 1)"
printf 'Perfetto PID: %s\n' "$PERFETTO_PID"
```

Run exactly one focused flow before `TRACE_DURATION_SECONDS` expires.

#### 3b. Stop early (optional)

Prefer letting `TRACE_DURATION_SECONDS` expire instead of stopping early. To stop early:

```bash
adb -s "$SERIAL" shell kill -TERM "$PERFETTO_PID" 2>/dev/null || true
adb -s "$SERIAL" shell "
  last_size=-1
  stable_count=0
  i=0
  while [ \$i -lt 30 ]; do
    size=\$(ls -l '$TRACE_DEVICE' 2>/dev/null | awk '{ print \$5 }')
    if [ -n \"\$size\" ] && [ \"\$size\" -gt 0 ] && [ \"\$size\" = \"\$last_size\" ]; then
      stable_count=\$((stable_count + 1))
      [ \$stable_count -ge 2 ] && exit 0
    else
      stable_count=0
    fi
    last_size=\"\${size:-0}\"
    i=\$((i + 1))
    sleep 1
  done
  exit 1
"
```

If the stop command fails because the trace already ended, still wait until the output file exists and its size is stable before pulling.

#### 3c. Pull the trace

```bash
adb -s "$SERIAL" pull "$TRACE_DEVICE" "$ARTIFACT_DIR/$TRACE_BASENAME"
```

#### 3d. Inspect in Perfetto

Load `references/` for Perfetto query examples when available. In Perfetto UI or `trace_processor_shell`, inspect:

- Main-thread slices around missed frames or long startup sections
- Frame scheduling, frame timeline, and render thread lanes
- Compose runtime tracing sections for recomposition work when enabled
- Binder transactions, monitor contention, scheduler gaps, and app log markers

> Only report frame timeline or Compose recomposition details when those tracks/events are actually present in the captured trace. The light command above does not guarantee them.

### 4. gfxinfo Framestats

Use for a quick manual frame/jank snapshot:

```bash
adb -s "$SERIAL" shell pidof "$PACKAGE"
adb -s "$SERIAL" shell dumpsys window | grep -F "$PACKAGE"
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" reset
# Perform the focused flow.
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" > "$ARTIFACT_DIR/gfxinfo.txt"
adb -s "$SERIAL" shell dumpsys gfxinfo "$PACKAGE" framestats > "$ARTIFACT_DIR/gfxinfo-framestats.txt"
```

Capture from a stable, responsive screen. If `dumpsys gfxinfo` fails to dump the process, or the device shows an ANR/dialog/splash screen instead of the flow, discard that capture and use Perfetto for root cause.

Read the headline summary first: total frames, janky frames, frame percentiles, slow UI thread, slow draw commands, and frame deadline misses. On emulators, absolute smoothness numbers are noisy; percentile spikes and slow draw/UI counters are still useful for deciding whether to take a Perfetto trace.

### 5. Memory / Leak Artifacts

Use on an adb target after narrowing the investigation to one flow. Exercise the flow, return to a stable screen, then capture memory artifacts from that state.

#### 5a. meminfo snapshot

```bash
adb -s "$SERIAL" shell am force-stop "$PACKAGE"
adb -s "$SERIAL" shell monkey -p "$PACKAGE" 1
# Exercise the focused flow, then navigate back to a stable idle screen.
adb -s "$SERIAL" shell dumpsys meminfo "$PACKAGE" > "$ARTIFACT_DIR/meminfo-flow.txt"
```

Read `TOTAL PSS`, Java heap, native heap, graphics, `Views`, `Activities`, binder counts, and object counts. Treat one noisy sample as a lead, not a conclusion.

#### 5b. Java heap dump (Shark CLI)

For retained Kotlin/Java objects, prefer Shark CLI when available. It works with Android heap dumps and produces text output the agent can inspect and cite.

```bash
HEAP="/data/local/tmp/app-flow.hprof"
HPROF="$ARTIFACT_DIR/app-flow.hprof"

if ! command -v shark-cli >/dev/null; then
  echo "Install Shark CLI, or analyze the HPROF with Android Studio Profiler / MAT." >&2
fi

adb -s "$SERIAL" shell am dumpheap -g "$PACKAGE" "$HEAP"
adb -s "$SERIAL" pull "$HEAP" "$HPROF"
adb -s "$SERIAL" shell rm -f "$HEAP"

if command -v shark-cli >/dev/null; then
  shark-cli --hprof "$HPROF" analyze | tee "$ARTIFACT_DIR/shark-analysis.txt"
fi
```

Read `shark-analysis.txt` first when it exists. Report suspected leaking objects, retained sizes, and reference chains. Look for retained feature objects, activities, fragments, view models, Compose state holders, repositories, listeners, callbacks, and caches that should have been released after leaving the flow. If Shark CLI is unavailable, still preserve the HPROF path and inspect it with the best available heap analyzer; do not claim leak roots from `meminfo` alone.

#### 5c. Native allocation traces (heapprofd)

For native allocation growth, capture a Perfetto trace with heapprofd enabled.

> **HARD RULE:** Current Android `perfetto` rejects `-t` together with `--config`. Keep the duration in the config.

```bash
TRACE_DEVICE="/data/misc/perfetto-traces/native-alloc.pftrace"

adb -s "$SERIAL" shell perfetto -o "$TRACE_DEVICE" \
  --txt -c - <<EOF
duration_ms: 60000
buffers { size_kb: 262144 fill_policy: RING_BUFFER }
data_sources {
  config {
    name: "android.heapprofd"
    heapprofd_config {
      sampling_interval_bytes: 65536
      shmem_size_bytes: 8388608
      block_client: true
      process_cmdline: "$PACKAGE"
    }
  }
}
EOF

adb -s "$SERIAL" pull "$TRACE_DEVICE" "$ARTIFACT_DIR/native-alloc.pftrace"
```

Analyze with the bundled helper:

```bash
SKILL_DIR="<absolute path to this loaded skill folder>"
"$SKILL_DIR/scripts/heapprofd_reports.sh" \
  "$ARTIFACT_DIR/native-alloc.pftrace" \
  "$ARTIFACT_DIR"
```

The helper writes: `heapprofd-summary.txt`, `heapprofd-top-allocations.txt`, `heapprofd-top-stack.txt`, `heapprofd-health.txt`.

Read those outputs together with `meminfo`. Report net native allocation size, top allocating frames/mappings, the expanded stack for the largest callsite, and whether trace stats show heapprofd health issues such as client errors, packet loss, or buffer overruns. Prefer Java heap dumps for retained app objects; heapprofd is for native allocation behavior.

### 6. Report

Report:

- Exact flow, device/emulator, Android version, build variant, and run count
- Artifact paths for every trace/report used
- Top hotspots or frame/jank evidence with percentages, durations, or counts
- Whether evidence is CPU samples, frame timeline, frame stats, or memory artifacts
- Caveats such as emulator noise, low sample count, cold-start compilation, or missing symbols
- Next smallest trace or code change when current evidence is insufficient

## Pitfalls

- **Broad captures**: "Use the app for a while" traces are hard to attribute and hide the functions that matter. Always pick one focused flow.
- **Non-debuggable apps**: `simpleperf record --app` fails on non-debuggable/non-profileable builds. Do not treat missing CPU samples as evidence — switch to Perfetto or gfxinfo.
- **Simpleperf ≠ wall-clock**: Simpleperf does not measure suspended coroutines, network latency, lock wait, or wall-clock waits. Low app CPU + slow flow → use Perfetto.
- **ARTIFACT_DIR under SKILL_DIR**: Never store run artifacts in the skill folder. The skill folder is for bundled instructions and scripts only.
- **SKILL_DIR from app repo pwd**: Do not derive `SKILL_DIR` from the target app repo's `pwd`. Installed plugins usually live outside the app being profiled.
- **Broad first-party regex**: Do not use `kotlin`, `Compose`, or `androidx.compose` as first-party patterns — these are framework/runtime frames, not app-owned.
- **Perfetto `-t` with `--config`**: Current Android `perfetto` rejects combining `-t` with `--config`. Keep duration in the config text.
- **Stopping Perfetto early**: Prefer letting `TRACE_DURATION_SECONDS` expire. If stopping early fails because the trace already ended, still wait for the output file to exist and stabilize before pulling.
- **gfxinfo on wrong screen**: If `dumpsys gfxinfo` fails to dump the process, or the device shows an ANR/dialog/splash, discard the capture and use Perfetto.
- **Emulator frame noise**: Absolute smoothness numbers on emulators are noisy. Use percentile spikes and slow draw/UI counters as signals, not conclusions.
- **Single meminfo sample**: One noisy `meminfo` sample is a lead, not a conclusion. Do not claim leak roots from `meminfo` alone — use a heap dump.
- **Reporting Compose tracks not present**: Only report frame timeline or Compose recomposition details when those tracks/events are actually present in the captured trace. The light Perfetto command does not guarantee them.

## Verification

After each capture, verify the artifacts exist and are non-empty before interpreting:

```bash
# Simpleperf
ls -la "$ARTIFACT_DIR/perf.data" "$ARTIFACT_DIR/simpleperf-self.txt" "$ARTIFACT_DIR/simpleperf-children.txt"

# Perfetto
ls -la "$ARTIFACT_DIR"/*.pftrace

# gfxinfo
ls -la "$ARTIFACT_DIR/gfxinfo.txt" "$ARTIFACT_DIR/gfxinfo-framestats.txt"

# meminfo
ls -la "$ARTIFACT_DIR/meminfo-flow.txt"

# Heap dump
ls -la "$ARTIFACT_DIR/app-flow.hprof" "$ARTIFACT_DIR/shark-analysis.txt" 2>/dev/null || true

# Native alloc
ls -la "$ARTIFACT_DIR/native-alloc.pftrace" "$ARTIFACT_DIR/heapprofd-summary.txt" 2>/dev/null || true
```

Verify the device/app state before capturing:

```bash
adb -s "$SERIAL" shell pidof "$PACKAGE"   # app is running
adb -s "$SERIAL" shell dumpsys window | grep -F "$PACKAGE"   # app window is visible
```

Verify Simpleperf produced samples (not an empty profile):

```bash
adb -s "$SERIAL" shell simpleperf report -i /data/local/tmp/perf.data --header-only 2>&1 | head -5
```

Verify Perfetto trace is valid and non-trivial in size before pulling:

```bash
adb -s "$SERIAL" shell ls -l "$TRACE_DEVICE"
```

## Related skills

- `../android-emulator-qa/SKILL.md` — device selection, build/install/launch, UI driving, screenshots, UI trees, logcat capture. Compose with this skill for the full record-and-analyze loop.
