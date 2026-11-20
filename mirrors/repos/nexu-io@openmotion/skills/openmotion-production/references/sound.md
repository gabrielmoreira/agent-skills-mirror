# 声音执行与声画核对

用于落实既定声音决定、工程音轨调整和实际声画时序核对。沿用所选流程、锁定画面与既有意图，不因本页重启声音叙事设计。

## 制作与受限修改

- 用实际可用工具选曲、作曲、编曲、录制、合成或剪辑，不把“有生成工具”当成声音已经设计好。生成模型不能保证精确时序时，先获得音频，再剪辑和编排。
- 给重要结果声音反馈时，避免暗示画面未证明的操作成功、处理速度或真实产品提示音。概念演示中的设计音效不应被说成产品原生声音。
- 声音调整需保持画面不变时，锁定画面版本、时长与时间戳；通过声音剪辑、编排、音色、层次与混音实现。不要偷偷移动镜头或动作来方便卡点。可无损复制视频流并核对视频包／解码帧与时间信息。
- 需要继续编辑时，保留实际使用的音乐、音效等必要分轨及时间关系；不要求为了交付人为拆出无用声部。标记音频增益、偏移和尾音处理，避免工程预览与导出不同。
- 先解决声音职责与编排，再处理均衡、动态、空间与整体响度。技术处理不能挽救与叙事无关的材料；更多声部和更响的声音也不自动更好。

## 审听与比较

有声与静音观看可以帮助识别声音增加了什么；也可临时只听音乐或音效来定位问题。选对当前疑问有用的方式，不机械要求每次完成所有模式。

对比前后版本时，以大致匹配的感知响度为基础，保持同一画面与播放位置，避免更响的一版天然占优。保留原始版；若制作响度匹配副本，明确标记调整，不覆盖原证据。不要同时播放两版声音来判断优劣。

先听段落发展、语义反馈和注意力，再听锚点、音色、混音与首尾。检查声音是否掩盖阅读或语音、让细小动作显得过重、制造不真实空间、不断提示却无重点，或尾音被硬截。削波、声道、响度和波形检查属于技术证据，不是听感评价。

明确记录完成了什么：实际听看、技术测量、代码／时间关系检查，或未验证。没有可靠音频感知能力时，交付可试听对比并标出限制；不能凭 RMS 峰值、声部数量或设计意图宣称“更有情绪”“更自然”或“听感提升”。

## 声画锚点：有声音职责时使用

规划时可先用预期动作相位和音乐结构安排。粗稿出现后，先从实际动态中辨认需要声音支持的主要变化，再与真实音轨的起点、重音／瞬态、乐句转折与留白配对；不能只沿原声画表寻找对得上的切点，而漏掉主导本段观看的场内动作。波形可辅助定位，不只凭文件名、BPM 或均匀网格认定重音；音频起始偏移、淡入与导出偏移都影响结果。同时检查目标相位前后已存在的突出重音：它是否抢先暗示了另一个落点，或盖过了当前动作的反馈。按意图调整原强调的强弱、位置或保留理由；只叠加一个新的同步音效，不能消除旧重音造成的误导。

| 声音事件及来源 | 音频／全片时间 | 实际可见事件、相位及证据位置 | 意图与复核 |
| --- | --- | --- | --- |
| 真实重音、乐句变化、音效或有意留白 | 标明 offset，落到项目帧 | 写明所选感知相位；已实现时给出输出帧／区间或动态片段位置 | 说明为何强调；复听看该区间，记录是否对应 |

- 选与内容有关的少数锚点，不把每个元素或每次转场吸附到节拍；允许有意提前、延后和跨拍，并解释其作用。
- 明确反馈对应启动、变化最清楚、接触还是完成；同一动作这些时刻可能相距很远。代码的起点或结束点不能代替这个选择。
- 绑定实际使用的音频版本、裁切／偏移与画面版本。同一共享时间常数只证明安排相同，不证明感知重点对应；向工程修改流程交接选定关系、证据位置与版本。
- 可以按声音编画面，也可锁定重要画面后调整有权限编辑的音轨；先保证内容、阅读与自然节奏，不用强行拉伸素材换取对齐。
- 原有音乐缺少适合的重音时，可在授权范围内选曲／编曲或添加克制音效。配乐与音效是不同职责；音效不是必需，也不能每次运动都加 whoosh。
- 交付分别记录“时间对应已核对”和“正常速度声画体验已听看”。后者未完成时明确未验证，不以音轨存在或波形对齐代替。

