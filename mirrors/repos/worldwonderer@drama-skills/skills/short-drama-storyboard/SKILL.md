---
name: short-drama-storyboard
description: 把已接受的中文短剧剧本和资产转成原文落实表、有戏剧动机的镜头、连续性边界与冻结关键帧提示词；关键场次可先做场次视觉计划或 Coverage Audition 比较真正不同的导演方案。用户提出“拆分镜/设计镜头/做镜头表”“场次视觉计划/调度故事板”“比较导演方案/Coverage Audition”“写首帧/关键帧提示词”“检查轴线、站位、视线、持物连续性”，或需要在不生成媒体的前提下把竖屏短剧、漫剧的剧本内容转成可拍的画面时使用。
license: MIT
---

# 短剧分镜与冻结关键帧

先守住故事内容，再安排原文落实、空间和镜头，最后写冻结关键帧。不在这里写随时间
变化的运动提示词，也不改写剧本或资产事实。

镜头目的、边界说明与场次视觉计划是创作者读的：项目内跟随 `short-drama.json#/language`，
独立运行时跟随用户使用的语言。关键帧的**可复制提示词正文**在项目内跟随
`#/format/prompt_language`，独立运行时由用户指定、未指定则为 `en`。不要用
其中一个推断另一个。ID、规则编号和字段名在两者之下都保持原样。

## Quick Start

离线验证时长合计和关键帧边界绑定的正反例：

```bash
python3 {技能目录}/scripts/selftest.py
python3 {技能目录}/scripts/storyboard_check.py <coverage.json> --shots <shots.jsonl> --keyframes <keyframes.jsonl>
```

## 开始前

本技能可独立安装和执行。先读取用户明确提供的剧本、资产与本任务直接输入；若当前目录是
`short-drama` 项目且项目工具可用，可以读取 `status` 并使用其发布生命周期，但缺少 core
或任何其他技能都不是分镜工作的阻断条件。[阶段契约](references/stage-contract.md) 给出
本阶段边界、制作形态输入与规则表，无需读取其他技能的文件。

## 按需读取资料

始终读取：

- 状态为 `accepted` 的 `screenplay.md` 与 `screenplay-index.jsonl`；
- 状态为 `accepted` 的资产、版本与相关连续性；
- `short-drama.json#/creator_authority/visual_direction` 中状态为 `accepted` 的视觉方向；
  若状态为 `unset`，就向创作者给出选择，不从对话记忆补造。

设计原文落实、场面调度、摄影机和剪切时读
[shot-craft.md](references/shot-craft.md)；只有写冻结帧时读
[keyframe-craft.md](references/keyframe-craft.md)。需要制作端的时长依据、景别与运镜
词表或时间片写法时读 [production-shot-grammar.md](references/production-shot-grammar.md)。
关键场次需要先组织整场的立场、空间、摄影与声音运动时读
[scene-visual-plan.md](references/scene-visual-plan.md)；第一种合理拍法不应直接成为唯一答案时加读
[coverage-audition.md](references/coverage-audition.md)。
涉及背影、裁切、遮挡、画外或延迟揭示时读
[阶段契约](references/stage-contract.md) 的参考媒体与补拍一节。
只有所有权或直接输入影响不清楚时，才读核心所有权契约。

- 竖屏多人、单房对白、证据揭示、群体轴线或门内外视角：
  [blocking-playbooks.md](references/blocking-playbooks.md)
- 需要查看“剧本 → 原文落实 → 镜头 → 关键帧”的完整正例，或对白表演括注
  `（情绪）` 怎样同源投影到本镜表演状态与下游 `delivery`：
  [screenplay-to-keyframe-example.md](references/screenplay-to-keyframe-example.md)

## 每轮的工作单元

一轮处理一个场次或一段连续镜头范围。整集请求按这些边界拆成若干轮，每轮：

1. 只读这个范围的直接输入，做它的覆盖与镜头设计，跑本地结构检查；
2. 落盘这个范围，其余范围保持原样；
3. 报告已覆盖范围、剩余范围、未决 coverage 和下一个值得做的范围；
4. 交还控制权，等创作者的下一次请求。

视频提示词、生产和审查各自是独立的工作单元，由创作者明确请求时开始。

