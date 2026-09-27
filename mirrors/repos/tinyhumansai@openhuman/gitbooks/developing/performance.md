# Performance and footprint

OpenHuman's Rust core runs in-process as a library, not as one OS process per
agent. That single decision is where most of the density numbers on this page
come from: a fixed bootstrap cost (allocator warm-up, code paging, registries,
detectors) is paid once per process and then shared across however many agents
run inside it, instead of being paid again for every agent.

Everything below was measured on Apple Silicon macOS, `--release` build,
against a deterministic mock inference provider (the `rss-bench` feature),
not real network calls. Treat the absolute numbers as this-machine numbers and
the ratios (density, marginal cost, binary delta) as the parts worth
generalizing. The scripts to reproduce them are listed at the end.

## Fleet: how many agents fit in one process

`library-fleet.sh` runs N concurrent live agents in a single process, with
latency-realistic mock inference (200 ms) so idle time behaves like a real
network wait instead of a busy loop. It reports the *marginal* RSS per
additional agent once the fixed base is paid, which is the number that
actually decides how many agents fit in a box.

| N agents | Marginal KiB/agent | Settled MiB | Idle CPU ms/10s | Threads | FDs |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 1,985 | 223 | 3 | 71 | 420 |
| 100 | 1,866 | 356 | 3 | 123 | 820 |
| 500 | 1,770 | 1,393 | 3 | 211 | 3,220 |

500 agents in one process, measured, at roughly 1.77 MiB marginal cost each.
Idle CPU stays flat regardless of N, which is the property that matters: an
agent that isn't mid-turn should not be spending cycles. Thread count grows
about 0.35 per agent, which is the one line item worth watching before pushing
past 500 in production.

Thousands of agents on a single box is the direction this is heading, not a
number we've hit yet. The trend across 50/100/500 agents is a settling
marginal cost, not a rising one, which is what makes that direction plausible.

## In-process vs one process per agent

The same benchmark suite includes `library-instances.sh`, which spawns N
independent `library-profile` processes instead of N agents inside one
process. That measured about 47.8-48.2 MiB per instance, flat across N =
10/25/50, which puts roughly 42 instances in a 2 GiB box by summed RSS (an
upper bound; macOS has no PSS-equivalent metric to divide out shared pages).

One process per agent pays the ~30-50 MiB fixed base every time. The
in-process model pays it once. At the measured marginal cost, the one-process
fleet model is roughly 25 times denser than the per-process model for the same
memory budget.

## Cold start

| Scenario | Median settled RSS | Median duration |
| --- | ---: | ---: |
| `agent-turn` (cold, one turn, no delegation) | 47.6 MiB | 102 ms |
| `cold-phases` (nine bootstrap phases: config load, registry init, agent build, memory construction, first turn) | 51.2 MiB | 476 ms |

A cold agent turn answers in about 102 ms. The full nine-phase bootstrap, the
thing a process pays exactly once, takes 476 ms. After that, a warmed turn in
the same process costs 0.5-1.9 MiB rather than the 26-31 MiB a first turn
retains, because most of a cold turn's cost is executable code paging in for
the first time, not per-turn allocation.

## Slim build footprint

A `--no-default-features --features rss-bench` build (drops every optional
domain) settles at about 15.2 MiB of private physical memory and roughly 42
MiB RSS. The rest of that RSS is reclaimable executable text and allocator
high-water retention, not live data: a deep attribution pass found about 3.2
MiB of live heap and 18.7 MiB of resident executable text inside that 42 MiB.

## Binary size by feature set

Cargo feature gates control what compiles in. Two starting points matter:
Contrib (`[features] default` in `crates/openhuman-core/Cargo.toml`, what a
bare `cargo check` builds) and Product (`scripts/ci/product-features.txt`,
what the desktop app ships).

| Build | Features | Unstripped | Stripped |
| --- | --- | ---: | ---: |
| Default (all gates) | Contrib/Product superset | 115.9 MiB | n/a |
| library-minimal | `skills,flows` | ~81.1 MiB | ~60.4 MiB |
| Pure slim | none | 68.4 MiB | 51.0 MiB |

