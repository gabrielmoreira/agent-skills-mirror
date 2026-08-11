---
name: lark-cli
description: "Use when the user wants to interact with Lark/Feishu in any way — including but not limited to: reading, querying, searching, sending, replying to, forwarding, or downloading Lark/Feishu IM messages and chat history; managing group chats; listing, viewing, searching, creating, or editing cloud docs/files, Drive, Markdown, spreadsheets, Base tables, wiki, whiteboards, slides, apps, calendars/events/meeting rooms, contacts/org structure, tasks/todos, approvals, attendance, mail, minutes, VC notes, OKRs, real-time events, or custom Lark CLI skills. Load this skill first to find the right sub-skill."
---

# Lark Skill Index

This skill is a directory. Find the sub-skill that matches the user's intent, load it with `read_skills`, then proceed.
All sub-skills are pre-installed at `~/.agents/skills/`.

---

## Prerequisite: Load lark-shared First

Before any Lark operation, load `lark-shared` first — it covers CLI initialization, identity switching (user/bot), scope management, and common error handling.

```
read_skills(skill_names=["lark-shared"])
```

---

## Sub-skill Directory

Load the skill that matches the user's request. Only load what you need for the current task.

| User intent | Load skill |
|-------------|-----------|
| Develop or deploy HTML apps and web pages | `lark-apps` |
| Wrap Lark API operations into a reusable custom Skill (atomic API wrapper or multi-step workflow) | `lark-skill-maker` |
| Send/receive messages, list P2P or group-chat messages, search chat history across chats, manage groups, upload/download chat files, batch get messages, list thread messages | `lark-im` |
| View/create/update events, manage attendees, check availability, book meeting rooms | `lark-calendar` |
| Query org structure, search employees, get user details | `lark-contact` |
| Create/edit Lark docs, search cloud drive documents | `lark-doc` |
| Manage cloud drive files/folders, upload/download, permissions, comments, rename files | `lark-drive` |
| Create/fetch/overwrite Drive-native Markdown files | `lark-markdown` |
| Create and operate spreadsheets, read/write cells, append rows, export | `lark-sheets` |
| Operate Base (multi-dimensional tables): create tables, manage fields, read/write records, views, workflows | `lark-base` |
| Create and manage presentations (slides) | `lark-slides` |
| Query and edit whiteboards, export whiteboard images | `lark-whiteboard` |
| Manage wiki spaces, space members, document node hierarchy | `lark-wiki` |
| Create todos, view/update task status, manage task lists | `lark-task` |
| Approval instance and approval task management | `lark-approval` |
| Query attendance and punch-in records | `lark-attendance` |
| Send/receive mail, manage drafts, folders, labels, contacts, mail rules | `lark-mail` |
| Query Minutes list, get Minutes info and AI artifacts (summary/todos/chapters) | `lark-minutes` |
| Query VC meeting records, get meeting note artifacts | `lark-vc` |
| Manage OKR objectives, key results, alignments, indicators, and progresses | `lark-okr` |
| Subscribe to real-time Lark events (messages, contact changes, calendar changes, etc.) | `lark-event` |
| Above skills insufficient; need to call native Lark OpenAPI directly | `lark-openapi-explorer` |
| Summarize meeting notes over a time range into a structured report | `lark-workflow-meeting-summary` |
| Generate daily/weekly agenda and unfinished task summary (standup/daily report) | `lark-workflow-standup-report` |

---

## Load Examples

```
read_skills(skill_names=["lark-shared", "lark-im"])
read_skills(skill_names=["lark-shared", "lark-calendar"])
read_skills(skill_names=["lark-shared", "lark-base"])
```

---

## When Unsure About a Command

For any lark-cli subcommand, if parameters or usage are unclear, run it with `--help` — do not guess.

```bash
lark-cli --help
lark-cli <command> --help
lark-cli <command> <subcommand> --help
```

Examples:

```bash
lark-cli im --help
lark-cli calendar events --help
lark-cli base record --help
```