## 配音与可编辑字幕协同

仅当用户明确要求字幕、提供音频或文案求对齐字幕、参考片带有字幕，或所选口播讲解缺少画面文字承载时，才生成字幕轨；纯动效、纯配乐、用户要求不加字幕，或画面大字排版已同步展示同段台词时，不额外叠加底部字幕条，避免两套文字互相遮挡。

禁止对整段未切分音频凭经验估算切分时刻。字幕时间按下列四类真实依据取得：

1. **TTS 通道返回时间元数据（仅 `opendesign` Cloud Key）**：目前仅 `opendesign`（OpenDesign Cloud Key）会将模型返回的字符级 `alignment` 或句/词级 `sentences` 写入 `job.result`；默认优先的 `account`（OpenDesign Plus）以及 `fal`、`wavespeed`、`atlascloud`、OpenAI 兼容接口均不保存 `job.result` 时间戳。可通过 `openmotion_assets_use` 的 `status` 读取 `job.result`，或同时传入 `assetId` 与 `versionId` 调 `action: "get"` 从顶层 `version.result` 读取，过滤仅含空 `words` 的重复句项、按 `startTime`/`endTime`（或 `alignment`）核对文本与顺序一致，并用 `ffprobe` 与 `ffmpeg -af silencedetect` 复核首尾有效发声边界（中英混排时部分模型可能折叠英文词起始时间，需以实际波形/静音检测校准起止）后换算句或词区间。
2. **无时间戳的 TTS 通道或新生成分句配音**：使用 `account` 等不返回时间戳的配音通道时，不要把整篇旁白一次合成为单条长音频；应按句或按拍分段生成语音，对每段实际导入文件运行 `ffprobe` 与 `ffmpeg -af silencedetect`，按容器时长及真实有效发声起止汇总放置对应字幕，防止吞词或提前消失。
3. **无声视频 + 用户纯文案（不配音）**：无需生成伪配音或跑转写，按短句断行与阅读时长直接规划每句起止，写入 `caption_add`。
4. **已有口播录音 + 纯文案（缺时间）或无文案录音**：已有长音频（含误用无时间戳通道整段合成的长旁白）但缺少时间轴时，不重生成 TTS；先按[语音转写与字幕工作流](../../../docs/transcripts.md#public-operations-and-storage)调 `transcript`（`command: "models"`）确认是否有可用转写模型，或直接导入已有 SRT/VTT。若 `models` 返回空且手头只有带人声的音视频而无文案/SRT：禁止将音频 `base64` 编码或强行喂给文本视觉模型（会触发 `400 Audio input is not available`），也不要擅自联网下载安装重型本地 ASR；应先如实告知用户当前未配置语音识别服务，请对方在设置中配置 OpenAI 兼容转写模型，或直接提供口播文案／字幕文件后，再结合 `ffmpeg -af silencedetect` 对齐并挂载字幕。

写入可编辑原生字幕层，不将字幕烘焙进生成画面像素，也不写成无法在字幕面板管理的零散节点：

- 遇到 `data-timeline-locked` 锁定轨道导致加轨或更新被拒时，先解锁轨道再操作，不要退化成零散文本节点；若用户此前已打开过 `CC` 开关并留有 `cueCount: 0` 的空原生字幕轨，`caption_add` 会自动复用该空轨，不会额外叠轨。
- 句级字幕统一调用 `openmotion_assets_use`（`action: "transcript"`），将全部参数嵌套在 `transcript` 对象内（`transcript` 不接受 `workId`）：传入 `command: "caption_add"`、`projectId`、`compositionPath`、带唯一 `id`、`text`、`start`、`end` 的 `segments`（或 `subtitles` SRT/VTT）、`textKind: "caption"`、`captionSettings`、当前 `expectedRevision`、`expectedVersionId` 及稳定 `requestId`，并记录返回的 `trackId`。`caption_add` 仅做加法偏移（不处理裁切与变速），会将 `timelineStart` 累加到每条 `segment` 的起止时间：仅当 `segments` 为未裁切、`1×` 原速（`playbackRate === 1`）单条连续音频的源内相对时间时再传非零 `timelineStart`；只要配音存在入点裁切、变速（`playbackRate != 1`）或多段分段 TTS 拼接，均须先将源音频时间换算/汇总为时间轴绝对时间并将 `timelineStart` 设为 `0` 或省略（禁止非零重复偏移），或先 `import` 转写文档并读取返回的 `document.id` 与 `document.revision`，再调用支持完整 `sourceStart`/`sourceEnd`/`timelineStart`/`playbackRate` 映射的 `captions`（传入 `transcriptId: document.id`、`expectedTranscriptRevision: document.revision` 及工程版本锁）。多段分段生成的 TTS 音频应汇总各句时间轴起止后通过**一次** `caption_add` 合并入同一条字幕轨，禁止逐段建轨。
- 后续仅调整预设、位置、缩放或显隐时，在 `transcript` 内传入 `command: "caption_update"`、`transcriptId: trackId`、`projectId`、`compositionPath`、要修改的 `captionSettings` 字段（如 `{ preset, position, scale, visible }`，或改传 `remove: true` 删除轨道）、`expectedRevision`、`expectedVersionId` 与稳定 `requestId` 原位更新（全片统一切换字幕显隐可用 `caption_toggle`），不重生成配音。`caption_add` 仅自动复用 `cueCount === 0` 的空轨，不会覆盖已有非空字幕轨：在模板改词或已有工程重排字幕词句/时间时，须直接原位更新现有托管字幕节点，或确认合成内无 `data-timeline-locked` 锁定轨道后先调 `caption_tracks` 查出原字幕轨（`kind: "caption"` 且 `cueCount > 0`）的 `id` 与 `settings`，用 `caption_update`（`transcriptId: oldTrack.id`、`remove: true`）移除旧轨，再拿删除调用返回的新 `revision` 与 `version.versionId` 作为下一步写入的 `expectedRevision` 与 `expectedVersionId`（并使用新的独立 `requestId`）重新写入（若后续写入失败，用 `openmotion_restore_version` 恢复删除前版本，避免丢失原字幕），禁止直接追加导致新旧双轨重叠显示。
- `caption_add` 当前固定输出整句模式（`pacing: "sentence"`）；仅在明确需要逐词高亮、且已取得与最终文案严格匹配的有序词级时间戳和已导入工程的真实 `sourcePath` 时，先用 `import` 写入带 `words` 的转写文档并读取返回的 `document.id` 与 `document.revision`，再调用 `captions` 传入 `projectId`、`transcriptId: document.id`、`expectedTranscriptRevision: document.revision`、`compositionPath`、`captionSettings: { pacing: "word" }`、`sourceStart`、`sourceEnd`、`timelineStart`、`playbackRate`、`expectedRevision`、`expectedVersionId` 与 `requestId`。`captions` 会按 `transcriptId` 建独立轨道；为避免多段配音拆出多条碎轨难以统一编辑，逐词高亮仅用于单条连续音频源，不对多段独立 TTS 文件逐段建轨。

编排字幕时按自然停顿与短句断行，控制单屏可读行数；结合背景对比度与影片气质从 `bar`、`clean`、`outline`、`yellow`、`card`、`cinema` 中选定预设，并按画面主体、产品界面细节、已有大字及结尾 CTA 调整 `position`（`bottom`／`center`／`top`）与 `scale`。交片前用 `caption_tracks` 确认存在非空的可编辑原生字幕轨（`kind: "caption"` 且 `cueCount > 0`）而非烘焙像素或普通字卡轨，结合音频时间证据或有声预览核对声画同步，并通过预览或导出帧核对留白与关键画面无遮挡。
