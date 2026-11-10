---
tags: [ux-brainstorm]
max_turns: 120
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, Agent]
---

ok we're done with questions for shiftly's settings (app in demo-app/). these are final:

1. settings split into sections: General, Locations, Scheduling, Time clock, Notifications, Billing
2. owners see everything, managers everything except Billing, staff only their own Notifications
3. each section saves on its own, and leaving with unsaved changes asks first
4. a workspace has up to 40 locations. deleting one asks to confirm, then offers Undo
5. "swaps need approval" only shows when shift swaps are on
6. desktop first, but it has to work on a phone during a shift

prototype two things for me to pick from: how you get around settings, and the locations list

Input files: demo-app/package.json, demo-app/components.json, demo-app/src/index.css, demo-app/src/lib/settings.ts, demo-app/src/lib/utils.ts, demo-app/src/components/ui/button.tsx, demo-app/src/components/ui/card.tsx, demo-app/src/components/ui/switch.tsx, demo-app/src/pages/Settings.tsx
