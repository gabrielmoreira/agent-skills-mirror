---
name: short-drama-write
description: 编剧环节：创作或修订中文短剧、漫剧单集卡、因果节拍与可拍摄的 Markdown 剧本，也负责把现有中文剧本以保留原文、预览语义差异、创作者接受后发布的方式规范化。用户提出“写/改一集短剧”“把大纲写成剧本”“优化场景/对白”“去模板感地修订”“去 AI 味润色”“续写下一集”或提供现成剧本要求进入后续制作时使用；不负责资产、分镜、媒体提示词或终审。
license: MIT
---

# 短剧写作

把单集意图写成可表演、可追踪且会改变故事状态的场景。`screenplay.md` 是唯一可编辑剧本源；卡片和节拍帮助推理，不是另一份正文。

## Quick Start

离线验证剧本分块索引与录音表逐字投影：

```bash
python3 {技能目录}/scripts/selftest.py
python3 {技能目录}/scripts/screenplay_index.py <screenplay.md> --output <screenplay-index.jsonl>
```

## 估算本集时长

写完一集后，可以按**项目自己声明的速率**估算它有多长。套件不带跨项目速率，也不设容差带：

```bash
python3 {技能目录}/scripts/duration_estimate.py <screenplay.md> \
  --index <screenplay-index.jsonl> --project <short-drama.json>
```

脚本见 [duration_estimate.py](scripts/duration_estimate.py)。**它不自己读剧本格式**：哪一段是
台词、哪一段是动作、哪一行是注释，全部按 `screenplay-index.jsonl` 的分块来，所以先建索引再估算。
一个格式两个读法就是两套答案——此前它自带的那套把 `[VO]` 计零秒、把 Markdown 注释当台词计时、
把带冒号的动作段读成对白、把一个多行动作段按行数重复计算。索引与剧本字节对不上时脚本拒绝估算；
索引里还有没归类的文本时，报告里会多出 `incomplete`，说明这个秒数没覆盖全篇。速率写在 `short-drama.json` 的
`format.pacing`（`spoken_characters_per_second` 与 `seconds_per_action_paragraph`），
由创作者按本项目的戏来定——密集争辩和沉默劳作不是同一个折算比。没有声明速率时，脚本只报
台词字数与动作段数，不猜秒数。

结果是**给创作者看的数字，不是门槛**：偏离目标不阻断交付。它的价值在于让"这一集到底多长"
在剧本阶段就能回答，而不是等到分镜环节才发现装不下——那时戏已经写完了。

## 开始前

本技能可独立安装和执行。先读取用户明确提供的单集材料与本任务直接输入；若当前目录是
`short-drama` 项目且项目工具可用，可以读取 `status` 并使用其发布生命周期，但缺少 core
或任何其他技能都不是写作工作的阻断条件。[阶段契约](references/stage-contract.md) 给出
本阶段边界与规则表，无需读取其他技能的文件。

## 先判断入口

1. **有已接受的分集规划**：读取本集进入状态、承诺和交接事实后写作。
2. **只有想法或口述大纲**：在本技能内制作最小单集卡与因果节拍；只有系列方向本身未定时才转 `$short-drama-develop`。
3. **已有规范剧本**：保留作者语言，做定点修订；先说明改动意图和影响。
4. **已有非规范文本，目的是进入后续制作**：保存原始字节；只提议场景标题、对白/动作分块、生产标签与索引所需的最小规范化。展示语义新增、删除、改写、未映射段落与不确定处，得到创作者接受后才能发布。不得补造故事引擎、节拍或新剧情。

## 每轮的工作单元

一轮写一个明确的场景或场景组。“把整集写完”也按场景边界拆成若干轮，每轮：

1. 只读这个单元的直接输入，写或改它的正文，跑本地结构检查；
2. 落盘这个单元，其余范围保持原样；
3. 报告已覆盖范围、剩余范围、未决决定和下一个值得做的单元；
4. 交还控制权，等创作者的下一次请求。

资产拆解、生产和审查各自是独立的工作单元，由创作者明确请求时开始。

## 每次执行

### 1. 读取当前真相

确认创作者约束、已接受的上游事实、本集进入状态和待兑现铺垫。若修订已有剧本，引用当前文件而不是凭对话记忆重写。本阶段拥有什么、继承什么见 [阶段契约](references/stage-contract.md)。

### 2. 确定单集契约的唯一 owner

