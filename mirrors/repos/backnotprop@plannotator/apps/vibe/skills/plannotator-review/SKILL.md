---
name: plannotator-review
disable-model-invocation: true
description: Open Plannotator's browser-based code review UI and address the returned feedback.
---

# Plannotator Review (Mistral Vibe)

Run:

```bash
PLANNOTATOR_ORIGIN=mistral-vibe plannotator review
```

You may append one directory or PR URL:

```bash
PLANNOTATOR_ORIGIN=mistral-vibe plannotator review <pr-url>
PLANNOTATOR_ORIGIN=mistral-vibe plannotator review ../feature-worktree
```

Directory paths are relative to the current session or absolute. Quote paths containing spaces. Feedback names the directory where changes belong.

If the session closes without feedback (the output is "Review session closed without feedback." or empty), acknowledge it in one sentence and stop. Do not begin any work: closing the session is not approval.
