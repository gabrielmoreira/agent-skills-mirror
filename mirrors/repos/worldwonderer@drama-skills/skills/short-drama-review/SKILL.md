---
name: short-drama-review
description: 校验与审查文件系统短剧项目中的原著分析层、故事、剧本、资产、连续性、资产图片提示词、分镜、关键帧和视频提示词，并消费有界授权生产观察做当前项目校准。用户提出“审稿/检查剧本”“检查资产或连续性”“检查图片/视频提示词”“检查原著分析或分集候选”“审查或诊断模板感”“根据生产观察做项目校准”，或判断一集能否交付文本或 JSON 时使用；只发布审查问题、审查结论和修订要求，不代替负责人修改来源文件。
license: MIT
---

# 短剧审查

审查并引用产物证据。优先由未参与当前版本创作的 reviewer 执行；条件不允许时可以自检并如实标注。
只写审查问题、审查结论和按负责人分组的修订要求，不在同一次审查中替 owner 修改创作来源。

审查问题、影响和修订要求在项目内跟随 `short-drama.json#/language`，独立运行时跟随用户
使用的语言，不在本技能内硬编码语言。稳定的规则编号和 ID 保持原样。
本技能从不撰写提示词正文：引用被审查的提示词时按其原样引用，不译成审查语言，
也不因为提示词语言与项目语言不同就判为缺陷——`#/format/prompt_language` 是创作者的选择。

## 开始前

本技能可独立安装和执行。先读取用户明确提供的待审产物与本任务直接输入；若当前目录是
`short-drama` 项目且项目工具可用，可以读取 `status` 并使用其发布生命周期，但缺少 core
或任何其他技能都不是审查工作的阻断条件。[阶段契约](references/stage-contract.md) 给出
本阶段边界、制作形态输入与规则表，无需读取其他技能的文件。

## Quick Start

复制最小 finding/verdict 样例，在完成一次有界审查 pass 后运行：

```text
python3 {技能目录}/scripts/review_check.py \
  --findings examples/minimal-findings.jsonl \
  --verdict examples/minimal-verdict.json
python3 {技能目录}/scripts/selftest.py
```

校验器检查 REV-02 所需字段、证据引用（经文件的 `sources` 声明解析）、阻断项数量和 verdict
一致性；它不代替语义审查，也不要求独立 reviewer provenance。输入路径不存在于当前目录时，
会相对本技能目录解析。

## 选择审查范围

声明一个或多个范围：

- `source_analysis`
- `story_script`
- `assets_continuity`
- `image_prompts`
- `storyboard_keyframes`
- `video_prompts`
- `production_outputs`
- `full_episode`
- `delivery_privacy`
- `project_calibration`

只读对应的审查表。`source_analysis` 读
[rubric-source-analysis.md](references/rubric-source-analysis.md)——它审的是原著分析层
（索引、快评、逐章提取、剧情单元、人物候选、改编价值与分集候选），不审剧本内容，
也不替 `$short-drama-develop` 决定改编方案。完整审查先读
[review-method.md](references/review-method.md)，再读三份审查表；制作端常见缺陷
与各环节判据见 [production-quality-gates.md](references/production-quality-gates.md)。
有创作者提供或授权形成的生产观察，需要绑定准确版本、诊断并路由项目内校准时读
[project-calibration.md](references/project-calibration.md)；没有观察记录时只报文字风险。
涉及参考图权限、遮挡式揭示或补拍版与替代版关系时加读
[阶段契约](references/stage-contract.md) 的参考媒体与补拍一节。
不预先加载所有创作资料。
证据来自项目产物和已接受限制，而非负责人的自我解释。
只有审查问题涉及“模板感、重复手法或 AI 味”时才读
[anti-template-repair.md](references/anti-template-repair.md)，用其诊断、修订示范与误报反例。

## 每轮的工作单元

一轮审查一批明确选定的产物或一段连续范围：记录 verdict 与按 owner 路由的 findings，
报告已审范围和剩余范围，然后交还控制权。产物由各自的 owner 修改；修订与之后的复审
各自是独立的工作单元，由创作者明确请求时开始。

## 工作流

### 1. 确定范围与复核方式

记录要审查的当前产物、已接受限制和范围。优先让未参与该版本创作的人或隔离上下文复核，
因为这能减少自证偏差；条件不允许时可直接自检，并在 reviewer 标签或备注中如实说明。
不要为“独立性”制造运行时证明、上下文 ID 或 provenance schema。

