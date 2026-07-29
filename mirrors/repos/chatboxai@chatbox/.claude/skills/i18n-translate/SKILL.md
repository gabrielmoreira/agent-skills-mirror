---
name: i18n-translate
description: 翻译 Chatbox Pro 当前未提交改动、暂存改动或用户指定 commit/range 中新增或受影响的 i18n key。当用户要求翻译、补全与改动 UI 文案相关的翻译时使用。Agent 需要阅读 diff 和组件上下文，遵守 skill 内置 glossary，并直接写 locale JSON；脚本只用于最后校验。
metadata:
  short-description: 翻译 Chatbox 改动中的 i18n key
---

# i18n-translate

你一名UI翻译者。请你读 diff、读源码上下文、判断哪些 i18n key 需要补译，然后直接编辑 `src/renderer/i18n/locales/*/translation.json`。注意不要运行 `pnpm translate`，也不要依赖抽取脚本来决定翻译内容。你(LLM)来检查哪些 key 需要翻译，并且直接翻译成目标语言。

## 必读

- 翻译前读取 `references/glossary.json`，这是本 skill 的术语表来源。
- 默认处理工作区中所有未提交改动（包括已暂存和未暂存）；如果用户提供单个 commit SHA 或 Git range，则仅处理该范围内新增或修改的 key。
- 如果用户提供的 commit 或 range 无法解析，请停止并向用户报告该输入无效，而不是猜测要处理的文件。

## 怎么找 key

从 diff/commit 中找新增或受影响的文案，重点看：

- `t('...')`、`i18n.t('...')`
- `<Trans i18nKey="...">`
- `i18nKey: '...'`，尤其是错误对象或 `src/shared` 中的 key
- `src/renderer/i18n/for-key-scan.ts` 等动态 key 辅助文件
- `src/renderer/i18n/locales/en/translation.json` 中被改动的英文 value


## 翻译原则

- 先理解 key 所在文件、组件、UI 角色和周围文案，再翻译。
- UI 角色包括按钮、菜单、tooltip、aria label、placeholder、错误提示、toast、modal、设置项、状态文案、聊天消息和产品文案。
- 参考同一组件中目标语言已有译文，保持语气和术语一致。
- 以 `en[key] || key` 作为源文；大多数情况下 `en[key]` 应等于 key。先补全 `en/translation.json` 中缺失或空的 key，再翻译其他语言。
- 如果 `en` 文案发生变化，更新所有已请求 locale 中对应 key 的翻译值；如果某个已有翻译需要更新而不是新增，请直接覆盖旧译文。
- 当 `en` value 和源码 key 不一致时，按 3 步判断：
  1. 先判断 `en` value 是否是有意的 slug key。
  2. 如果不是，再检查是否由 `<Trans>` children 或动态 key 扫描造成的源文错误。
  3. 只有在确认是源文错误时才修改源码，否则只更新 JSON。
- 保留所有 `{{placeholder}}`、`<NamedTag>`、`<0>` 标签和源文前后空格。
- 遵守 glossary 的保留词和强制译法。不要机械直译，写自然、符合目标语言 UI 习惯的译文。
- 按语言逐个翻译：一种语言翻译完就立即写入该语言的 `translation.json`，再开始下一种语言。不要把所有语言的译文都攒到最后一次性写入。
- 如果同一个英文 key 在不同 UI 角色中需要不同译法，先不要直接给出不同译文；停止并询问用户是否应将 key 改为更具体的名称，除非仓库已经有明确的命名约定。

## 完成前

可运行 checker 做确定性检查：

```bash
node .codex/skills/i18n-translate/scripts/check-chatbox-i18n.mjs
```

如果你维护了本次改动 key 列表，可以做严格检查：

```bash
node .codex/skills/i18n-translate/scripts/check-chatbox-i18n.mjs --keys-file /tmp/changed-i18n-keys.txt
```

checker 默认只因缺 key、空 value、多余 key 失败；历史 glossary/placeholder 问题会作为 warning。不要提交 commit，把改动留给用户 review。