## 工作流

### 1. 先确认每段原文由谁落实

从 [coverage-template.json](assets/coverage-template.json) 开始，接受后发布为
`剧集/<EP>/storyboard/coverage.json`。每个与制作有关的剧本段落都必须标明一种处理：

- `covered`：由一个或多个镜头落实；
- `intentional_repeat`：因表演或剪辑需要而有意重复，并写明理由；
- `omitted_with_reason`：有理由地省略；
- `nonvisual_context`：仅供理解、无需直接呈现的内容。

对白、动作、画面文字、画外音或关键音效还没有着落时，不要先追求漂亮镜头。
发布原文落实表时，先在文件的 `sources` 里为每个上游快照声明一次 `owner` 与 `artifact`，再让每条 `shot_refs` 用 `src` 指向该声明并写上 `record_id`。裸 `shot_id`
只可表示同一镜头文件内的关系，不能证明审的是哪一版。

### 2. 关键场次先比较整场导演选择（可选）

只有导演选择明显改变体验时才增加本层。若存在多种真正不同的观看方法，先用
[coverage-audition.example.jsonl](assets/coverage-audition.example.jsonl) 比较信息时机、对齐对象、
表演空间、最强画面、落点、损失和制作相容性；创作者选择后，再用
[scene-visual-plan.example.jsonl](assets/scene-visual-plan.example.jsonl) 把所选方法写成整场的戏剧转向、
观众立场、空间压力、视觉推进、摄影节奏、反应落点与声音策略。只有一个明确方法时直接写计划，
不为流程完整补 audition。

这层不新增剧本/资产事实，也不拥有 shot purpose、duration 或 start/end boundary。普通场景跳过；
不固定方案数、宫格或镜头数。

### 3. 先写镜头目的

使用 [shot-template.jsonl](assets/shot-template.jsonl)，接受后发布为
`剧集/<EP>/storyboard/shots.jsonl`。每个镜头先用一句话回答：

- 观众此刻必须注意什么、感到什么；
- 信息、情绪、观众立场或权力关系发生什么变化；
- 为什么要在这里切镜，而不是留在前一镜。

同时按事实填写 `audience_visibility`：准确来源、现在展示还是暂缓展示、可见或可听的
载体，以及各自的 `reveal_trigger`（何时揭示）和 `protection_method`（怎样防止提前泄露）。
遮挡不是默认的画面风格：它既不能提前泄露剧本保留的信息，也不能藏掉本镜必须交代的
证据或反应。

之后才选择景别和摄影机行为。镜头不是给动作段落加几个摄影形容词。
若本场有已接受视觉计划，每镜用准确 `scene_visual_plan_ref` 说明自己投影其中哪一段变化；
只在这类镜头记录中新增该字段。普通场景完全省略；计划与来源冲突时退回负责人，不靠 shot 覆盖。

### 4. 绑定空间和资产

绑定准确的场景及视角、人物及造型、道具及状态和剧本来源段落，并建立：

- 位置、朝向、视线、屏幕运动方向与轴线；
- 进出路线和不随镜头改变的场景锚点；
- 双手与持物、伤势与服装、文字状态、光线方向；
- 有权威性的镜头开始边界和结束边界。

可见字样必须通过 `text_treatment_refs` 指向资产负责人已接受的文字政策。预览只能
指向带 `authority: candidate` 的候选政策。镜头和关键帧可以决定构图怎样让文字可见，
但不得把 `exact_readable` 偷换成装饰字、凭空写新文案，或用自由文本代替政策引用。

需要的资产或状态缺失、含混时，向资产或编剧环节提出修订，不要猜绑定关系。
若创作者要求从头到尾预览，只能针对唯一且不是 `unresolved` 的提案建立临时的原文落实、
镜头和关键帧。候选引用要明确标为待确认，不得写成已接受的绑定，
也不得获得最终批准。

### 5. 设计能够制作的镜头

短镜头通常围绕一个主要动作，再保留让观众读懂后果所需的反应；这不是镜头数量公式。
一个镜头守不住空间关系、表演、对白或信息变化时就拆开；新切镜没有增加注意重点或
戏剧价值时就合并。