### 2. 先跑结构校验

先检查可证明事实：

- 数据结构、JSONL、稳定 ID 和来源引用；
- 原文落实、资产版本、时间总和与连续性；
- 负责人权限、隐私边界和当前项目状态。

缺少必要输入时停止相关内容审查；互不依赖的问题可以一次汇总。

### 3. 带证据审查内容

重新查看当前资料，不采用负责人的自我辩解。每个 finding 只需包含：

- 可定位的文件、记录、段落、镜头或提示词；
- 必要的短引文或冲突字段；
- 对观众理解或制作的影响；
- 必须达到的修订结果、负责技能、严重程度和状态。

分类使用 `structural_invariant`、`reviewed_invariant`、`craft_default` 或 `taste_option`。
校准 finding 还要说明它观察的是输入参考还是生成结果、适用配置和观察限制。

### 4. 跨层综合

优先守住剧本原意与连续性，而不是奖励华丽提示词：

```text
剧本事实 -> 资产决定 -> 镜头目的与边界 -> 关键帧 -> 动作 -> 下一状态
```

### 5. 给出结论并分派修订

- `APPROVE`：没有阻断问题；
- `APPROVE_WITH_NOTES`：只有不阻断的改进；
- `REVISE`：存在结构、内容或限制冲突；
- `PROVISIONAL`：关键输入不足，暂时无法完成判断。

按 owner 分组；reviewer 发出修改要求，owner 在另一个有界工作单元修改来源。后续明确请求复审时，
重新读取当前版本并只复查受影响范围；本轮不自动进入修改或复审。
CLI 的 `review` 记录 verdict、reviewer 标签和备注；详细 finding 文件用于创作沟通，不是批准所需的
密码学证据包。

## 审查表

- 故事承诺、因果、场景、行动、对白：
  [rubric-story-script.md](references/rubric-story-script.md)
- 资产身份/变体、连续性、资产图片提示词：
  [rubric-assets-prompts.md](references/rubric-assets-prompts.md)
- 原文落实、镜头、关键帧、视频提示词和跨镜状态：
  [rubric-visual-motion.md](references/rubric-visual-motion.md)

## 审查问题与严重程度

从 [finding-template.jsonl](assets/finding-template.jsonl) 建立审查问题，从
[verdict-template.json](assets/verdict-template.json) 建立审查结论。问题目录提供编号、类别、
默认检查方式、严重程度和负责人；审查问题记录本次目标的证据和状态。

### 写上游引用

每个文件先声明本次引用到的上游快照，每条引用再指名快照和记录。

findings.jsonl 首行是声明记录：

```json
{"record_type":"sources","schema_version":"1.0.0","sources":{"screenplay":{"owner":"short-drama-write","artifact":"剧集/EP001/screenplay.md","hash":"<sha256>"}}}
```

verdict.json 用顶层 `sources` 对象声明同样的内容。键取产物文件名，短、小写，
文件内唯一且稳定；同一产物的两个快照用后缀区分。

引用写成：

```json
{"src": "screenplay", "record_id": "EP001-SC001"}
```

指向整个产物或产物内某个字段时只写 `{"src": "screenplay"}`，需要时加 `field`；
`authority`、`role`、`value_seconds` 记在各自的引用上。

- `fatal`：不安全或非公开内容被交付、交付包损坏、缺少授权；
- `error`：阻断当前检查的结构或内容错误；
- `warning`：有具体影响的常用做法问题；
- `note`：创作选择、问题或不阻断交付的润色建议。

没有证据不要打分。不能只说“AI 味”；必须定位重复手法、用套话代替具体内容，或没有铺垫的文句模式，
并解释它伤害什么。

## 边界

- 不提交图片、视频或 TTS 任务，不配置 adapter，也不把 Dashboard 操作当作生产授权。
- `production_outputs` 只复核项目内当前版本的已有媒体；运行环境不能读取或播放时明确记录
  限制，不从文字产物或 adapter 状态推断脸部一致、表演、口型、混音、剪辑或市场表现。
- 生产观察必须绑定准确的 prompt/spec/reference/config 与结果版本，并保留其范围与限制。
- 不把非公开制作观察变成通用审查标准。
- 审查问题只带创作者修订所需的必要证据；不泄露非公开输入、完整创作文本、
  网址或机器路径。
