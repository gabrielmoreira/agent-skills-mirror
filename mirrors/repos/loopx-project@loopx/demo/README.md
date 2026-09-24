# LoopX Demo Workspace

> **DEMO — NOT an official product capability.**
>
> Everything under `demo/` is an exploratory prototype / showcase, not part of
> the shipped LoopX product. It is **not** installed with the LoopX wheel, not
> registered in the product capability catalog, and not exposed through the
> product CLI.

This directory holds self-contained demos that are kept runnable from the repo
checkout for reference and experimentation:

- `auto_research/` — the auto-research worker/supervisor showcase (kernels,
  worker loop, evidence packets, terminal-result query, demo end-to-end).
- `multi_agent/` — the companion multi-agent launcher showcase (contract,
  round ledger, role successor, visible launch policy, wake scheduler).
- `visible_multi_agent_launcher.py` / `visible_multi_agent_tmux.py` — the
  tmux-based visible multi-agent launcher used by the demo.

The demos depend on the real LoopX product modules (`loopx.quota`,
`loopx.todos`, `loopx.status`, …) and are run by importing the `demo` package
from the repo root (examples and smokes already add the repo root to
`sys.path`).

These were relocated from the product capability surface
(`loopx/capabilities/auto_research` and `loopx/control_plane/agents/multi_agent`)
to make the demo/non-product boundary explicit. If a piece here matures into a
stable caller contract, it should be promoted back into
`loopx/capabilities/<capability>/` with a real entrypoint and focused
validation.