The `skills,flows` recipe in
[`docs/library-minimal-recipe.md`](../../docs/library-minimal-recipe.md) is
the supported embed target for a headless host: it keeps SKILL.md execution
and saved-workflow runs, drops voice, web3, media, meet, MCP and the desktop
automation stack, and lands about 30% smaller than the default build. Most of
that gain is binary size and code-paging surface; it only moves settled RSS by
about 3-5 MiB per scenario, since most of the RSS story is initialization and
allocator behavior rather than linked code size.

Do not describe this as a "15 MB binary." The smallest number on this page is
15.2 MiB of private memory in a slim, running process; the smallest binary is
51 MiB stripped with nothing enabled.

## Feature gates and loadable modules

Everything above compiles in at build time through Cargo features (`media`,
`skills`, `flows`, `mcp`, `channels`, `http-server`, `scheduler-gate`,
`file-logging`, `modules`, and more). Beyond that, several domains ship as
loadable native `cdylib` modules rather than being linked into the core
binary at all: `tinydocs`, `tinyvoice`, `tinyjuice`, `tinyruntime`,
`tinywallet`, `tinymcp`, `tinychannels`, and `tinyconnectors`, each behind a
small `*-bus` contract crate. A module loads into the same process and shares
its privileges, so the admission checks (ABI, manifest, dependency, digest)
matter more than for an ordinary dependency; see `AGENTS.md`'s "Loadable
modules and bus contracts" section for the rules.

## The kernel-floor ratchet

`scripts/kernel-floor.sh` measures the dependency graph of the `flows`
profile (`--no-default-features --features flows`, the surface a second host
would embed) along three numbers: package count, unique crate names, and
native (C/C++) build count. `scripts/kernel-floor.limits` holds the ceiling
for each, currently `flows:306:285:2`, and the ratchet only moves down: a
change that grows the graph has to lower this number in the same PR, and
raising it requires a written justification a reviewer actually reads. This
is what stops the dependency floor silently growing back after each gating
effort sheds crates from it.

## How to reproduce

Every number above comes from the driver scripts under `scripts/profile/`,
built around `crates/openhuman-cli/src/bin/library_profile/main.rs`
(scenario implementations) and the `library-profile` / `rss-bench` binaries.
Benchmarks run from these scripts, not in CI.

```bash
# RSS/duration medians across fresh processes, all scenarios
./scripts/profile/library-bench.sh

# Same, against the slim (--no-default-features) recipe
./scripts/profile/library-bench.sh --slim

# Fleet sweep + the 2 GB / 2 vCPU budget gate
./scripts/profile/library-fleet.sh --agents "50,100,500" --target 1000 --budget-mib 2048

# Many-processes counterpart to the fleet sweep
./scripts/profile/library-instances.sh --instances "10,25,50" --hold-secs 30

# Dependency-floor ratchet
scripts/kernel-floor.sh flows
```

`scripts/profile/README.md` documents the remaining scripts (`library-cpu.sh`
for CPU profiling via samply, `library-heap.sh` for live-heap attribution via
dhat). Full methodology, caveats, and the per-scenario breakdown live in
[`docs/library-benchmarking.md`](../../docs/library-benchmarking.md) and
[`docs/library-minimal-recipe.md`](../../docs/library-minimal-recipe.md).

## Measurement conditions, stated plainly

These numbers were gathered on macOS, which has no cgroup memory limit to
enforce locally and no `/proc/<pid>/smaps_rollup`, so there is no true PSS
(proportional shared memory) reading available. RSS overcounts shared pages
in a way that matters more as agent count grows. The fleet and instances
numbers are a projection from measured marginal cost, not a live "did it
survive an OOM kill at N agents" test on the target 2 GB / 2 vCPU Linux box.
Every scenario also replaces network inference with a deterministic mock
provider at a fixed latency, so turn timings measure orchestration overhead,
not real model latency. Real Linux cgroup validation is documented follow-up
work, not something this page claims already happened.

For token-level cost rather than process footprint, see [Smart Token
Compression](../features/token-compression.md), which is the other half of
"cheap": it controls how much of what the harness assembles actually reaches
the model.
