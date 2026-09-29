# Superpowers 会话诊断打包材料

Session: <session-id>
Harness: <name> <version> (<provenance label>)    Superpowers: <version> (<sha or "not a checkout">; <provenance label>)
Redaction level: skeleton | evidence | full
Built: <ISO timestamp>

把头部的版本字段标注为 historical evidence（历史证据）、unverified snapshot（未核实快照）、
current observation（当前观测）或 unknown（未知）。`environment.json` 对每个环境字段及其
支撑位置都带有同样的来源区分。

## 这是什么

一份经过脱敏的编程智能体会话记录，该会话装了 superpowers 并且出了问题。它让不在场的
智能体或人能够判断 superpowers 是否起了作用，如果是，该改什么。里面的报告用 `path:line`
证据陈述发生了什么。按设计，它不包含对 superpowers 的诊断，也不包含修复建议；那是读者的事。

## 文件

- `report.md` —— 诊断报告（问题陈述、结论、环境、会话、时间线、发现、涉及程度、覆盖说明）。
- `case.md` —— 分析员所依据的案例文件。
- `environment.json` —— 环境一节的机器可读副本。
- `timeline.md` —— 逐轮时间线。
- `findings/<dimension>.md` —— 每个维度的原始分析发现。
- `transcripts/<session-id>.md` —— 每个被检查会话的逐轮精简版本（绝不是原始 JSONL）。
  各级别下的工具结果正文：

  | 级别 | 工具结果正文 |
  |---|---|
  | skeleton | 有意限制；替换为 `[tool result: <tool>, <bytes> bytes, exit <code>]` |
  | evidence | 被引用事件的正文保留，包括支撑发现所需的命令和结果 |
  | full | 全部保留 |
- `scrub-log.md` —— 用到的每个占位符及其类别（绝不包含原始值）。

## 怎么读

从 `report.md` §1–2 开始，然后是 §7（涉及程度）及其引用的证据行，再看 `transcripts/`
中对应的轮次。`path:line` 引用指向提交者机器上的原始文件；同样的行号以 `[L<n>]` 标记
的形式保留在精简后的会话记录中。

## 脱敏

占位符形如 `<EMAIL-1>`、`<PERSON-2>`、`<SECRET-3>`、`<HOST-4>`、
`<REPO-5>`、`<ORG-6>`、`<PROPRIETARY-7>`；家目录路径改写为 `~/…`。在本打包材料内，
同一个占位符始终指代同一个原始值。

## 制作者须知

完成后的打包材料用实际结果替换这些须知。

脱敏之后，只用本打包材料核对每一条实质性的导出发现：把它的引用解析到一个已包含的会话
记录/来源标记，读取被引用的命令/结果或引文，并核实它确实支撑该声明。仅仅路径和行号
存在是不够的。当脱敏级别或必要的保留删去了支撑时，记录具体的局限。

对报告、案例、环境、发现、README 以及任何本地 issue 草稿做对账。针对最终文件（不含日志
本身）刷新 scrub-log 中的计数。删除过时的导出说明；区分打包准备与归档交付。保留一份从
历史锚点到已包含证据的映射。

把独立的隐私审计与证据有用性分开记录：
- 隐私审计：CLEAN，或未解决的遗漏。
- 证据支撑：supported（有支撑）或 limited（有局限），并列出受影响的发现及原因。

检查之后如果内容有变，重做受影响的检查。展示最终日志、文件清单和两项结论，供既有的归档
批准使用。归档经审阅的文件，并核实交付的归档与之一致。把归档交付记录在经审阅的打包材料
之外，而不是在批准后修改其内容。脱敏不是详尽的隐私认证。
