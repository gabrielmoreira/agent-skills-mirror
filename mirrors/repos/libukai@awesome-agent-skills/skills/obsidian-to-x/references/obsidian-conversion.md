# Obsidian Markdown Conversion

This document explains how to convert Obsidian-specific Markdown syntax to standard Markdown for X Articles.

## Problem

Obsidian uses non-standard Markdown syntax that requires conversion before publishing:
- Images: `![[Attachments/image.png]]` instead of `![](path)`
- Annotations: `> [#6178] Title` format in blockquotes
- Frontmatter: Chinese field names like `标题:` instead of `title:`

## Solution: Automatic Conversion

Obsidian syntax conversion is now built into `x-article.ts` via the `md-to-article.ts` module. No separate conversion step is needed -- just pass the Obsidian Markdown file directly:

```bash
# Direct publish (x-article.ts handles Obsidian conversion internally)
${BUN_X} ${SKILL_DIR}/scripts/x-article.ts Articles/your-article.md
```

For standalone conversion (debugging or inspection):

```bash
# Simple conversion (output to system temp)
${BUN_X} ${SKILL_DIR}/scripts/md-to-article.ts Articles/your-article.md

# Custom output path
${BUN_X} ${SKILL_DIR}/scripts/md-to-article.ts Articles/your-article.md /tmp/custom.md
```

## What Gets Converted

1. ✅ **Title**: `标题:` → `title:`
2. ✅ **Images**: `![[Attachments/img.png]]` → `![](absolute/path/img.png)`
3. ✅ **Placeholders**: `![[wechatAccountCard]]` → (removed)
4. ✅ **Annotations**: `> [#6178] Title` → (removed, entire line deleted)
5. ✅ **Callouts**: `> [!question] Title` → (removed, Obsidian callout syntax)
6. ✅ **Cover**: `封面:` → `cover_image:` (with absolute path)
7. ✅ **Code blocks**: Automatically extracted and inserted

## Manual Conversion (Advanced)

If you prefer shell commands:

```bash
# Get current project root (assumes you're in the Obsidian project directory)
PROJECT_ROOT="$(pwd)"
ORIGINAL_FILE="Articles/your-article.md"
CONVERTED_FILE="Temp/converted.md"

# Create Temp directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/Temp"

# Step 1: Convert Obsidian image syntax to standard Markdown with absolute paths
sed "s|!\[\[Attachments/\([^|]*\)\(|[^]]*\)\{0,1\}\]\]|![]($PROJECT_ROOT/Attachments/\1)|g" "$ORIGINAL_FILE" > "$CONVERTED_FILE"

# Step 2: Remove Obsidian-specific placeholders (e.g., wechatAccountCard)
sed -i '' '/!\[\[wechatAccountCard\]\]/d' "$CONVERTED_FILE"

# Step 3: Remove annotation lines with [#number] prefix
sed -i '' '/^> \[#[0-9]*\] /d' "$CONVERTED_FILE"

# Step 4: Add English title field to frontmatter (extract from Chinese field)
TITLE=$(grep "^标题:" "$ORIGINAL_FILE" | sed 's/标题: //')
sed -i '' "2a\\
title: $TITLE
" "$CONVERTED_FILE"

# Step 5: Extract cover image path from frontmatter
COVER=$(grep "^封面:" "$ORIGINAL_FILE" | sed 's/封面: "\[#[0-9]*\] !\[\[\(.*\)\]\]"/\1/' | sed "s|Attachments/|$PROJECT_ROOT/Attachments/|")

# Step 6: Publish (x-article.ts handles Obsidian conversion internally)
${BUN_X} ${SKILL_DIR}/scripts/x-article.ts "$ORIGINAL_FILE" --cover "$COVER"
```

## Simplified Version

For typical use cases:

```bash
# Quick conversion for Obsidian articles
# Assumes you're in the project root directory
PROJECT_ROOT="$(pwd)"
mkdir -p Temp

# Convert and save to Temp directory
sed "s|!\[\[Attachments/\([^|]*\)\(|[^]]*\)\{0,1\}\]\]|![]($PROJECT_ROOT/Attachments/\1)|g" Articles/original.md > Temp/converted.md
sed -i '' '/!\[\[wechatAccountCard\]\]/d' Temp/converted.md
sed -i '' '/^> \[#[0-9]*\] /d' Temp/converted.md
sed -i '' '2a\
title: Your Article Title' Temp/converted.md

${BUN_X} ${SKILL_DIR}/scripts/x-article.ts Articles/original.md --cover Attachments/cover.png
```

## When to Apply

If the user's Markdown file contains `![[]]` syntax or Chinese frontmatter, automatically perform the conversion before calling the publish script.
