# Field reports: token savings from reference coding (2026-08-11)

**What is recorded here.** Users running the reference-coding loop (clone the
peer repos, `xerj autoindex` them, retrieve before writing) in real product
development report roughly **5× fewer tokens** end-to-end, attributing it to
fewer retry loops on unfamiliar APIs and sharper, better-grounded requests.
Relayed by the project owner on 2026-08-11 from direct user conversations.

**What this is and is not.** This is field testimony, not a controlled run. It
is recorded here so that every public occurrence of the number has a citable
source, per the repository's honest-claims rules. Public copy must always
attribute it as a user report ("users report"), never as a measurement.

**How it relates to what we measured.** The controlled benchmark
(`landing/case-studies/reference-coding.html`; raw data under
`.claude/skills/xerj-code/measure/`) measured, on code the model had not
memorised: 2.7× fewer output tokens task-for-task than grep-driven Claude Code
(26,477 → 9,982), 26× fewer than working from memory alone (260,916 → 9,982),
2.1× cheaper ($3.27 → $1.58), at the same 16/16 solve rate as native tooling.
A real development mix sits between the 2.7× (tooling-assisted) and 26×
(memory-loop) regimes, which is where the ~5× reports fall. The regimes have
different baselines; do not present the bracket as a single like-for-like
measurement.

**Standing rule for reusing the number.** Quote it only as "users report ~5×",
link or cite this file as provenance, and keep a measured number adjacent so
the reader can see both. If future controlled end-to-end runs on real product
work land, replace the testimony with the measurement.
