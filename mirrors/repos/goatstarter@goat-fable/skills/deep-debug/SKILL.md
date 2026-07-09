---
name: deep-debug
description: Structured root-cause debugging protocol. Use when a bug has survived one or two fix attempts, when a failure is described as weird, flaky, or impossible, or when you notice you are guessing instead of diagnosing. Also invoked manually via /deep-debug.
---

# Deep Debug

You are here because normal fixing didn't work. That means something you believe about this system is false. The protocol's one rule: **no code changes until you can state the mechanism of the failure in one sentence.**

## 1. Freeze the evidence

- Write down (scratch file or todo): the exact symptom, verbatim error text, and what has already been tried and failed. Failed attempts are data: each one falsified some hypothesis; extract which.
- Build a minimal reproduction: the smallest command that shows the failure on demand. One test, one curl, one function call. This is later your proof-of-fix.
- No reproduction possible → that's the actual task now. Report what conditions are missing rather than fixing blind.
- Flaky? Run the repro 5-10 times, record the rate. Without a baseline rate you can't distinguish "fixed" from "got lucky".

## 2. Locate by observation, not intuition

- Read the WHOLE error: the second exception, the "caused by", the warning three lines up. Go to the exact file:line it names and read around it.
- Separate the crash *site* from the bug *source*: bad values are usually born elsewhere and explode here. Trace the value backwards.
- Instrument: targeted log lines at the suspected boundary (inputs, branch taken, timing), run the repro, read what actually happened. One instrumented run beats ten minutes of staring.
- Bisect: is the data already wrong at the pipeline's midpoint? Halve again. For regressions, `git bisect` with the repro script.
- Works in A, fails in B: list every difference (data, config, env, order) and eliminate them one at a time.

## 3. Hypothesis loop

State it falsifiably, mechanism included: "session is null because the middleware registers before the cookie parser." Then run the CHEAPEST test that could disprove it: a log line, a controlled input, a reorder in a scratch copy. Not a full fix.

- Confirmed → step 4.
- Falsified → good, a branch is closed. Log it in the scratch list so you don't re-try it in 20 minutes. Next hypothesis.
- Can't state a mechanism → you're still in step 2; gather more evidence.

Anti-tunneling: the same approach failing twice means change strategy, not variables' names. Three different approaches dead → run the assumption audit, by observation, embarrassing ones first:

1. Is the code I'm editing the code that's actually running? (build output, deployed copy, right service, right branch)
2. Is my change loaded? (restart, cache, memoized module)
3. Is the input what I assume? (log it)
4. Is the version what I assume? (lockfile, `--version`)
5. Does the test even reach my code? (plant a deliberate crash; if the test still passes, it never got there)
6. Does the doc I'm trusting match this installed version?

## 4. Fix, prove, sweep

1. Fix at the layer where the wrong value/order is born, not where it explodes. Never a null-check/try-except/retry/fallback whose only justification is "the symptom goes away".
2. Re-run the step-1 reproduction and watch it pass (flaky: as many runs as the failing baseline).
3. Run surrounding tests for collateral damage.
4. Grep for siblings of the same mistake; report them even if out of scope.
5. Report: mechanism, fix, proof, siblings. If instead you're stuck after the audit: report the repro, hypotheses eliminated, and evidence gathered. That report is a deliverable; a cosmetic fix is not.
