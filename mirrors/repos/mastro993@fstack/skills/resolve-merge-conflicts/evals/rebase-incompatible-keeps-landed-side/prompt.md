---
tags: [resolve-merge-conflicts]
max_turns: 100
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

rebase my bankers-rounding branch onto latest main pls, it conflicts. don't push, I want to look at it before I force push. repo is in repo/

(sandbox note: GitHub is simulated here; put this sandbox's gh first on PATH with `export PATH="$PWD/bin:$PATH"` from the sandbox root before any gh command)

Input files: repo/, remote.git/, bin/gh
