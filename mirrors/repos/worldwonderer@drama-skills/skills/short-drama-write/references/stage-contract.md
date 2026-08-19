# 剧本阶段契约

## 目录

- [独立运行与项目集成](#独立运行与项目集成)
- [所有权边界](#所有权边界)
- [单集契约与题材边界](#单集契约与题材边界上游输入)
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

- **本阶段拥有**：场景执行计划、节拍、剧本正文；场景/动作/对白/生产标签；已实现的
  知识、信念、目标、关系与情绪变化；块 ID、类型与跨度。
- **本阶段继承**：已接受的单集契约与已接受事实。开发环节拥有已规划契约时，本阶段只投影
  它、不复制它；没有开发环节记录时，本阶段可拥有独立单集契约，后续若引入开发记录须显式
  迁移权威。
- **本阶段不越权**：不决定景别、机位与镜头时长，不建立或改写资产身份与变体，不指定提示词
  构成。需要这些变化时发修订请求。

## 单集契约与题材边界（上游输入）

本阶段执行的是**已接受的单集契约**，不重新设计分集，也不给项目归类题材。下面写清这两样
东西进入本阶段时必须包含什么、缺失时怎么办——写作时按这份清单核对即可，不去读开发环节
的文件。

### 单集契约必须提供的字段

| 字段 | 本阶段拿它做什么 | 缺失时 |
|---|---|---|
| 进入状态 | 首场从哪个已经成立的处境开始 | 向 develop owner 发修订请求 |
| 当集追求与阻力 | 每场的议程与反对力量从哪来 | 同上；不自行发明动机 |
| 因果升级 | 哪几步必须在本集内被看见 | 同上 |
| 方向性转折 | 哪一次选择改变了局面 | 同上 |
| 当集兑现 | 集尾钩子之前必须落地的局部结果 | 同上 |
| 出去的压力与交接事实 | 末场留下什么、下一集要继承什么 | 同上 |
| 信息权限 | 谁知道什么、观众知道什么 | 同上 |

本阶段只把这些字段**落实成可表演的场景**：补场景发动机、节拍顺序、对白策略与生产标签。
不得在剧本里改写契约字段——需要改就发修订请求，不在执行层偷改。

### `write_standalone`：没有开发记录时

项目没有 develop 拥有的单集契约时，本阶段可以自己拥有一份独立契约，但它必须包含上表
同样的字段，并明确标为 standalone。后续若引入 develop 记录，先做语义 diff，让创作者明确
选择权威迁移，把 standalone 契约标记 superseded，再换成指针；同一集不得同时激活两种模式。

### 题材：本阶段执行，不分类

题材机制会影响压力来源、可用证据、场面颗粒与集尾取向，但**选择哪个题材、用哪套钩子取向
属于开发阶段**。本阶段的做法是：

- 已有已接受的题材与钩子取向时，按它执行，并以单集契约为准；
- 没有已接受取向时（例如从想法直接写作），**不要贴题材标签给自己造公式**。改为向创作者
  确认本集要兑现什么承诺、观众该获得什么回报，然后按第 5 节的叙事工艺决策规则写；
- 任何情况下都不把题材词直接当成剧情答案，也不因为"这个题材通常这样"就新增契约里没有的
  事件、人物或代价。

## 本阶段规则

### `SCR`

| ID | Class | Knowledge |
|---|---|---|
| SCR-01 | reviewed_invariant | Every scene has a current agenda, opposing force, directional turn, and exit state. |
| SCR-02 | craft_default | Prefer choices and consequences over coincidence for major turns. |
| SCR-03 | reviewed_invariant | Private thought is expressed through behavior, evidence, or deliberate VO/OS. |
| SCR-04 | craft_default | Dialogue carries agenda, relationship, subtext, and a change—not only information. |
| SCR-05 | structural_invariant | Existing production tags use supported, closed syntax and resolvable references. |
| SCR-06 | taste_option | Silence, slang, interruption, narration, and sentence rhythm remain character/style choices. |
| SCR-07 | reviewed_invariant | Story-critical text, VO/OS, SFX, transition, and continuity requirements are not left indistinguishable from ordinary prose. |
| SCR-08 | craft_default | When abstract emotion obscures performance, translate it into character-specific behavior, object handling, distance, silence, or delivery. Dialogue turn length and tactic follow the scene agenda rather than a universal attack-defense cadence. |
| SCR-09 | craft_default | Break a long speech with a visible action beat that changes the speaker's tactic, giving downstream a sourced cut point and the performance a breath; a speech with no internal turn is shortened rather than split. |
| SCR-10 | reviewed_invariant | When the creator marks a beat's realization as replaceable under later pressure, the record separates the dramatic function from the current depiction and names a fallback depiction that delivers the same function: same person proven or changed, downstream payoff refs and next-episode entry state still satisfied, cost not erased, no new setup required. Deleting the beat is never a fallback. An unmarked beat leaves the rule inactive—the suite carries no platform standard, predicts no outcome, and pre-emptive sanding is the more expensive mistake. |
| SCR-11 | craft_default | When sound carries story information, spatial pressure, off-screen presence, a deliberate silence, or a scene bridge, the screenplay identifies the necessary source/event and its dramatic target; it does not prescribe per-shot mixing, add decorative sound to every scene, or use music to replace performance. |
| SCR-12 | craft_default | A crowded scene first makes clear who is contending with whom—by cutting non-essential presence, staggering entrances, splitting the scene so one opponent holds the focus at a time, or handing attention from one character to the next—rather than naming every present character in action paragraphs. Deliberately chaotic ritual, siege, or farce may override this once the disorder is a visible choice and one followable thread remains. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
