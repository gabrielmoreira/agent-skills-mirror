# 视频提示词阶段契约

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

- **本阶段拥有**：运动顺序、表演路径、摄影与声音的实现；交付容器的成员、顺序与容器时长。
  成员的已接受时长是分镜的只读投影，容器时长等于它们之和。
- **本阶段继承**：镜头目的、起止边界、已接受时长、形态运动预算、逐字对白。
- **本阶段不越权**：不回写镜头或资产权威；结束报告只用于比较，不是第二个终点取值权威。
  需要改时长、终点、对白或下一镜开场时，发修订请求给对应负责人。

## 制作形态需要什么

视觉风格不是贴在提示词前面的标签。创作者已接受的视觉方向与制作形态由项目层决定并传入，
**本技能不加载形态卡，也不自行选择形态**；本节只说明本阶段需要形态回答什么、以及拿到
答案后投影成哪些字段。

形态决定属于 `craft_default`：创作者说明理由即可覆盖。形态不能创造新的
`structural_invariant`，也不能改写身份、地理、持物归属与可读文字政策。审查者不得单凭
形态偏好阻断交付。

不要用“加一句风格前缀”处理形态差异。前缀只改变检索标签；形态改变的是**必须出现和
可以省略的字段**，只有后者会被执行，也只有后者能被审查。

本阶段要向形态决定问：**运动层、接触、节奏、声源与结果**在本形态下怎么写。

运动段的默认值随形态改变（默认全动作 / 默认保持姿态并声明例外 / 一镜一因果 / 把全动作
预算集中给情绪转折镜）。拿到形态运动预算后，本阶段只负责把它落成有因果顺序的动作与
可比较的终点，不重新选择形态。

本阶段新增：运动层、接触、节奏、声源与结果。

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

### `VID`

| ID | Class | Knowledge |
|---|---|---|
| VID-01 | structural_invariant | Motion reads but cannot rewrite shot start/end/duration/dialogue and next-shot state. |
| VID-02 | craft_default | Write start anchor, ordered subject motion, camera behavior, timing, and end report; add performance change and environment/audio only when this shot actually carries them. |
| VID-03 | craft_default | When a reference frame carries appearance/composition, focus prose on change instead of repeating the 设定集. |
| VID-04 | structural_invariant | Explicit segment timing sums exactly to its shot's accepted duration—neither exceeding it nor leaving an unallocated remainder. |
| VID-05 | reviewed_invariant | Untimed action load must be feasible enough to preserve the intended performance and story change. |
| VID-06 | structural_invariant | Locked and moving camera instructions cannot govern the same interval without an explicit transition. |
| VID-07 | taste_option | Camera may be locked or moving; audio/lip-sync detail follows the chosen production profile. |
| VID-08 | reviewed_invariant | Structured motion names this shot's exact subjects, actions, contacts, and results rather than reusable placeholders; when a performance path is present, it names only the actors and visible changes this shot actually carries. |
| VID-09 | structural_invariant | Next-start is an existing canonical ref whose `src` resolves through the file's `sources` declaration, or an explicit provisional locator; never an invented record, source key, or hash. |
| VID-10 | craft_default | Resolve one accepted production profile for the current delivery scope; local variants may coexist when their range and precedence are explicit, without overriding source coverage or exact-readable obligations. |
| VID-11 | reviewed_invariant | A selective transform names its trigger, exact target scope, end geometry/state, and preserve set so non-target people, props, text surfaces, and spatial anchors do not change with it. |
| VID-12 | reviewed_invariant | A pickup/alternate names stable master/supplement motion IDs and maps each source requirement to a field or disposition; motion may request replacement, but only a downstream independent verdict can approve it. |
| VID-13 | structural_invariant | A delivery container carries one or more accepted shots that are contiguous in source order, share one accepted geography/asset binding chain, and do not cross a scene boundary—a Location/View change ends the container. Its duration equals the sum of their accepted durations, and packing changes neither shot boundaries nor per-shot reviewability. |
| VID-14 | craft_default | Music intent may be annotated per shot as a relative entry/exit/duck against neighbours, but its realization belongs to the timeline layer; no deliverable—single-shot or multi-shot container—carries a baked-in music bed unless the project accepted otherwise or the source is diegetic. Dialogue, off-screen sources, ambience, and event effects stay with the deliverable. |
| VID-15 | structural_invariant | Within one episode a shot belongs to at most one container, so container durations sum without double-billing. Containers need not cover every shot, but the containers plus the shots left loose must account for the episode's shot set exactly once; an unaccounted or twice-counted shot is a defect, not a packing preference. |
| VID-16 | reviewed_invariant | When performance changes, multi-character motion differentiates the actors who actually carry it and keeps each chosen signal readable in the accepted framing; it does not require an arc for non-performing shots, force every craft field, or duplicate one emotion across the cast. |
| VID-17 | reviewed_invariant | Every multi-reference binding carries a stable `slot_id` and explicit unique `order`, so array reordering or insertion cannot silently change a reference's role; until a project validator owns this check, the reviewer cites conflicting slots/orders rather than claiming mechanical enforcement. |
| VID-18 | reviewed_invariant | Per-shot text readiness is a scope-aware review/status projection derived from current accepted refs and real blocking gaps, not a persisted motion fact. A missing input blocks only dependent claims; overall delivery-ready requires all applicable scopes. Readiness never claims generated identity, performance, lip-sync, mix, edit, or market quality. |
| VID-19 | reviewed_invariant | When the creator profile declares required literal tokens for a delivery route, that route's delivery text preserves them byte-for-byte and outside the verbatim-dialogue fence. Paraphrase, translation, reordering, or omission is treated as a defect because a literal-matching surface has no reason to reject the rewritten text—the failure is silent rather than reported. The suite asserts no specific surface's behaviour, and whether a given result took the route is returned adherence, provable only by a bound production observation. Tokens declare a route and never substitute for the start state, action, or endpoint. Absent a declared token list the suite invents none; until the profile exposes a machine-readable list at a pinned field path, the reviewer cites the profile against the delivery text rather than claiming mechanical enforcement. |
| VID-20 | reviewed_invariant | Packing routes change delivery granularity only, leaving shot boundaries, shot purpose, and per-shot reviewability intact. A single long-form generation carrying several accepted shots *is* a multi-shot container and is billed under VID-13 and VID-15; it introduces no separate accounting and no exemption from the contiguity, binding-chain, and scene-boundary constraints. A continuation route instead starts from a previously generated result, which is observation evidence and not an accepted artifact: the accepted shot start boundary stays the sole authority, and any claim about the observed state binds a production observation record or remains `unverified`. |
| VID-21 | craft_default | When the project's accepted production profile has generated imagery carry the frame, actions are written as high-frequency, whole-body or single-limb movements common in everyday footage; precise interception, invisible internal states, negative actions, and three-or-more-step two-handed choreography are rewritten into equivalent common-action combinations, with the dramatic information carried by combination and timing. The rule is inactive for live action or an undeclared profile, and a rewrite may never change accepted shot boundaries, terminal states, or screenplay fact. |
| VID-22 | reviewed_invariant | Delivery text carries only what will be filmed. Record and rule IDs, lifecycle status words, hashes, field paths, reference filenames, craft notes, and run-on negative lists stay in the spec fields and review records; the delivery text takes their result — a negative intent rewritten as a positive state, a reference constraint rewritten as a visible fact. A prompt that recites its own constraints reads as complete and renders as nothing. Until a project validator owns this check, the reviewer cites the delivery text against this rule rather than claiming mechanical enforcement. |

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
