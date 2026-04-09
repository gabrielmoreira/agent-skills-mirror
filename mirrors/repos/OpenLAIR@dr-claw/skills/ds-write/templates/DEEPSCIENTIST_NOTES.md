# DeepScientist Template Notes

These templates are vendored from `Orchestra-Research/AI-Research-SKILLs/20-ml-paper-writing` so the `write` skill can use them offline inside local quest workspaces.

Selection defaults:

- general ML / AI paper with no stronger venue constraint: start from `iclr2026/`
- targeting ICLR / ICML / NeurIPS / COLM / AAAI: use the matching venue directory directly
- ACL-style NLP / CL paper: use `acl/`
- systems paper: use `asplos2027/`, `nsdi2027/`, `osdi2026/`, or `sosp2026/` as appropriate

Usage rule:

1. Activate the dedicated `paper/*` branch/worktree.
2. Copy the chosen template directory into the active paper workspace's `paper/latex/`.
3. Keep the template's main `.tex` file as the build root unless there is a concrete reason to rename it.
4. Draft the paper inside that `paper/latex/` tree and keep `paper/` for supporting notes, plans, figures, and bundle metadata.

License:

The upstream source is MIT-licensed. See `UPSTREAM_LICENSE.txt`.