上游明确的事件先后也是故事事实，不是可以为省镜头而重排的素材。把相邻镜头的开始/结束
边界顺读一遍：冻结首帧不得提前包含本镜随后才发生的认出、松手、决定或持物变化；合并镜头
也只能压缩停留，不能让后发生的接收跑到前一个动作之前。

时长表示剪辑意图。只有明确的计时算术可以机械检查；一般的可拍性必须结合本镜内容判断。

写 `duration_seconds` 之前，先按项目在 `short-drama.json` 的 `format.pacing` 里声明的速率，
把每个镜头认领的剧本块折算成秒——台词按字数、动作段按段数，这与 `duration_estimate.py` 在
剧本阶段用的是同一组速率。折算值是起点，为节奏调整它是创作决定；跳过折算直接凭感觉写，
整集总时长会到覆盖检查那一步才暴露，而那时要重排的是全部镜头。项目没有声明速率时先向
创作者要一个量级。

### 6. 默认每镜一个冻结关键帧

使用 [keyframe-template.jsonl](assets/keyframe-template.jsonl) 写结构化来源，发布为
`剧集/<EP>/storyboard/keyframes.jsonl`；再用
[keyframe-prompts.md](assets/keyframe-prompts.md) 渲染可复制的派生文本。结构化关键帧
保存只属于单帧的选择；Markdown 不是第二份事实来源。

把已接受镜头的开始边界和准确资产版本，落到一个可以同时存在的瞬间：焦点、构图、
摄影机与镜头焦段、空间锚点、姿态、目光、双手与持物、表情、光线、排除项。

`generic_prompt` 写这一瞬间要拍出来的画面本身，按 `keyframe-craft.md` 的十二项逐条写满，
那里有一段四百余字的成稿可以照着写。它只含要被拍出来的内容——不写镜头/记录 ID、规则 ID、
状态词与成段否定罗列（`SHT-21`）。同一集里两条关键帧的正文不应该只有编号不同：
读起来一样，说明写的是模板不是画面。

关键帧不得包含“先、再、最后”、表演变化过程、运镜过程或正在变化的环境；时间变化
交给 `$short-drama-video-prompts`。

### 7. 校验并呈现

先做原文落实、参考图权限和连续性的结构检查，再按制作资料自检。
候选预览也必须精确加总逐镜数值时长；若仍有未定时长或尚未完成这笔账，宁可省略总时长并
列出未决项，也不要写一个与镜头表不一致的约数。

时长账目与关键帧边界这两项是纯记账，交给
[storyboard_check.py](scripts/storyboard_check.py) 核对，不要用人工目测代替：

```bash
python3 <skill-dir>/scripts/storyboard_check.py 剧集/EP001/storyboard/coverage.json \
  --shots 剧集/EP001/storyboard/shots.jsonl \
  --keyframes 剧集/EP001/storyboard/keyframes.jsonl \
  --screenplay-index 剧集/EP001/screenplay-index.jsonl \
  --project short-drama.json
```

给了 `--screenplay-index` 就多做一项覆盖对账：**剧本的每一个块都要有一种处理，而镜头认领
必须与那种处理相符**。`covered` 要恰好一个镜头认领，`intentional_repeat` 可以多于一个，
`omitted_with_reason` 与 `nonvisual_context` 不应有镜头认领——后两种是"决定不拍"，
写清理由即可。认领按块 ID 走（`source_refs` 里的 `record_id`），不按正文——正文一直在改，
块 ID 不变。

处理表本身也一起校验：状态必须是上面四种之一，一个块只能有一行，指向的块要在剧本索引里，
`intentional_repeat` 与 `omitted_with_reason` 必须写理由。此前这张表没有任何检查，
删掉几行、填一个不存在的状态、把 `shot_refs` 指向别的镜头都能通过——覆盖表与 `shots.jsonl`
是关于同一件事的两份独立说法，中间没有对账。

它只做算术和结构比对：本集时长总和是否等于各镜头 `duration_seconds` 之和、覆盖列出的
镜头有没有既不计入也不挂起、`shots.jsonl` 里的镜头有没有整个从总和里消失、
同一个镜头有没有在总和里被列两次（列两次就会被加两次）、有没有边界条目整条写成「同上」「位置不变」这类回指、
每张关键帧是否声明了 `boundary_role` 并绑定对应边界字段、
同一镜头的同一端有没有两张关键帧、每条引用的 `src` 能否在本文件 `sources` 里解析到一个
上游快照。有 `--project` 且项目声明了每集目标时长时，还会核对
带符号差值。**差值不是缺陷**，脚本只检查它算得对不对。

