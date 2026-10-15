# Short Drama Creator Workspace Design

## Status

- **Status:** Active
- **Last refreshed:** 2026-08-06
- **Primary surface:** `$short-drama dashboard`
- **Audience:** writers, directors, and independent short-drama creators

## Product principle

Creators work on one page:

```text
项目标题与状态
内容目录 | 当前正文
待办提示与导出提示
```

The product has one page and one always-visible reading area. It does not provide tabs,
pop-up document viewers, an advanced mode,
engineering mode, raw-file view, lifecycle panel, or technical report entry.
Runtime records and integrity evidence remain system-owned and have no product
navigation.

## Goals

- Answer within ten seconds: which project, which episode, current work, next action.
- Organize work by project, episode, scene, character, and shot instead of files.
- Let creators read and edit story content without understanding its storage format.
- Keep save semantics explicit: saving persists the current Markdown and does not launch production.
- Explain problems in terms of audience or production impact.
- Export production materials by purpose.

## Single-page information architecture

```text
短剧创作台
├── 当前项目与一句状态说明
├── 内容目录
│   ├── 全剧
│   └── EP001
│       ├── 故事与剧本
│       ├── 人物场景
│       ├── 分镜画面
│       └── 生成文案
├── 当前正文（始终可见，打开项目后自动载入）
└── 待办提示 / 导出提示
```

The interface never uses a filesystem tree as navigation. Markdown, structured
records, images, and video are rendered as creator-facing documents, cards, or
media previews in the permanent reading area. Selecting another item replaces that
area in place; it never opens a modal or another page.

### Creator-facing progress

Infer progress from the five visible documents and media, without a separate lifecycle file:

- 未开始
- 创作中
- 提示词就绪
- 已有媒体

The page shows only a compact plain-language reminder. Production confirmation and export
requests are handed back to the conversation; the Dashboard must not imitate an action it
cannot complete.

## Interaction rules

### Save

- Save persists the current edit.
- The interface shows saved, saving, unsaved, and conflict states in plain language.
- Save does not confirm or launch external production.

### Revise or continue

- The creator reads and edits the current document in place.
- Requests to revise, continue, review, export, or produce return to the conversation.
- A future action API may shorten this loop, but it must not create a second source of truth.

### Problems

Problem cards contain:

1. the scene or shot;
2. the audience or production impact;
3. the intended result;
4. a direct action.

Do not display internal severity names, reviewer identities, storage paths, or protocol
states.

## Visual language

- A calm director's worktable, not an administration dashboard.
- Graphite background with warm paper-like content surfaces.
- Amber marks the current action; red is reserved for required fixes; green is reserved
  for creator-confirmed or export-ready content.
- System sans-serif for controls and a readable local serif stack for screenplay content.
- Use the content rail and paper-like reading area as the defining visual motif.
- Avoid metric-card walls, decorative gradients, and code-editor styling.

## Accessibility and responsive behavior

- Native buttons, labels, headings, and live status regions.
- Visible keyboard focus and Cmd/Ctrl+S support.
- No state depends on color alone.
- Desktop uses a compact content rail plus one permanent content canvas.
- Narrow layouts stack navigation and content with 44px touch targets.
- Honor `prefers-reduced-motion`.

## Creator-visible files

The target public handoff is:

```text
项目/
├── 原始资料/
├── 剧集/
│   └── EP001/
│       ├── 剧本.md
│       ├── 视觉设定.md
│       ├── 分镜.md
│       ├── 图片提示词.md
│       └── 视频提示词.md
├── 审查/
│   └── EP001-审查.md
└── 导出/
```

The Dashboard classifies the five Chinese document names into story, cast, storyboard,
and prompt groups, opens `剧本.md` first, and derives episode progress from visible files.

## Implementation constraints

- Python standard-library server and vanilla HTML/CSS/JS; no new dependency.
- Loopback-only session, Host/Origin validation, path containment, symlink refusal,
  atomic save, and concurrent-edit protection remain mandatory.
- Never inject project HTML into the DOM.
- The browser submits creator actions and content identifiers; it does not submit hashes,
  manifests, or arbitrary output paths.
- Every server action needs unit and HTTP coverage.
- Every visual change needs desktop and narrow-layout inspection.

## Delivery sequence

1. Replace the file console with the single creator workspace.
2. Add creator-safe revise, review, production-preview, and export actions.
3. Introduce logical content identifiers independent of storage paths.
4. Keep the five Markdown files as the only creator-facing episode truth.
