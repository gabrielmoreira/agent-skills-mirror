---
name: error-messaging-and-empty-states
description: Ensure user-facing errors and empty states are clear, actionable, and HIG-aligned. Covers alerts, ContentUnavailableView, retry flows, and permission guidance.
---

# Error Messaging & Empty States

Design and audit user-visible errors and empty states so they are clear, actionable, and respectful of user intent.

## When to use this skill

- When adding new flows with failure modes
- Before App Store submission
- After user reports confusion or churn
- When adding sync, network, or permission features

---

## Core Principles (HIG-aligned)

- Be specific: explain what failed
- Offer a next action: retry, adjust, learn more
- Avoid blame: no “you did X wrong”
- Keep it short and human

---

## Step 1: Inventory User-Facing Errors

Search for alerts and error views:

```bash
rg --type swift -g '!*Tests*' '\.alert\(' YourApp/Views/
rg --type swift -g '!*Tests*' 'ContentUnavailableView' YourApp/Views/
```

Check:
- Title + message are both present
- Primary action is clear
- Secondary action cancels or dismisses

---

## Step 2: Empty State Coverage

Empty states should explain:
1) Why it’s empty
2) What the user can do next

Examples:
- “No patterns yet” + “Create your first pattern” button
- “Nothing synced” + “Open on iPhone to sync”

---

## Step 3: Permissions & Settings Errors

If a permission is denied:
- Explain why it’s needed
- Offer a path to Settings

Checklist:
- Only request permissions on user action
- Provide a Settings CTA after denial

---

## Step 4: Network & Sync Failures

- Use retry actions for transient failures
- Surface offline state explicitly
- Avoid repeated blocking alerts

---

## Step 5: Error Copy Style Guide

- Short, human, and actionable
- Avoid technical jargon
- Use the user’s language (localized)

---

## Output Format

| Category | Issues | Status |
|----------|--------|--------|
| Alerts reviewed | X | ✅/❌ |
| Empty states present | X | ✅/❌ |
| Permission guidance | X | ✅/❌ |
| Retry paths | X | ✅/❌ |
| Localized error copy | X | ✅/❌ |
