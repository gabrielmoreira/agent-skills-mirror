---
tags: [pr-babysit]
max_turns: 150
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

keep an eye on PR 9 and let me know when CI finishes. don't push anything to it though, I'm still working on that branch locally (repo/)

(sandbox note: GitHub is simulated here; put this sandbox's gh first on PATH with `export PATH="$PWD/bin:$PATH"` from the sandbox root before any gh command)

Input files: repo/, remote.git/, bin/gh
