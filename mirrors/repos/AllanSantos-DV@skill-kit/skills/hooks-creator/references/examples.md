# Hook Examples — Complete Implementations

Ready-to-use hook examples written in JavaScript (Node.js). Each hook is a single `.js` file that works on Windows, macOS, and Linux without platform-specific overrides.

---

## 1. Auto-Format with Prettier (PostToolUse)

Runs `prettier` on any file modified by a file-editing tool.

### JSON Config (`.github/hooks/format.json`)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "node hooks/auto-format.js",
        "timeout": 15
      }
    ]
  }
}
```

### JavaScript (`hooks/auto-format.js`)

```js
#!/usr/bin/env node
// PostToolUse hook: auto-format files after edits
'use strict';
const { execSync } = require('child_process');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let inputJson;
  try { inputJson = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // Only run for file-editing tools
  const tool = inputJson.tool_name;
  if (tool !== 'replace_string_in_file' && tool !== 'create_file' && tool !== 'multi_replace_string_in_file') {
    process.exit(0);
  }

  // Extract file path from tool input
  const file = (inputJson.tool_input && (inputJson.tool_input.filePath || inputJson.tool_input.file_path)) || '';
  if (!file) process.exit(0);

  // Run prettier on the file
  try {
    execSync('npx prettier --write "' + file + '"', { stdio: 'ignore' });
  } catch (_) {
    // prettier not available or failed — silently continue
  }

  process.stdout.write('{}\n');
});
```

### What it does

After every file edit, checks if the tool was a file-editing tool, extracts the file path, and runs `prettier --write` on it. Returns empty JSON on success. Non-matching tools exit immediately with code 0 (no-op).

---

## 2. Project Context Injection (SessionStart)

Injects git branch, last commit, and uncommitted change count into the agent’s context at session start.

### JSON Config (`.github/hooks/session.json`)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "node hooks/session-context.js",
        "timeout": 10
      }
    ]
  }
}
```

### JavaScript (`hooks/session-context.js`)

```js
#!/usr/bin/env node
// SessionStart hook: inject project context (git state) into agent context
'use strict';
const { execSync } = require('child_process');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  // Consume stdin (required) but we don’t need the input for this hook

  let branch = 'unknown';
  let lastCommit = 'none';
  let changes = '0';

  try { branch = execSync('git branch --show-current', { encoding: 'utf8' }).trim(); } catch (_) {}
  try { lastCommit = execSync('git log --oneline -1', { encoding: 'utf8' }).trim(); } catch (_) {}
  try {
    const status = execSync('git status --short', { encoding: 'utf8' });
    changes = String(status.split('\n').filter(l => l.trim()).length);
  } catch (_) {}

  const result = {
    hookSpecificOutput: {
      additionalContext: 'Project context: branch=' + branch + ' | last_commit=' + lastCommit + ' | uncommitted_changes=' + changes
    }
  };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

### What it does

Runs at the start of every session. Gathers git state (current branch, last commit, number of uncommitted changes) and injects it as `additionalContext` so the agent knows the project state without needing to run git commands.

---

## 3. Block Dangerous Commands (PreToolUse)

Prevents the agent from running dangerous terminal commands like `rm -rf`, `DROP TABLE`, `git push --force`.

### JSON Config (`.github/hooks/safety.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "node hooks/block-dangerous.js",
        "timeout": 5
      }
    ]
  }
}
```

### JavaScript (`hooks/block-dangerous.js`)

```js
#!/usr/bin/env node
// PreToolUse hook: block dangerous terminal commands
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let inputJson;
  try { inputJson = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // Only check terminal/command tools
  if (inputJson.tool_name !== 'run_in_terminal' && inputJson.tool_name !== 'Bash') {
    process.exit(0);
  }

  const command = (inputJson.tool_input && inputJson.tool_input.command) || '';

  const dangerousPatterns = [
    /\brm\s+.*-[rR]/,
    /\brm\s+-[fF][rR]/,
    /DROP\s+TABLE/i,
    /DROP\s+DATABASE/i,
    /git\s+push\s+--force(?!-with-lease)/,
    /git\s+reset\s+--hard/,
    /\bmkfs\b/,
    />\s*\/dev\/sda/,
    /:(\)\{\s*:\|:&\s*\};:/
  ];

  for (const pattern of dangerousPatterns) {
    if (pattern.test(command)) {
      const result = {
        hookSpecificOutput: {
          permissionDecision: 'deny',
          permissionDecisionReason: 'BLOCKED: Command matched dangerous pattern. This command was prevented by the safety hook.',
          additionalContext: 'BLOCKED: Command matched dangerous pattern. This command was prevented by the safety hook.'
        }
      };
      process.stdout.write(JSON.stringify(result) + '\n');
      return;
    }
  }

  process.stdout.write('{}\n');
});
```

### What it does

Intercepts every terminal command before execution, checks against a list of dangerous patterns (destructive file ops, database drops, force pushes), and denies execution if a match is found. Non-terminal tools pass through immediately.

---

## 4. Task Completion Reminder (Stop)

Reminds the implementor agent to check its quality checklist before finishing. Based on `hooks/stop-checklist.js`.

### Agent Frontmatter

```yaml
hooks:
  Stop:
    - type: command
      command: "node hooks/stop-checklist.js"
      timeout: 10
