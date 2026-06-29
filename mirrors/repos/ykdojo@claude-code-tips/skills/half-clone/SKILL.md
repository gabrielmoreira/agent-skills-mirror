---
name: half-clone
description: Clone the later half of the current conversation, discarding earlier context to reduce token usage while preserving recent work.
---

Clone the later half of the current conversation, discarding earlier context to reduce token usage while preserving recent work.

Steps:
1. Get the current session ID and project path: `tail -1 ~/.claude/history.jsonl | jq -r '[.sessionId, .project] | @tsv'`
2. Find half-clone-conversation.sh with bash: `find ~/.claude -name "half-clone-conversation.sh" 2>/dev/null | sort -V | tail -1`
   - This finds the script whether installed via plugin or manual symlink
   - Uses version sort to prefer the latest version if multiple exist
3. Preview the conversation to verify the session ID: `<script-path> --preview <session-id> <project-path>`
   - Check that the first and last messages match the current conversation
4. Run the clone: `<script-path> <session-id> <project-path>`
   - Always pass the project path from the history entry, not the current working directory
5. The script prints the new session ID (the `New session: <id>` line). Give the user the exact command to resume it directly, no picker needed:
   ```
   claude --resume <new-session-id>
   ```
   The script automatically appends a reference to the original conversation at the end of the cloned file. (The new session is also marked `[HALF-CLONE <timestamp>]`, e.g. `[HALF-CLONE Jan 7 14:30]`, so `claude -r` and picking it works as a fallback.)