脚本报错时先修产物再继续；它不评价镜头好坏，也不决定该拆多少镜。需要逐条查诊断码
含义、或确认某项该由脚本判还是由审查者判时，读
[review-and-fixtures.md](references/review-and-fixtures.md)。

候选选择清单必须覆盖正文中全部新增导演选择；没有必要让创作者判断的环境微动、具体手位或
声音时机就删除，不能一面写进可执行提示词，一面在接受摘要中省略。
摘要按选择类别总括本场全部新增的观众立场/信息时机、代表帧/最强画面/场尾落点、
机位/景别/运动与停留、时长/节奏、手势/目光/表演信号、声音进入/撤出/留白与视觉处理，
并声明“正文中未由来源接受的执行选择仍全部保持候选”，
不逐镜复述已经清楚标注的细节。只点名会改变信息时机、因果顺序、观众立场或表演所有权、
可读文字、场尾落点、制作成本或回退路径的高影响例外；正文新增项若既不在类别范围内也未被点名，
就删除或补入摘要。总括是接受范围，不会把正文选择悄悄升级为已接受事实。

若创作者尚未声明交付面遮挡区，内容构图仍可作为候选比较，但播放面避让核验保持 `blocked`，
整体不能称为 `delivery-ready`；该缺口必须出现在本次准备度摘要中。只列真正影响当前候选判断或
请求交付范围的缺口，不要罗列与本次候选判断无关的正式发布先决条件。

按顺序呈现：

1. 尚未落实的原文与 `unresolved` 项；
2. 按场分组的镜头表；
3. 可复制的关键帧提示词；
4. 相对剧本原意发生的差异；
5. 需要创作者接受的选择。

本技能不在本轮自动启动终审；需要 delivery verdict 时，把当前有界范围作为单独请求交给
`$short-drama-review`。

## 修订

若运动提示词环节要求修改镜头开始或结束边界，负责人仍是本技能。对照剧本原意审查
提议，修改当前有界范围的镜头与关键帧，并展示哪些旧产物已经关闭或需要刷新。运动提示词与
终审属于后续的独立工作单元，本轮只报告它们的影响范围。
运动提示词文件不得悄悄变成第二份边界事实。
镜头重排、插入、拆分或合并时读取
[shot-revision-identity.md](references/shot-revision-identity.md)，保留稳定身份、retire 被替代 ID，
并重新对账 coverage 与全部下游引用；只在确有 predecessor/retirement 时新增
`revision_lineage`，并使用 [按需 lineage 片段](assets/revision-lineage.fragment.json)；普通新镜不保存
空 lineage。不用数组位置或文本相似度决定 ID。

## 边界

- 不生成图片或视频。
- 镜头绑定资产，不把完整外观描述复制到每一镜。
- 外部制作单位不等于创作镜头本身的编号。
- 镜头数量、每次切镜秒数、焦段分布都不是通用定律。
- 新增或删除故事事实，必须先由编剧环节修订。
- 创作者要求把已接受关键帧实际生成图片时，连同绑定和参考文件交给
  `$short-drama-produce`；由生产技能展示任务预览并取得明确确认，本技能不调用媒体服务。

## 所有产物

- `剧集/<EP>/storyboard/coverage.json`
- `剧集/<EP>/storyboard/coverage-auditions/<SC>.jsonl`（仅关键场次需要比较方案时；每场独立接受，项目工作历史，
  默认不进执行交付包；accepted 后打包时显式传 `--omit`，不会按文件名静默排除）
- `剧集/<EP>/storyboard/scene-visual-plans/<SC>.jsonl`（仅关键场次需要场次计划时；每场独立接受）
- `剧集/<EP>/storyboard/shots.jsonl`
- `剧集/<EP>/storyboard/keyframes.jsonl`
- `剧集/<EP>/storyboard/keyframe-prompts.md`（仅派生文本）
