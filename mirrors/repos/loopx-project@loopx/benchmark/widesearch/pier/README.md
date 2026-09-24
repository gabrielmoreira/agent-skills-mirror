# WideSearch real-sandbox templates (pier)

Reusable, provider-neutral pier wiring for the WideSearch real-sandbox path.
Copy these templates into a local pier dataset root and fill the `<PLACEHOLDER>`
values. Do not commit credentials, local absolute paths, raw runs, or verifier
output. Inject judge secrets only into the separate verifier; keep the model
provider secret in the runner-owned gateway, outside the agent container.

Layout expected by pier (task root):

```text
<task-root>/
  task.toml            <- task.toml.template
  environment/
    Dockerfile         <- environment/Dockerfile.template
  tests/
    Dockerfile         <- tests/Dockerfile.template
    test.sh            <- tests/test.sh.template
    widesearch_evaluator.py
    <gold.csv>
  instruction.md
```

Key wiring facts:

- Workspace and `jobs_dir` must live under `$HOME`: colima does not bind-mount
  macOS `/tmp`, so the verifier's `/logs/verifier` bind mount silently fails
  there and the reward never returns to the host.
- The verifier image must create `/app` (`WORKDIR /app`) because pier copies the
  answer artifact into the verifier container with `docker compose cp`.
- `test.sh` writes `reward.json` with numeric-only values. Pier's
  `VerifierResult` is `dict[str, float | int]`; a string detail field fails the
  trial. Validate before writing with
  `loopx benchmark verify-verifier-reward <reward.json> --require-valid`.
- The agent image must have `/bin/sh` symlinked to bash (`set -o pipefail` is
  used by the pier agent setup; Debian dash does not support it).
- Gold lives only in the verifier image; the agent image never contains it.

Model credentials: countable runs must route the agent image through a
runner-owned local gateway. The real provider credential stays in the gateway
process, outside the agent container; the Codex provider config receives only a
fixed non-secret sentinel. This is the concrete boundary required by
`provider_credential_shell_excluded` in the integrity attestation. Use
`network_access: "permitted_solving"` in the integrity policy for web-research
benchmarks (see `loopx.capabilities.benchmark_toolkit.integrity`).
