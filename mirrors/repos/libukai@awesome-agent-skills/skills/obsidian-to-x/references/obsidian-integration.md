# Obsidian Integration

This document explains how to automatically detect and publish the currently active file in Obsidian.

## Get Active File

### Method 1: workspace.json (Primary, 39x faster)

Parse `.obsidian/workspace.json` to get the most recently opened file:

```bash
# Fast and reliable (0.007s)
ACTIVE_FILE=$(jq -r '.lastOpenFiles[0]' .obsidian/workspace.json)
```

**Advantages:**
- ⚡ 39x faster than CLI (0.007s vs 0.274s)
- ✅ Works even when Obsidian is not running
- ✅ No user interaction required

**Requirements:**
- `jq` tool installed: `brew install jq` (macOS) or `apt install jq` (Linux)

---

### Method 2: Obsidian CLI (Fallback)

Use [Obsidian CLI](https://help.obsidian.md/cli) `recents` command:

```bash
# Slower but official (0.274s)
ACTIVE_FILE=$(obsidian recents 2>&1 | grep -v "Loading\|installer" | head -1)
```

**Advantages:**
- ✅ Official Obsidian interface
- ✅ Always up-to-date with Obsidian's state

**Requirements:**
- Obsidian 1.12+ installer
- CLI enabled in Settings → General → Command line interface
- Obsidian app must be running

## Simplified Workflow for "Publish Current Article"

When the user says "publish current article" or "post this to X":

**Step 1: Get active file path**
```bash
ACTIVE_FILE=$(obsidian file active)

# Fallback: if CLI fails, use workspace.json
if [ -z "$ACTIVE_FILE" ] || [ ! -f "$ACTIVE_FILE" ]; then
    ACTIVE_FILE=$(jq -r '.lastOpenFiles[0]' .obsidian/workspace.json)
fi

# Validate file exists
if [ -z "$ACTIVE_FILE" ] || [ ! -f "$ACTIVE_FILE" ]; then
    echo "❌ Error: Could not determine active file"
    exit 1
fi

echo "📄 Active file: $ACTIVE_FILE"
```

**Step 2: Clean Chrome CDP processes**
```bash
pkill -f "Chrome.*remote-debugging-port"; pkill -f "Chromium.*remote-debugging-port"; sleep 2
```

**Step 3: Publish (x-article.ts handles Obsidian conversion internally)**
```bash
# Publish to X (Obsidian syntax converted automatically)
bun ${SKILL_DIR}/scripts/x-article.ts "$ACTIVE_FILE"
```

**One-command shortcut:**
```bash
# Use the publish-active.sh script
bash ${SKILL_DIR}/scripts/publish-active.sh
```

## Error Handling

**If workspace.json parsing fails:**
- Ensure `jq` is installed: `brew install jq` (macOS) or `apt install jq` (Linux)
- Check if `.obsidian/workspace.json` exists
- Fallback to Obsidian CLI automatically

**If Obsidian CLI fallback fails:**
- Error: "No active file" → Open a file in Obsidian first
- Error: "Obsidian CLI not found" → Enable CLI in Settings → General → Command line interface
- Warning: "installer is out of date" → Download latest installer from https://obsidian.md/download (still works, just a warning)