```

### JavaScript (`hooks/stop-checklist.js`)

```js
#!/usr/bin/env node
// Stop hook: remind implementor of checklist
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  try {
    const inputJson = JSON.parse(rawInput);
    if (inputJson.stop_hook_active === true) process.exit(0);
  } catch (_) {
    // Empty or invalid JSON — continue to output reminder
  }

  const result = {
    decision: 'block',
    reason: 'Before finishing: 1) Did you run tests? 2) Did you produce a task map (if decisions were made)? 3) Is the quality checklist satisfied?',
    hookSpecificOutput: {
      hookEventName: 'Stop',
      decision: 'block',
      reason: 'Before finishing: 1) Did you run tests? 2) Did you produce a task map (if decisions were made)? 3) Is the quality checklist satisfied?'
    }
  };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

### What it does

Fires when the agent session ends. Outputs `decision: "block"` with a `reason` at **both** top-level and inside `hookSpecificOutput` — this ensures the agent sees the message whether VS Code routes it as Stop or SubagentStop. The `stop_hook_active` guard prevents infinite loops where the hook’s message causes another stop attempt.

---

## 5. Subagent Routing Audit (SubagentStart)

Logs which subagent was invoked and when, useful for debugging orchestration patterns. Based on `hooks/subagent-audit.js`.

### Agent Frontmatter (on orchestrator)

```yaml
hooks:
  SubagentStart:
    - type: command
      command: "node hooks/subagent-audit.js"
      timeout: 5
```

### JavaScript (`hooks/subagent-audit.js`)

```js
#!/usr/bin/env node
// SubagentStart hook: log routing decisions
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let agent = 'unknown';
  try {
    const inputJson = JSON.parse(rawInput);
    if (inputJson.agentName) agent = inputJson.agentName;
  } catch (_) {
    // Empty or invalid JSON — use default agent name
  }

  const now = new Date();
  const ts = now.getFullYear() + '-' +
    String(now.getMonth() + 1).padStart(2, '0') + '-' +
    String(now.getDate()).padStart(2, '0') + ' ' +
    String(now.getHours()).padStart(2, '0') + ':' +
    String(now.getMinutes()).padStart(2, '0') + ':' +
    String(now.getSeconds()).padStart(2, '0');

  // Log to stderr (doesn’t affect hook output)
  process.stderr.write('[' + ts + '] Subagent started: ' + agent + '\n');

  // Return empty success
  process.stdout.write('{}');
});
```

### What it does

Fires whenever the orchestrator spawns a subagent. Logs the agent name and timestamp to stderr (which appears in debug output but doesn’t interfere with the JSON contract). Returns empty JSON to allow the subagent to proceed normally.

---

## 6. Output Format Enforcement (Stop)

Reminds research/validation agents to follow their required output format. Based on `hooks/output-format.js`.

### Agent Frontmatter (on researcher/validator)

```yaml
hooks:
  Stop:
    - type: command
      command: "node hooks/output-format.js"
      timeout: 10
```

### JavaScript (`hooks/output-format.js`)

```js
#!/usr/bin/env node
// Stop hook for researcher/validator: remind output format
'use strict';

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  try {
    const inputJson = JSON.parse(rawInput);
    if (inputJson.stop_hook_active === true) process.exit(0);
  } catch (_) {
    // Empty or invalid JSON — continue to output reminder
  }

  const result = {
    decision: 'block',
    reason: 'Verify your output follows the required format: Research Summary (researcher) or Validation Report (validator) with all mandatory sections.',
    hookSpecificOutput: {
      hookEventName: 'Stop',
      decision: 'block',
      reason: 'Verify your output follows the required format: Research Summary (researcher) or Validation Report (validator) with all mandatory sections.'
    }
  };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

### What it does

Fires when a researcher or validator session ends. Injects a block decision reminding the agent to verify the output follows the structured format (Research Summary or Validation Report). Guards against infinite loops with the `stop_hook_active` check.

---

## 7. Context Injection via Lessons (PreToolUse)

Injects relevant lessons learned into the agent context based on keyword matching. Based on `hooks/lesson-injector.js`.

### JSON Config (`.github/hooks/lessons.json`)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "node hooks/lesson-injector.js",
        "timeout": 5
      }
    ]
  }
}
```

### JavaScript (`hooks/lesson-injector.js`) — abbreviated

