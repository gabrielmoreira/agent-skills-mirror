# 贡献指南

欢迎参与本仓库的本地化贡献。本指南只覆盖术语翻译的请求、决定与落地流程；上游内容刷新仍由维护者按 [`.skills/translate-skill/SKILL.md`](./.skills/translate-skill/SKILL.md) 执行（见 README），本指南不改变那条流程。

## 翻译术语：请求与认领

1. 任何人都可以为仓库里发现的英文术语开 issue 请求翻译。请求包含：术语、出现位置（`文件:行`，可列多处）、可选建议译法、可选理由。参考示例：[#34](https://github.com/vinvcn/mattpocock-skills-zh-CN/issues/34)。
2. 讨论后由维护者决定译法；决定的术语登入 [翻译术语表](./TRANSLATION-GLOSSARY.md) 的「已决定的翻译」表。
3. 任何人都可以认领已决定的术语并开 PR 落地：按术语表替换仓库中的出现位置（大小写不敏感匹配）；PR 描述链接术语表条目与相关 issue。
4. PR 合并后由维护者把术语表条目状态改为 `applied`。
5. 术语尚未决定时保持原文，不要抢先翻译或自行发明译法；新请求先进入术语表的「Translate terms（翻译请求）」区。

## PR 检查清单

- 先 `git add` 暂存改动，再运行下面的检查（脚本只扫描已跟踪文件）：
```bash
node scripts/check-translation.mjs
node scripts/audit-english.mjs
git diff --check
```
- 用 `audit-english` 的输出做人工复核。
- 遵守 [翻译 skill](./.skills/translate-skill/SKILL.md) 的保留规则：identifiers、code、路径、行为关键 labels 不翻译。
- 只改与该术语相关的出现位置。

## 其他贡献

- 发现 bug 或想提改进：直接开 issue 或 PR。
