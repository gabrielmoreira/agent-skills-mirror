# Troubleshooting

Common issues and solutions for the obsidian-to-x skill.

## Chrome debug port not ready

**Prevention (REQUIRED)**: Always clean Chrome CDP processes BEFORE executing any script:

```bash
pkill -f "Chrome.*remote-debugging-port"; pkill -f "Chromium.*remote-debugging-port"; sleep 2
```

**Important**: This should be done automatically as the first step of every workflow — do not ask the user, just do it.

If a script still fails with `Chrome debug port not ready` or `Unable to connect` after cleaning, wait 5 seconds and retry once.

## macOS Accessibility Permission Error

**Symptom**: `osascript` fails with error 1002: "System Events encountered an error: osascript is not allowed to send keystrokes"

**Cause**: Terminal app lacks Accessibility permissions, preventing automated paste operations for image uploads.

**Fix**:
1. Open System Settings → Privacy & Security → Accessibility
2. Find your terminal app (Terminal.app, iTerm2, etc.)
3. Enable the toggle to grant permission
4. Restart the terminal and retry

**Note**: The `check-paste-permissions.ts` script may show permissions as granted, but actual execution can still fail if permissions were recently changed. Always verify in System Settings if errors persist.

## Post-Composition Check Failures

The script automatically verifies after all images are inserted:
- Remaining `XIMGPH_` placeholders in editor content
- Expected vs actual image count

If the check fails (warnings in output), alert the user with the specific issues before they publish.

## 脚本重复执行（Agent 后台任务导致）

**症状**: 发布脚本被执行两次，Chrome 被启动两次，文章内容重复填入。

**根本原因**: 使用了 Agent 工具的 `run_in_background=true` 模式。该模式的输出文件写入 `/private/tmp/`，被 vault 权限钩子拦截，导致 `TaskOutput` 报错 `No task found`。Agent 误判任务失败，随后用 Bash `&` 重新执行，造成两个进程并发。

**修复**: 发布脚本一律使用 Bash 后台进程，日志重定向到 vault 内：

```bash
bun ${SKILL_DIR}/scripts/x-article.ts "file.md" > .temp/x-article-output.log 2>&1 &
```

然后用 `sleep N && cat .temp/x-article-output.log | tail -30` 轮询进度。

**禁止**: 不要对发布脚本使用 `Agent run_in_background=true`。

---

## Code Blocks Not Inserting

**Feature**: The script automatically extracts code blocks from Markdown and inserts them into X Articles editor using CDP automation.

**How it works**:
1. Markdown parser extracts code blocks with language and content
2. Code blocks are replaced with placeholders (`XCODEPH_1`, `XCODEPH_2`, etc.) in HTML
3. After content and images are inserted, code blocks are inserted at placeholder positions
4. Uses CDP `Input.insertText` and `Input.dispatchKeyEvent` for reliable insertion

**Supported languages**: Any language supported by X Articles code editor (JavaScript, Python, TypeScript, Rust, Go, Shell, etc.)

**Technical details**:
- Implementation: `scripts/insert-code-blocks.ts`
- Deletion method: `execCommand('delete')` for reliable placeholder removal
- Insertion flow: Select placeholder → Delete → Open code dialog → Select language → Insert code
- Total time: ~2-3 seconds per code block

**No manual action required** - code blocks are automatically detected and inserted during article composition.
