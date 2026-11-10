---
tags: [ux-brainstorm]
max_turns: 80
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

brief and direction are locked in, build me the variants to choose from.

Ticket inbox for Helpdeck (web support tool)
- who: support agents, all day, 40-120 tickets per shift, keyboard-heavy
- job: pick the next ticket that matters and answer it. primary action is replying
- content: subject (up to 120 chars), customer name + plan, channel (email/chat), wait time, priority, assignee, last message preview
- states: default (~60 open tickets), empty (inbox zero), error (failed to load)
- constraints: desktop web, 1280px and up, no design system yet, WCAG AA
- taste: likes Linear and Superhuman, dislikes Zendesk's dense toolbars
- out of scope: editing ticket details, admin settings, reports

direction: "Keyboard-first list". one dense list with the conversation preview beside it, actions on shortcuts, chrome kept to icons. refs: Linear's issue list, Superhuman's inbox, Front's shared inbox
