# 分镜阶段契约

## 目录

- [独立运行与项目集成](#独立运行与项目集成)
- [所有权边界](#所有权边界)
- [制作形态需要什么](#制作形态需要什么)
- [参考媒体与补拍](#参考媒体与补拍)
- [本阶段规则](#本阶段规则)

本文件是本技能的自包含契约：预检、所有权、形态输入与规则表都在这里，
不需要读取其他技能的文件。

## 独立运行与项目集成

本技能可以单独安装并运行；下面几条说明项目工具存在时怎样集成。

1. **读取直接输入**：只读取用户明确提供或当前任务实际需要的文件，不批量加载整个项目。
2. **可选项目集成**：若存在 `short-drama.json` 且 core 项目工具可用，可以运行
   `python3 <core>/scripts/project_tool.py status <project>`，使用返回的目录布局和语言设置；
   core 不可用时，直接基于已提供输入产出本阶段文件。
3. **可选发布生命周期**：项目工具可用时，用 `publish` 原子发布并用 `--input <path>`
   声明直接输入；`accept`、`review` 与 `package` 继续承担确认、复核与交付。
4. **保持职责分离**：创作者确认、内容修订和复核是不同动作；reviewer 提修改要求，负责人改文件。

## 所有权边界

- **本阶段拥有**：可选 coverage audition 与场次视觉计划、覆盖处置、镜头目的、镜头时长、
  绑定、起止边界；关键帧的注意焦点、构图、机位/镜头与冻结站位。渲染出的关键帧提示词是缓存。
- **本阶段继承**：剧本的信息权限与原文要求；资产的身份与变体绑定。
- **本阶段不越权**：不用风格词改写人物状态，不新建资产身份，不改写剧本事实。镜头边界
  拥有起止位置、姿态、目光、双手、持物与可见连续性；关键帧只投影这些事实，永不覆盖它们。

## 制作形态需要什么

视觉风格不是贴在提示词前面的标签。创作者已接受的视觉方向与制作形态由项目层决定并传入，
**本技能不加载形态卡，也不自行选择形态**；本节只说明本阶段需要形态回答什么、以及拿到
答案后投影成哪些字段。

形态决定属于 `craft_default`：创作者说明理由即可覆盖。形态不能创造新的
`structural_invariant`，也不能改写身份、地理、持物归属与可读文字政策。审查者不得单凭
形态偏好阻断交付。

不要用“加一句风格前缀”处理形态差异。前缀只改变检索标签；形态改变的是**必须出现和
可以省略的字段**，只有后者会被执行，也只有后者能被审查。

本阶段要向形态决定问：**注意力、层次、遮挡、可动层与冻结边界**在本形态下怎么表达。

运动预算的默认值随形态改变：实拍默认全动作，要写的是限制；三维默认可全动作，但摄影机
是最贵的一层；限动画与水墨默认保持姿态，要写的是**哪一层例外**；Q 版默认一镜一因果。
省掉这一判断的后果可预测：默认保持姿态的形态会被写成全员飘动，默认全动作的形态会被
写成一串没有接触点的动作词。

本阶段新增：注意力、层次、遮挡、可动层与冻结边界。

## 参考媒体与补拍

- **参考图能决定什么要逐张写明**：每张参考的用途、可以照搬什么、不可以照搬什么。身份参考
  不自动决定构图；构图、尺度或效果参考不自动带入图中人物、服装、文字、道具与故事状态。
- **像素主张需要证据**：关于参考图上可见内容（尤其文字、水印、标牌、界面）的断言，必须
  来自创作者/参考图权利人的可核对说明，或运行环境获授权后形成的输入参考观察记录，并绑定
  被检查的字节。两者都没有时保持 `unverified`，负面提示词不能代替证据。
- **观众揭示时机**：某一事实何时可被观众看到，由已接受的可见性决定绑定其来源、载体、
  权限、触发与保护方式。构图既不能提前泄露该事实，也不能遮掉本环节必须传达的载体。
- **母版、补拍与替代**：补拍默认只补充、不替代母版。普通母版不增加版本范围字段；只有
  补拍/替代版才声明 `pickup | alternate`，用同一文件内稳定的记录 ID 说明母版与补充关系，并把每项原文要求对应到当前字段或说明
  去向。只有下游审查结论才能批准替代，不得回写形成循环引用。

## 本阶段规则

### `SHT`

| ID | Class | Knowledge |
|---|---|---|
| SHT-01 | structural_invariant | Every production-relevant screenplay block has a coverage disposition. |
| SHT-02 | reviewed_invariant | Each shot has a dramatic/viewing purpose and preserves its source meaning. |
| SHT-03 | craft_default | Keep a short shot focused on the smallest action/reaction unit that carries its purpose; combine or split it according to performance, information, and continuity rather than a fixed count. |
| SHT-04 | craft_default | Change framing/camera because attention, pressure, alignment, reveal, or rhythm changes. |
| SHT-05 | structural_invariant | A keyframe projects one accepted shot boundary and exact asset variants. |
| SHT-06 | reviewed_invariant | A keyframe is one freezeable instant, not an ordered action chain. |
| SHT-07 | taste_option | Lens vocabulary, tempo, and locked/handheld/formal style follow visual direction. |
| SHT-08 | reviewed_invariant | Each authoritative source action is realized once; repeated coverage adds reaction/detail/recontextualization rather than replaying it. |
| SHT-09 | reviewed_invariant | Exact Location/View orientation and visible anchors match the camera side used by the shot. |
| SHT-10 | reviewed_invariant | Rendered keyframe prose contains only facts from the boundary that keyframe declares. A start frame carries no state first created by the shot's motion or end; an end frame carries no state already spent before it. Neither frame borrows the other's facts. |
| SHT-11 | craft_default | When information changes another person's power, relationship, knowledge, or choice, preserve that reception visibly; shot count, framing, and duration follow the consequence and project profile. |
| SHT-12 | reviewed_invariant | Each audience-visibility fact binds its exact source, carrier, permission, trigger, and protection method; framing neither reveals that fact early nor hides the carrier this shot must communicate. |
| SHT-13 | reviewed_invariant | Multi-character blocking projects sourced, directed relationships into compatible positions, gaze, distance, and action lines for the current boundary. |
| SHT-14 | reviewed_invariant | A contested moving object preserves ownership, trajectory, direction, time/round state, and end location across cuts unless an authorized ellipsis says otherwise. |
| SHT-15 | reviewed_invariant | When the creator has declared delivery-surface overlay regions with their permanence and source, what a shot must be read for—face and gaze, readable evidence text, the decisive hand action—does not sit only inside those regions, and shots bind the declared version. An undeclared surface leaves the rule inactive: record it as unresolved and do not restage against a guessed region. |
| SHT-16 | structural_invariant | Coverage carries an episode duration total that is the arithmetic sum of its shots' accepted `duration_seconds`; every shot the coverage lists either contributes a number or is named in `unresolved_durations`, so no shot leaves the total silently. When the project declares a target per episode, the record binds that field and states the signed delta; the delta is reported to the creator and never blocks on its own. |
| SHT-17 | structural_invariant | A keyframe declares which boundary it freezes and binds that shot's matching boundary field. An end keyframe is a projection of `end_boundary`, never a second end-state authority, and per-shot keyframe count stays open: one start frame by default, an end frame only when the delivery workflow consumes it. Handing over a start/end pair delegates the motion between them to interpolation, so an action the shot exists for cannot rest on that gap alone. |
| SHT-18 | craft_default | For a scene where directing choice materially changes audience knowledge, alignment, spatial pressure, performance ownership, or the landing, an accepted scene visual plan may bridge project direction and shots; it binds exact screenplay blocks, direction/profile, Location/View and relevant asset states, ordinary scenes skip it, and it never owns screenplay facts or shot boundaries. |
| SHT-19 | reviewed_invariant | When a coverage audition is used, its approaches genuinely differ by knowledge timing, alignment, performance space, strongest image, landing, losses, or production fit; it uses no fixed option, grid, framing, or shot-count formula, and an independent creator acceptance record names the exact audition record and an existing selected approach before the formal plan or shots. |
| SHT-20 | reviewed_invariant | Shot revision identity follows directing responsibility rather than array position or text similarity: reorder preserves IDs, insertion creates one, split/merge retires replaced IDs and creates successors, and active coverage plus downstream refs are reconciled before delivery. |
| SHT-21 | reviewed_invariant | A keyframe's delivery text carries only what will be filmed: record and rule IDs, lifecycle status words, hashes, field paths, reference filenames, craft notes, and run-on negative lists stay in the spec fields. Two keyframes in one episode whose delivery text differs only by their identifiers are a template, not two frames. The suite runs no mechanical check; the reviewer cites the text against this rule. Same obligation as `VID-22` in the video-prompts stage. |

### `CON`

| ID | Class | Knowledge |
|---|---|---|
| CON-01 | structural_invariant | Linked end and next start states match or have an explicit owner revision. |
| CON-02 | reviewed_invariant | Knowledge, injury, ownership, weather, light, or physical state does not teleport/regress without story cause. |
| CON-03 | craft_default | Track downstream-relevant deltas, not the whole 设定集 in every shot. |
| CON-04 | structural_invariant | A delta records before, after, cause/source, effective range, and affected bindings. |
| CON-05 | taste_option | Declared montage, ellipsis, dream, or subjective imagery may intentionally break ordinary continuity. |
| CON-06 | structural_invariant | A delta's affected refs cover all existing consumers; future consumers remain locators until materialized. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
