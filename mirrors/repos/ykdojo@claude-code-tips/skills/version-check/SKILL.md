---
name: version-check
description: Recommend which Claude Code version to run, or whether to update. Use when asked which Claude Code version is best/safe, whether to update now, whether a recent release is buggy, or what changed since the installed version.
---

# Claude Code version check

The goal is a recommendation: stay put, update, or pin to a specific version. Claude Code ships `latest` very frequently (often 1-2x/day), so "best version" is a moving target and the answer is usually a *range*, not a single build.

## Heuristics (read first)

- **`stable` lags `latest` and is NOT an LTS.** The npm `stable` dist-tag is just a pointer that trails `latest` by a handful of patch releases. It can even sit *behind* an important fix release, so "stable" does not mean "most bugs fixed." Don't blindly recommend `@stable`.
- **Quiet version = good sign.** If nobody is complaining about a recent release, that's a positive signal. A loud pile-on about a specific build is the thing to avoid.
- **Version comparisons are the strongest signal.** Posts where people compare builds ("X broke Y, rolled back to Z") tell you exactly which release to avoid.
- **Stay ~a day behind the bleeding edge.** Avoid a release that's only a few hours old - let others surface same-day regressions first.
- **The real lever is *when* you update, not stable-vs-latest.** Default Claude Code auto-updates to `latest` constantly, which is how you drift onto a same-day regression.

## 1. What's installed vs what's published

```bash
claude --version
npm view @anthropic-ai/claude-code dist-tags --json
```

`dist-tags` shows `latest`, `stable`, and `next`. Compare against the installed version to see how far ahead/behind each pointer is.

Recent releases and their timestamps (to see how fast things are shipping):

```bash
npm view @anthropic-ai/claude-code time --json | python3 -c "import sys,json;d=json.load(sys.stdin);print('\n'.join(f'{k}: {v}' for k,v in list(d.items())[-8:]))"
```

## 2. Scan the changelog for regressions in the gap

Fetch the changelog and read the entries *between* the installed version and `latest`. Look for "Fixed ... regression in X" lines - if a recent build introduced a regression that has not yet been fixed, that's the one to avoid.

```bash
curl -sL https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | awk '/## <LATEST>/,/## <INSTALLED>/'
```

(Substitute the two version numbers.) A release that is mostly "Fixed …" after a noisy one is usually a safe landing spot.

## 3. Community sentiment (optional but valuable)

Check r/ClaudeAI for recent posts about version stability and comparisons. **Reddit returns HTTP 403 to curl (including from datacenter IPs), so use Playwright** - navigate to the search `.json` URL and `JSON.parse(document.body.innerText)`. See the `reddit-fetch` skill for the full pattern.

```
https://www.reddit.com/r/ClaudeAI/search.json?q=claude+code+update+broke+OR+regression&restrict_sr=on&sort=top&t=month&limit=25
```

Apply the heuristics above: a positive or quiet recent-update thread is reassuring; a high-score "X is broken" thread names the build to skip.

## 4. Recommend

- If the installed version is in the recent, well-received range and nothing in the gap regressed: **stay put**, don't chase a release that's only hours old.
- If there's a known regression in a build, recommend the last good version and `npm install -g @anthropic-ai/claude-code@X.Y.Z` to pin/rollback.
- For anyone who's been burned: **disable the auto-updater and update deliberately** (the repo's setup script does this), rather than religiously tracking `@stable`.
