# 视频提示词阶段契约

## 目录

- [运行时预检](#运行时预检)
- [所有权边界](#所有权边界)
- [制作形态需要什么](#制作形态需要什么)
- [参考媒体与补拍](#参考媒体与补拍)
- [本阶段规则](#本阶段规则)

本文件是本技能的自包含契约：预检、所有权、形态输入与规则表都在这里，
不需要读取其他技能的文件。

## 运行时预检

进入本阶段前先完成这套轻量预检。它只检查安装完整性、项目事务状态和已记录的精确引用，
不评价创作内容。

1. **验证安装**：从本技能目录的 `suite-ref.json` 解析到逻辑安装路径中的 core，用当前
   环境可用的 Python 3 解释器运行 core 的 `scripts/suite_verify.py`。验证器沿逻辑安装
   路径逐一检查清单中的技能；混装、缺件、额外可执行文件或 hash 不一致时停止写入，
   也不要退回源码检出目录“借用”通过验证的兄弟技能。
2. **先恢复事务，再读状态**：定位项目根目录后，先运行 core 的 `scripts/project_tool.py`
   的 `recover`，再运行 `status`。`recover` 可重复执行；它报告 blocked 时保持创作者文件
   原样并先处理冲突，不要绕过 WAL、手改状态文件或假定上次写入成功。`status` 中的
   accepted/candidate 指针和阻断项是本阶段工作的当前事实。
3. **只通过公开生命周期写入**：负责人用 `publish` 原子发布候选，并给每个外部结构化引用
   提供精确 input hash。上游接受引用不继承候选状态。创作者接受、独立审查与内容修订是
   不同动作。每次修订后重新运行适用的结构校验，并让下游刷新旧 hash。打包是最终交付闸门，
   不是接受或审查命令；仍有阻断项时不打包。
4. **读共享 JSON/JSONL 时同时声明读了哪几条记录**：`bible/*.jsonl` 与项目文件是全项目
   共享输入，只按整文件 hash 绑定会让后续任何一次增补把此前引用过它的产物全部标为
   `stale`。发布时对这类输入补 `--input-record <path>=<selector>`（JSONL 用记录 ID，
   JSON 用 RFC 6901 指针，每条一次），此后只有被绑定的记录变化才会影响本产物。
   Markdown 没有可机器校验的记录身份，仍按整文件绑定。

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
- **母版、补拍与替代**：补拍默认只补充、不替代母版。声明 `master | pickup | alternate`，
  用同一文件内稳定的记录 ID 说明母版与补充关系，并把每项原文要求对应到当前字段或说明
  去向。只有下游独立审查结论才能绑定固定 hash 并批准替代，不得回写形成循环引用。

## 本阶段规则

### `VID`

| ID | Class | Knowledge |
|---|---|---|
| VID-01 | structural_invariant | Motion reads but cannot rewrite shot start/end/duration/dialogue and next-shot state. |
| VID-02 | craft_default | Write start anchor, ordered subject motion, performance change, camera behavior, environment/audio, timing, and end report. |
| VID-03 | craft_default | When a reference frame carries appearance/composition, focus prose on change instead of repeating the bible. |
| VID-04 | structural_invariant | Explicit segment timing sums exactly to its shot's accepted duration—neither exceeding it nor leaving an unallocated remainder. |
| VID-05 | reviewed_invariant | Untimed action load must be feasible enough to preserve the intended performance and story change. |
| VID-06 | structural_invariant | Locked and moving camera instructions cannot govern the same interval without an explicit transition. |
| VID-07 | taste_option | Camera may be locked or moving; audio/lip-sync detail follows the chosen production profile. |
| VID-08 | reviewed_invariant | Structured motion names this shot's exact actor, action, contact, performance path, and result rather than reusable placeholders. |
| VID-09 | structural_invariant | Next-start is an existing canonical ref or an explicit provisional locator, never an invented record/hash. |
| VID-10 | craft_default | Resolve one accepted production profile for the current delivery scope; local variants may coexist when their range and precedence are explicit, without overriding source coverage or exact-readable obligations. |
| VID-11 | reviewed_invariant | A selective transform names its trigger, exact target scope, end geometry/state, and preserve set so non-target people, props, text surfaces, and spatial anchors do not change with it. |
| VID-12 | reviewed_invariant | A pickup/alternate names stable master/supplement motion IDs and maps each source requirement to a field or disposition; motion may request replacement, but only a downstream independent verdict can bind fixed hashes and approve it. |
| VID-13 | structural_invariant | A delivery container carries one or more accepted shots that are contiguous in source order, share one accepted geography/asset binding chain, and do not cross a scene boundary—a Location/View change ends the container. Its duration equals the sum of their accepted durations, and packing changes neither shot boundaries nor per-shot reviewability. |
| VID-14 | craft_default | Music intent may be annotated per shot as a relative entry/exit/duck against neighbours, but its realization belongs to the timeline layer; no deliverable—single-shot or multi-shot container—carries a baked-in music bed unless the project accepted otherwise or the source is diegetic. Dialogue, off-screen sources, ambience, and event effects stay with the deliverable. |
| VID-15 | structural_invariant | Within one episode a shot belongs to at most one container, so container durations sum without double-billing. Containers need not cover every shot, but the containers plus the shots left loose must account for the episode's shot set exactly once; an unaccounted or twice-counted shot is a defect, not a packing preference. |

### `CON`

| ID | Class | Knowledge |
|---|---|---|
| CON-01 | structural_invariant | Linked end and next start states match or have an explicit owner revision. |
| CON-02 | reviewed_invariant | Knowledge, injury, ownership, weather, light, or physical state does not teleport/regress without story cause. |
| CON-03 | craft_default | Track downstream-relevant deltas, not the whole bible in every shot. |
| CON-04 | structural_invariant | A delta records before, after, cause/source, effective range, and affected bindings. |
| CON-05 | taste_option | Declared montage, ellipsis, dream, or subjective imagery may intentionally break ordinary continuity. |
| CON-06 | structural_invariant | A delta's affected refs cover all existing consumers; future consumers remain locators until materialized. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
