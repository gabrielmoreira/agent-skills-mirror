/**
 * Cursor Hook: afterAgentResponse
 * Fires after every agent response. Detects task completion and prompts for archiving.
 *
 * This script reads JSON from stdin (Cursor hook protocol) and outputs JSON to stdout.
 * For stop event, we can only output a followup_message for user confirmation.
 */

const fs = require('fs');
const path = require('path');

// Archive state file location
const ARCHIVE_STATE_FILE = path.join(__dirname, '..', 'archive', '.archive_state.json');
const ARCHIVE_DIR = path.join(__dirname, '..', 'archive');
const AGENTS_FILE = path.join(__dirname, '..', '..', 'AGENTS.md');

// Timeout in seconds after which archive prompt is auto-dismissed
const ARCHIVE_TIMEOUT_SECONDS = 30;

function loadState() {
  try {
    if (fs.existsSync(ARCHIVE_STATE_FILE)) {
      return JSON.parse(fs.readFileSync(ARCHIVE_STATE_FILE, 'utf8'));
    }
  } catch (e) {
    // ignore
  }
  return { lastPrompt: null, lastTaskId: null };
}

function saveState(state) {
  try {
    if (!fs.existsSync(ARCHIVE_DIR)) {
      fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
    }
    fs.writeFileSync(ARCHIVE_STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  } catch (e) {
    // ignore
  }
}

/**
 * Detect if the agent just completed a meaningful task.
 * Heuristics:
 *   - Agent used Write/StrReplace/Shell tools (made changes)
 *   - Agent output mentions "done", "completed", "finished", "创建", "完成", "修改" etc.
 *   - Agent used multiple tools in sequence (multi-step task)
 */
function detectTaskCompletion(input) {
  const { toolsUsed = [], agentMessage = '', toolResults = [] } = input;

  // No tools used = just a conversation, skip
  if (toolsUsed.length === 0) return false;

  // Check if any tool made changes
  const writeTools = ['Write', 'StrReplace', 'EditNotebook', 'WriteNoReturn'];
  const madeChanges = writeTools.some(t => toolsUsed.includes(t)) ||
                      toolResults.some(r => r && (r.diff || r.modified));

  // Check if output looks like a completion
  const completionKeywords = [
    '已完成', '已完成所有', '任务完成', '完成', 'done',
    'finished', 'completed', 'all done',
    '创建完成', '修改完成', '修复完成', '生成完成',
    '已创建', '已修改', '已修复', '已生成',
  ];

  const outputLower = agentMessage.toLowerCase();
  const isComplete = completionKeywords.some(kw => outputLower.includes(kw.toLowerCase()));

  // Consider it a task if: made changes OR (multiple tools used AND looks complete)
  const multiStep = toolsUsed.length >= 2;
  return madeChanges || (multiStep && isComplete);
}

/**
 * Archive: copy current AGENTS.md to .cursor/archive/ with timestamp
 */
function doArchive() {
  try {
    if (!fs.existsSync(AGENTS_FILE)) {
      console.error('[archive-hook] AGENTS.md not found');
      return;
    }
    if (!fs.existsSync(ARCHIVE_DIR)) {
      fs.mkdirSync(ARCHIVE_DIR, { recursive: true });
    }

    const now = new Date();
    const ts = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const agentId = Math.random().toString(36).slice(2, 8);
    const archiveName = `AGENTS_${ts}_${agentId}.md`;
    const destPath = path.join(ARCHIVE_DIR, archiveName);

    fs.copyFileSync(AGENTS_FILE, destPath);

    // Update archive log
    const logFile = path.join(ARCHIVE_DIR, 'archive_log.json');
    let log = [];
    try {
      if (fs.existsSync(logFile)) {
        log = JSON.parse(fs.readFileSync(logFile, 'utf8'));
      }
    } catch (e) {}

    log.push({
      archivedAt: now.toISOString(),
      file: archiveName,
      source: 'AGENTS.md',
    });

    // Keep only last 50 entries
    if (log.length > 50) log = log.slice(-50);
    fs.writeFileSync(logFile, JSON.stringify(log, null, 2), 'utf8');

    console.log(`[archive-hook] Archived to ${archiveName}`);
  } catch (e) {
    console.error('[archive-hook] Archive failed:', e.message);
  }
}

// Main: read stdin JSON
let rawInput = '';
process.stdin.on('data', chunk => { rawInput += chunk; });
process.stdin.on('end', () => {
  let input = {};
  try {
    if (rawInput.trim()) {
      input = JSON.parse(rawInput);
    }
  } catch (e) {
    console.error('[archive-hook] Failed to parse input:', e.message);
  }

  // Check for explicit archive trigger in user message
  const userMessage = (input.userMessage || '').toLowerCase();
  const archiveTriggers = ['归档', 'archive', '迭代', 'iterate', '更新规则'];
  const shouldArchive = archiveTriggers.some(t => userMessage.includes(t));

  if (shouldArchive) {
    doArchive();
    console.log(JSON.stringify({
      followup_message: '已归档 AGENTS.md。正在触发自动迭代（检查现有规则文件、代码结构和开发约定）...',
    }));
    return;
  }

  // Detect task completion for auto-prompt
  const state = loadState();
  const sessionId = input.sessionId || 'unknown';

  // Avoid re-prompting in the same session
  if (state.lastTaskId === sessionId) {
    console.log(JSON.stringify({}));
    return;
  }

  if (detectTaskCompletion(input)) {
    // Mark this session as prompted
    state.lastTaskId = sessionId;
    state.lastPrompt = new Date().toISOString();
    saveState(state);

    console.log(JSON.stringify({
      followup_message: '本次任务已完成。是否需要归档本次开发上下文到 AGENTS.md？请回复"归档"以触发自动迭代，或忽略此提示（' + ARCHIVE_TIMEOUT_SECONDS + '秒后自动跳过）。',
    }));
    return;
  }

  // No action
  console.log(JSON.stringify({}));
});
