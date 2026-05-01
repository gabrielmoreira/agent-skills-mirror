---
name: web-adapt
description: Short alias for universal-web-adaptation. Use this when adapting an unfamiliar public website generically before creating any site-specific rules.
license: Proprietary session artifact for local Copilot use
---

# Web adapt skill

This is the short public alias for:

- `universal-web-adaptation`

Also available as simpler aliases:

- `adapt`
- `网站适配`

Use this skill when you want to:

- work with an unfamiliar site generically
- detect search inputs, buttons, popups, and openers
- try multiple navigation/submission strategies
- decide whether a site profile is actually needed

## Primary guidance

1. try generic adaptation first
2. tune runtime if the page is heavy
3. follow popups/new tabs when needed
4. only create a dedicated site profile if the generic path is not robust enough

## Key rules

- Prefer URL verification whenever possible.
- Use container-qualified selectors when duplicates exist.
- Treat opener-search, popup-search, hidden/disabled, login-gated, and rate-limited sites as distinct classes.

## Quick invocation template

You do not need to use only `/web-adapt`.

Reliable invocation patterns include:

1. `/web-adapt`
2. `use the web-adapt skill`
3. a natural-language request that clearly asks for generic website adaptation before any site-specific rules

Use prompts like:

```text
Use /web-adapt to adapt this unfamiliar site first, then tell me whether we should stay generic or create a dedicated site profile.
```

```text
使用 /web-adapt 先通用适配这个网站，并输出是否需要升级成专用 site profile。
```

```text
Please adapt this unfamiliar site generically first and tell me whether a dedicated site profile is actually necessary.
```

## Output contract

The skill output should always include:

1. site classification
2. strategies attempted (in order)
3. evidence of success or failure (URL/title/visible results)
4. final decision: generic vs dedicated profile
5. next recommended action

## Pointer

For the full detailed playbook, also see:

- `skills/universal-web-adaptation/SKILL.md` in this repository
