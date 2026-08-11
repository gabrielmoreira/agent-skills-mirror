---
name: teamshare-cli
description: "Use when the user wants to interact with Teamshare capabilities, especially Teamshare Base multi-dimensional tables: files, directories, sheets, fields, records, views, forms, dashboards, or dashboard widgets. Load this skill first to route to the right Teamshare sub-skill. Also trigger for localized requests in the user's language that refer to Teamshare or Teamshare Base."
---

# Teamshare CLI Skill Index

This skill is a directory entry for Teamshare capabilities. The concrete Teamshare skills are pre-installed at `~/.agents/skills/` by `teamshare-cli install`.

## Prerequisite: Load teamshare-shared First

Before any Teamshare operation, load `teamshare-shared` first. It covers login, platform configuration, credential status, and common auth recovery.

```text
read_skills(skill_names=["teamshare-shared"])
```

## Sub-skill Directory

Load only the sub-skill needed for the current task.

| User intent | Load skill |
|-------------|------------|
| Login, logout, check credential status, inspect current API base URL, or recover config/auth errors | `teamshare-shared` |
| Operate Teamshare Base multi-dimensional tables: files, directories, sheets, fields, records, views, forms, dashboards, and widgets | `teamshare-base` |

## Load Examples

```text
read_skills(skill_names=["teamshare-shared"])
read_skills(skill_names=["teamshare-shared", "teamshare-base"])
```

## Authentication

Use the Teamshare shared skill for the exact login flow. The normal CLI sequence is:

```bash
teamshare-cli auth status
teamshare-cli auth login --env cn-saas
teamshare-cli auth login
teamshare-cli auth status
```

Use `cn-saas` or `International` unless the user explicitly gives a different environment. Do not ask the user for credential contents, and do not print or store tokens.

## When Unsure About a Command

Always check `--help` before guessing parameters.

```bash
teamshare-cli --help
teamshare-cli auth --help
teamshare-cli config --help
teamshare-cli base --help
teamshare-cli base <command> --help
```