- **有 accepted `项目开发/episode-map.jsonl` 记录**：复制
  [episode-card.json](assets/episode-card.json)。它在 `sources` 里声明上游快照，用
  `{"src": "episode-map", "record_id": "EP001"}` 指向那条记录，其余只保存写作执行选择；
  不复制、不改写 incoming/objective/turn/payoff/handoff。
- **没有 development map 的 script-first 项目**：复制
  [episode-card-standalone.json](assets/episode-card-standalone.json)，以 `write_standalone`
  模式拥有最小单集契约。

同一集不得同时激活两个模式。若后续建立 development map，先做语义
diff，让创作者明确选择 authority 迁移，将 standalone 契约标记 superseded，
再换成 pointer 卡。若上游契约需改，发 develop owner revision；不在 execution
字段里偷改。不要用悬念替代整集回报。

单集契约进入本阶段时必须包含哪些字段、缺失时怎么办，见
[阶段契约](references/stage-contract.md) 的“单集契约与题材边界”。若只做原文规范化，
跳过本步，不推断缺失剧情。
从想法或 `write_standalone` 直接写作时，本阶段执行已接受的题材与钩子取向，不自行给项目
归类题材；没有已接受取向时按同一节的做法处理，不为贴题材标签另造公式。

### 3. 建立因果节拍

复制 [beats.jsonl](assets/beats.jsonl)，让每条节拍回答：

- 因为什么，谁现在要什么；
- 谁或什么阻挡；
- 观众能看见/听见的行动是什么；
- 信息、权力、关系、情绪、物理状态或风险怎样变化；
- 这个结果怎样制造下一股压力。

若节拍开启新线，明确声明；不要把“然后发生”伪装成“因此发生”。数量与长短服从本集动作，而非统一模板。

关系字段遵守同一约定：同一 `beats.jsonl` 内的前因、铺垫与兑现只写稳定
`because_of_ids`/`setup_ids`/`payoff_ids`，避免自引用文件哈希；来自 episode map、
前集或其他 owner artifact 的关系写 canonical `because_of_refs`/`setup_refs`/
`payoff_refs`。`*_refs` 只放引用对象。

引用这样写：文件首行的 `{"record_type": "sources", "schema_version": "1.0.0",
"sources": {...}}` 记录把每个上游快照声明一次，`sources` 的每个短键映射到
`{"owner": ..., "artifact": ...}`；每条引用写
`{"src": "<sources 键>", "record_id": "<记录 ID>"}`，需要时再加 `field` 指向该记录内
的 JSON pointer。指向整个 artifact 时只写 `{"src": "<sources 键>"}`。同一份文件里
同一个键始终指同一个快照。`.json` 文件把同样的 `sources` 对象写在顶层。

### 4. 先定场景功能，再写正文

对每个场景先回答：为什么必须存在、谁的议程对撞、哪个可见动作承载冲突、哪里发生方向性变化、退出状态给下游留下什么。需要场景与可见行动方法时读取 [script-craft.md](references/script-craft.md)。

写对白前读取 [dialogue-craft.md](references/dialogue-craft.md)，尤其检查人物策略、潜台词、信息争夺和声音差异。
当声源、环境撤出、主动留白、画外存在或相邻场 sound bridge 承担戏剧转向时，读取
[scene-sound-dramaturgy.md](references/scene-sound-dramaturgy.md)。剧本只拥有故事必需的声音事实，
不替分镜设计逐镜声轨，也不用配乐替代表演。

创作者指出某个兑现的呈现方式**可能需要更换**时，读取
[substitutable-realization.md](references/substitutable-realization.md)，把功能、当前实现
与备选实现分开写下来。**不要因此提前磨平任何内容**：先按最想要的拍法写，备选只在真的
需要时启用。创作者没有标注时不做这一步，也不替创作者预判。

长单集需要跨多轮续写、上下文即将切换或中断恢复时，读取
[scene-handoff-capsule.md](references/scene-handoff-capsule.md)，只保存从当前剧本派生的
最小场景交接；一次完成或局部修订时不要额外建立第二份摘要。

### 5. 写唯一剧本源

复制 [screenplay.md](assets/screenplay.md)，严格按 [screenplay-format.md](references/screenplay-format.md) 写：

- `## EP001-SC001 内 · 地点 · 时间`；
- 现在时、可见可表演的动作；
- `角色（可表演提示）：台词`；
- 仅对故事必需事实使用 `[VO]`、`[OS]`、`[SFX]`、`[画面文字]`、`[转场]`、`[连续性]`。

