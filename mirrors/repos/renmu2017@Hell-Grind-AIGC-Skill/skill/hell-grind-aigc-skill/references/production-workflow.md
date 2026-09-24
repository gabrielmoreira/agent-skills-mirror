# AIGC 视频生产管理工作流

## 生产原则

- 项目事实、镜头契约、提示词、平台适配、生成记录和选择决定分别保存。
- 十阶段目录是数据流，不是文件收藏夹。
- 每阶段都有进入条件、核心产物、退出门和返工去向。
- 任何生成都要有当前任务授权、provider、次数/预算和权利边界。
- 本地初始化、审计和校验固定 0 个网络请求、0 次数据库读写。

## `00_brief`：目标与授权

**进入条件：** 用户给出创意或生产目标。

**核心产物：** `project.yaml`、`brief.md`。

**必须明确：**

- 一句话故事、观众、用途和发行场景。
- 总时长、画幅、帧率和实际交付目标。
- 创意硬约束和禁区。
- 权利状态、生成授权、预算/次数和 provider 边界。
- 发布授权与生成授权分开。

**退出门：** 目标可验收；关键权利和行为授权无歧义。

**返工：** 目标或权利不清回本阶段；不能用后续提示词代替决策。

## `01_story`：故事与世界规则

**进入条件：** brief 已批准。

**核心产物：** `story-bible.md`。

**必须明确：** 世界规则、角色目标和弧光、视觉母题、颜色/声音母题、时间地点、禁止变化和结局状态。

**退出门：** 每场戏能说明改变了什么；世界规则不自相矛盾。

**返工：** 镜头目标反复变化或角色行为无因果时回故事阶段。

## `02_assets`：身份、状态与参考

**进入条件：** 故事需要的角色、生物、道具、场景和视效可列举。

**核心产物：** `assets.csv`、`reference-scope.csv`、`asset-state-matrix.csv` 和批准参考。

**必须明确：** 稳定 ID、identity invariants、state variables、多视图覆盖、材质、比例、道具交互、场景空间、inherit/exclude、权利状态和批准状态。

**退出门：** 进入首批镜头所需的最少资产版本全部 approved；缺失视角已登记。

**返工：** 身份漂移和状态回退先回资产，不在镜头提示词中无限补人物描述。

## `03_scenes`：场次与空间

**进入条件：** 关键资产和故事顺序可用。

**核心产物：** `scenes.csv`、`spatial-map.csv`。

**必须明确：** 场次顺序、地点 ID、区域、时间、故事目标、进出状态、出入口、固定锚点、光源和允许资产。

**退出门：** 每场戏的开始/结束变化和空间关系可检查。

**返工：** 房间每镜重建或角色位置无法解释时回场景空间图。

## `04_shots`：镜头契约

**进入条件：** 场次目标和空间已批准。

**核心产物：** `shots.csv`、`beat-sheet.csv`、`audio-cues.csv`。

**必须明确：** 镜头功能、时长、允许角色、open/close state、动作时间线、camera start/path/end、对白与声音、continuity in/out、三栏约束和 risk focus。

**退出门：** 动作和对白服从时长；首尾状态可画出；没有多个主运镜。

**返工：** F-ACTION-OVERLOAD 或 F-CAMERA-CONFLICT 回镜头拆解，不直接进入提示词加词。

## `05_prompts`：版本化表达

**进入条件：** 镜头契约为 `contract_ready`。

**核心产物：** `prompt-index.csv`、平台无关主提示词、独立适配层。

**必须明确：** prompt ID/version、父版本、changed variables、变更原因、硬约束、平台适配和哈希。

**退出门：** 本地审计无 error；人工确认资产、时间、空间、声音和连续性。

**返工：** 表达遗漏回提示词；契约本身不成立则回 `04_shots`。

## `06_generations`：调用与迭代

**进入条件：** prompt approved，且当前任务明确授权 provider、次数/预算和参考权利。

**核心产物：** `generation-log.csv`、`iteration-log.csv` 和本地输出路径。

**必须明确：** generation ID、batch、prompt ID、provider/model/参数、时间、状态、成本、失败码、changed variables 和 hypothesis。

**退出门：** 每次尝试可追溯；达到批次目标或停止条件。

**返工：** 依失败责任层回资产、镜头、提示词、适配或转后期；不默认继续抽卡。

## `07_review`：评审、选片与连续性

**进入条件：** 存在可评审生成结果。

**核心产物：** `selection-log.csv`、`continuity-matrix.csv`、`waivers.csv`、`qa-checklist.md`。

**必须明确：** hard gate、候选优缺点、选择理由、已知缺陷、跨镜影响、豁免和负责人。

**退出门：** selected 镜头有唯一选择记录；error 已修复或批准豁免。

**返工：** 按失败码回具体责任层；不让“最好看”覆盖叙事和连续性问题。

## `08_edit`：时间线、声音和后期

**进入条件：** 镜头有选择或明确临时占位。

**核心产物：** `edit-notes.md`、时间线版本和后期问题表。

**必须明确：** 镜头顺序、切点、声音桥、字幕、调色、视效修复、占位状态和未解决问题。

**退出门：** 画面与声音结构完整；所有后期修复可追溯到镜头和生成。

**返工：** 若问题无法用剪辑/合成合理修复，回选择或生成，不用后期掩盖身份/人数硬错。

## `09_delivery`：交付与发布分权

**进入条件：** 时间线锁定，问题关闭或豁免。

**核心产物：** `delivery-checklist.md`、交付文件和归档清单。

**必须明确：** 实际时长、帧率、画幅、分辨率、音频、字幕、片尾署名、权利、源文件、版本和发布授权。

**退出门：** 技术、内容、权利和归档门通过。

**返工：** 技术错误回 edit；内容硬错回 review/上游；权利不清停止交付。

**重要：** `ready_for_delivery`、`ready_for_review`、`published` 是不同状态。交付完成不自动授权上传或发布。

## 状态机

### 资产

```text
proposed → reference_ready → approved → deprecated
```

### 镜头

```text
planned → contract_ready → prompt_ready → generated → reviewed → selected → locked
```

`generated/reviewed/selected` 可进入 `needs_revision`，但必须记录失败码、上一版本和 next_action。

### 提示词

```text
draft → checked → approved → superseded
```

## 单一数据源

| 事实 | 文件 |
|---|---|
| 项目目标、画幅、预算、授权 | `00_brief/project.yaml` |
| 世界规则 | `01_story/story-bible.md` |
| 资产身份/状态/参考范围 | `02_assets/*.csv` |
| 场次和空间 | `03_scenes/*.csv` |
| 镜头、动作、声音 | `04_shots/*.csv` |
| 提示词版本 | `05_prompts/prompt-index.csv` |
| 调用与迭代 | `06_generations/*.csv` |
| 选择、连续性、豁免 | `07_review/*.csv` |
| 剪辑决定 | `08_edit/edit-notes.md` |
| 交付与发布授权 | `09_delivery/delivery-checklist.md` |

提示词引用事实，不重写事实。生成平台历史、聊天记录和文件夹名都不是项目单一数据源。

## 调用与数据库成本

本地初始化、提示词审计和项目校验固定：

- 网络请求：0。
- 数据库读写：0。

真实生成次数与成本按用户当前授权执行并逐次记录；Skill 不自动调用付费模型。
