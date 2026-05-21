# Show HN Title Formulas

## The Core Formula

```
Show HN: [Name] – [verb phrase describing what it does]
```

The dash is an en dash (–), not a hyphen (-).

Total length: 60-80 characters including "Show HN: ".

## Five Proven Formats

### Format 1: Direct Capability
```
Show HN: [Name] – [verb] + [object] + [context]
```
Examples:
- `Show HN: Datasette – Instantly publish SQLite databases to the web`
- `Show HN: Jitsi – Free, open source video conferencing`
- `Show HN: Pandoc – Universal document format converter`

Best for: tools with a clear, single function

### Format 2: Problem-Solution
```
Show HN: [Name] – [pain point] without [the annoying part]
```
Examples:
- `Show HN: Zulip – Group chat that threads every conversation`
- `Show HN: Coolify – Self-hosted Heroku alternative with no vendor lock-in`

Best for: tools that replace something people already use but dislike

### Format 3: Technical Architecture
```
Show HN: [Name] – [what it is] built with [interesting tech choice]
```
Examples:
- `Show HN: Lite XL – A lightweight text editor written in C and Lua`
- `Show HN: Bun – A fast all-in-one JavaScript runtime built in Zig`

Best for: developer tools where the implementation is the interesting part

### Format 4: Outcome for Specific User
```
Show HN: [Name] – [specific outcome] for [specific person]
```
Examples:
- `Show HN: Fly.io – Deploy app servers close to your users`
- `Show HN: Retool – Build internal tools in minutes`

Best for: B2B tools with a clear target persona

### Format 5: The Experiment Frame
```
Show HN: [Name] – An experiment in [doing X] differently
```
Examples:
- `Show HN: Ink – React for command-line apps`
- `Show HN: Tauri – Electron alternative using system webview`

Best for: projects that challenge a conventional approach

## Character Counting

Count characters in your title before submitting:

```python
title = "Show HN: Datasette – Instantly publish SQLite databases to the web"
print(f"{len(title)} characters")
```

Target: 60-80 characters. Under 60 feels thin. Over 80 gets cut off in some views.

## Words That Add Length Without Value

Remove these from your title:
- "simple", "easy", "fast", "powerful", "lightweight" (unless it is a literal technical spec like "under 5MB")
- "tool", "app", "platform", "solution", "service" (usually redundant)
- "for developers", "for teams" (only include if it narrows the audience usefully)
- "open source" (put it in the body; the title has no room for it)

## En Dash vs Hyphen

Always use an en dash (–) as the separator between name and description.

Copy it: –

Not a hyphen (-) and not an em dash (—).

Most Show HN titles follow this convention. It is a visual signal of the format.