识别创作者交来的行业通行方言（`△` 动作行、`【卡点】` 等）、做原文规范化映射，
或按创作者要求以方言交付时，读取
[production-format-dialect.md](references/production-format-dialect.md)。

不要把镜头、资产全集、模型参数或提示词写进剧本。私密想法要转成行为、证据、空间后果，或明确标记的声音表达。

正文发布后，用 [screenplay_index.py](scripts/screenplay_index.py) 生成只读派生索引；工具只识别格式契约中的场景标题、动作、对白、六种生产标签和注释，并保留 UTF-8 byte offsets 与行范围：

```bash
python3 <skill-dir>/scripts/screenplay_index.py 剧集/EP001/screenplay.md \
  --output 剧集/EP001/screenplay-index.jsonl \
  --source-ref 剧集/EP001/screenplay.md \
  --speaker 葛晴 --speaker 游森
```

由 write owner 阅读当前剧本后，把本集实际说话者逐个传给 `--speaker`；索引器只做精确
标签核对，不用冒号正则猜人物。未登记的 `前缀：内容` 写成 `ambiguous_dialogue_or_action`。

**它不会作为块进入索引**，所以覆盖、时长与配音本都看不到它——必须处理掉，不能留着。
三种处理方式：补入说话者清单（它确实是台词）、改用 `[画面文字]` 等生产标签、或改写这一行
让它不再是「前缀：内容」的形状（动作段里的全角冒号可以改成破折号或拆成两句）。
留着不处理时，分镜阶段的覆盖检查会报 `SHT01_SCREENPLAY_IS_NOT_FULLY_INDEXED`，
时长估算的报告会带上 `incomplete`。

规范化预览尚未获 creator acceptance 时加 `--authority candidate`，使 meta、block 与
source issue 的 refs 都保持 candidate；accepted 剧本发布后再以默认 accepted authority
重建，不得只手改状态字段。

修订后**必须把上一版一起交给索引器**，两个参数成对出现：

```bash
python3 <skill-dir>/scripts/screenplay_index.py 剧集/EP001/screenplay.md \
  --output 剧集/EP001/screenplay-index.jsonl \
  --previous-index 剧集/EP001/screenplay-index.jsonl \
  --previous-source <改稿前的剧本字节> \
  --source-ref 剧集/EP001/screenplay.md --speaker 葛晴 --speaker 游森
```

这样**正文块按内容保 ID**——内容没变的块保住自己的 ID，被改写的块**换新 ID 并让旧 ID 退役**，
于是指向它的下游引用会失败而不是静默改指。同时多一层拆分/合并识别：歧义写入
`mapping_review_request`，必须显式重映射。
**场景标题是例外**：它按 `scene_id` 保 ID，改写标题不换 ID（同一场戏仍是同一场，内容由标题下面
的块承载）。说话者清单从上一版索引读回，与这次传的 `--speaker` 取并集，修订时只传新增的人即可。

**退役是永久的，不只是对下一版**。索引 meta 里的 `block_id_high_water` 记着每个场景、每种块
用到过的最大编号，逐版往下传。没有它时，编号只从上一版索引推：某个场景里某一类块一旦全部消失，
下一版就从 01 重新发号，把一个曾经属于别的内容的编号发给新块——下游引用照样解析得开，
指的却是另一段戏。

**输出路径上已经有索引、却没有告诉索引器上一版是什么时，命令会指名该文件并停下**。
这一条不是礼貌提示：不带上一版重建，ID 按位置重新发放，被改写的块会拿回前一个块退役的编号，
指向它的下游引用于是解析得开、内容却换了一个——而解析得开正是正确引用的样子，下游看不出来。
确实要从零重编 ID（下游引用还没建立，或准备整体重指）就加 `--no-previous`，
让这件事成为一个明写出来的决定。

索引器绝不改写 `screenplay.md`。

正文落定后做一次量级粗测：按项目已接受的语速/字数比把正文字数折成秒数（项目没有这个
比值就向创作者要一个量级），与本集目标时长比一次。差出两倍以上就在报告里点名，由创作者
决定改集长还是拆集；两倍以内不必提。

### 5b. 配音本

项目的对白由录音或 TTS 承担时，配音本和剧本一起交付，不是事后想起来才补的东西：没有它，
拿到剧本的人手里有台词、没有任何一句该怎么念，而这正是下单前最后缺的一块。项目确定
只做无声或字幕交付时才跳过这一步，并在报告里写明跳过的理由。

