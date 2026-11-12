---
tags: [resolve-merge-conflicts]
max_turns: 80
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

github says PR #42 has conflicts with main and can't be merged. can you sort it out? my checkout is in repo/

(sandbox note: GitHub is simulated here; put this sandbox's gh first on PATH with `export PATH="$PWD/bin:$PATH"` from the sandbox root before any gh command)

Input files: repo/, remote.git/, bin/gh