```js
#!/usr/bin/env node
// PreToolUse hook: inject relevant lessons learned into agent context
'use strict';
const fs = require('fs');
const path = require('path');
const os = require('os');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let hookInput;
  try { hookInput = JSON.parse(rawInput); } catch (_) { process.exit(0); }

  // Extract user prompt from various possible locations
  let userPrompt = hookInput.chatMessage || hookInput.user_message || hookInput.prompt;
  if (!userPrompt && hookInput.data) {
    userPrompt = hookInput.data.chatMessage || hookInput.data.user_message || hookInput.data.message;
  }
  if (!userPrompt) process.exit(0);

  const promptLower = userPrompt.toLowerCase();

  // Keyword → tag mapping
  const tagMap = {
    'create': ['new', 'add', 'create'],
    'modify': ['update', 'edit', 'modify', 'refactor'],
    'fix': ['fix', 'bug', 'error'],
    'hooks': ['hook', 'hooks'],
    'git': ['git', 'commit', 'push', 'branch']
  };

  const matchedTags = new Set();
  for (const [tag, keywords] of Object.entries(tagMap)) {
    for (const kw of keywords) {
      if (new RegExp('\\b' + kw + '\\b').test(promptLower)) {
        matchedTags.add(tag);
        break;
      }
    }
  }
  if (matchedTags.size === 0) process.exit(0);

  // Find and filter lessons by tag intersection
  const lessonsDir = path.join(os.homedir(), '.copilot', 'lessons');
  if (!fs.existsSync(lessonsDir)) process.exit(0);

  // ... read lesson files, parse frontmatter, match tags, sort by confidence ...

  const result = { decision: 'add', content: 'Relevant lessons: ...' };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

### What it does

Reads the user’s prompt, matches keywords to lesson tags, finds matching lesson files in `~/.copilot/lessons/`, and injects a summary of the most relevant lessons into the agent’s context. Uses only Node.js built-ins (`fs`, `path`, `os`).

---

## 8. Transcript-Aware Skill Feedback (Stop)

Only reminds about skill feedback when skills with Feedback Protocol were actually used. Based on `hooks/skill-feedback.js`.

### JSON Config

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "node hooks/skill-feedback.js",
        "timeout": 5
      }
    ]
  }
}
```

### JavaScript (`hooks/skill-feedback.js`) — abbreviated

```js
#!/usr/bin/env node
// Stop hook: capture skill feedback when skills with Feedback Protocol were used
'use strict';
const fs = require('fs');

let rawInput = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { rawInput += chunk; });
process.stdin.on('end', () => {
  let hookInput;
  try { hookInput = JSON.parse(rawInput); } catch (_) { process.exit(0); }
  if (hookInput.stop_hook_active === true) process.exit(0);

  const transcriptPath = hookInput.transcript_path;
  if (!transcriptPath || !fs.existsSync(transcriptPath)) process.exit(0);

  let lines;
  try { lines = fs.readFileSync(transcriptPath, 'utf8').split('\n'); } catch (_) { process.exit(0); }
  if (!lines || lines.length < 5) process.exit(0);

  // Scope to current interaction: find last user.message
  let startIdx = 0;
  for (let i = lines.length - 1; i >= 0; i--) {
    if (lines[i].includes('"user.message"')) { startIdx = i; break; }
  }

  // Find SKILL.md reads that contain "Feedback Protocol"
  const feedbackSkills = [];
  for (let i = startIdx; i < lines.length; i++) {
    const line = lines[i];
    if (!line.includes('"tool.execution_start"')) continue;
    let evt;
    try { evt = JSON.parse(line); } catch (_) { continue; }
    if (evt.data && evt.data.toolName === 'read_file') {
      const fp = evt.data.arguments && evt.data.arguments.filePath;
      if (fp && /[\\/]skills[\\/]/.test(fp) && /SKILL\.md$/.test(fp)) {
        if (fs.existsSync(fp)) {
          const content = fs.readFileSync(fp, 'utf8');
          if (/Feedback Protocol/.test(content)) {
            const m = fp.match(/[\\/]skills[\\/]([^\\/]+)[\\/]SKILL\.md/);
            if (m) feedbackSkills.push(m[1]);
          }
        }
      }
    }
  }

  if (feedbackSkills.length === 0) process.exit(0);

  const message = 'SKILL FEEDBACK CHECK: Skills with Feedback Protocol were used:\n' +
    feedbackSkills.map(s => '  - ' + s).join('\n');

  const result = {
    decision: 'block',
    reason: message,
    hookSpecificOutput: { hookEventName: 'Stop', decision: 'block', reason: message }
  };
  process.stdout.write(JSON.stringify(result) + '\n');
});
```

### What it does

Analyzes the session transcript to find which SKILL.md files were read via `read_file` tool calls. For each skill, checks if it contains a "Feedback Protocol" section. Only blocks the agent with a feedback reminder when relevant skills were actually used — avoids noisy reminders in sessions that didn’t use any skills with feedback.