创作者要为录音准备台词表时，复制
[voice-record-sheet.jsonl.md](assets/voice-record-sheet.jsonl.md)。它是**剧本的投影，
不是第二份台词权威**：首行声明所引 `screenplay-index.jsonl` 快照，其后每行用
`source_ref` 绑定一个剧本块并逐字等于该块，要改词就改剧本再重新投影。

录音顺序几乎从不是剧情顺序（通常按人物集中录），配音者失去的正是上下文，所以每行要补
对谁说、接谁的话、此刻他知道什么、这一句要达成什么。写策略而不是情绪词——"愤怒"不可
执行，"质问"可执行。多音字、生僻字与专名的读法在进棚前定完并留痕；棚里中断是最贵的。

音色描述属于角色档案，由 assets owner 按 `$short-drama-assets` 的 `voice-direction.md` 写；
配音本用 `source_ref` 指向它，不在这里另写一份。两份都在，一句台词才既有词也有声音。

本写作阶段不生成音频，也不从这份文本判断成品音质；实际 TTS 的确认后生产边界见文末。

写完后用 [voice_sheet_check.py](scripts/voice_sheet_check.py) 核对它仍然是投影：

```bash
python3 <skill-dir>/scripts/voice_sheet_check.py 剧集/EP001/voice-record-sheet.jsonl \
  --index 剧集/EP001/screenplay-index.jsonl \
  --screenplay 剧集/EP001/screenplay.md
```

脚本按块 ID 定位、切出剧本原字节，再逐字比对台词与说话人。剧本改过而
索引没重建、或有人在表里顺手改了词，都会被单独报出来——**这两种情况下的配音本看起来
和正常的一模一样**，而它被带进录音棚的那一刻正是没人能核对的时刻。

只覆盖部分对白（按人物或按场次分表）是正常做法，未覆盖的块只报告不判错。

### 6. 修订而不是抹平

按顺序做所有者修订：

1. **因果**：选择是否造成后果，转折是否由已存在的压力产生；
2. **场景**：目标、反对、转向、退出是否清楚；
3. **可拍性**：情绪和认知是否有演员能执行的载体；
4. **对白**：每轮是否在争取、回避、试探、逼迫或重新定义关系；
5. **生产事实**：必读文字、画外音、画外对白、关键声音和连续性变化是否有边界标签；
6. **交接**：本集结束的知识、持物、伤势、关系和决定能否成为下一集准确开场。

局部修订保留不相关段落。先展示语义差异与可能失效的下游产物，创作者接受后再发布。

### 7. 报告审查交接

完成结构检查后只报告当前范围是否适合单独复核，不自动启动复核。若之后收到带证据的修订请求，
只修改本技能拥有的单集卡、节拍或剧本；完成该有界修订后再次交还控制权，复审需要新的明确请求。

## 规则分级

- **`structural_invariant`**：场景/块 ID、引用、已有生产标签语法、来源哈希与明确矛盾；
  校验器可阻断。
- **`reviewed_invariant`**：因果是否成立、场景是否真正转向、内心是否可表演、对白是否改变局面，
  以及生产关键事实是否漏标；reviewer 须引用文本证据。
- **`craft_default`**：进入得晚、退出得早、以选择和后果推动、用具体动作承载情绪；可说明理由覆盖。
- **`taste_option`**：沉默、旁白、方言、打断、场景静动、句式节奏；遵从创作者选择。

不要把统一的爆点安排、转折时刻、台词比例、字数、场景数或节拍数设为质量门槛。

## 产物与边界

本技能只拥有：

- `剧集/<EP>/episode-card.json`（上游 pointer + write execution，或显式
  `write_standalone` 契约；二者不并存）
- `剧集/<EP>/beats.jsonl`
- `剧集/<EP>/screenplay.md`
- 由剧本生成的 `screenplay-index.jsonl`
- `剧集/<EP>/voice-record-sheet.jsonl`（对白由录音或 TTS 承担时）
- 规范化预览与语义修订差异

资产身份、分镜边界、图片/视频提示词及终审结论属于其他技能。本技能不生成媒体。

创作者要求实际合成已确认台词时，把当前录音表与声音绑定交给 `$short-drama-produce`。
生产技能必须先展示本次 TTS 任务的原句、角色/声音、数量、参数和输出路径，并取得针对这份
预览的明确确认；本技能不会替创作者确认，也不会把剧本接受状态当作付费生产授权。
