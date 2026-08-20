# 资产阶段契约

## 目录

- [独立运行与项目集成](#独立运行与项目集成)
- [所有权边界](#所有权边界)
- [跨产物引用](#跨产物引用)
- [制作形态需要什么](#制作形态需要什么)
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

- **本阶段拥有**：人物/地点/道具的身份与变体；资产状态变化记录与场景/单集资产台账；
  出现证据的提取。
- **本阶段继承**：剧本给出的身份、地理与文字政策；故事状态条目是开发/剧本的只读投影。
- **本阶段不越权**：不决定镜头构图与动作终态，不改写剧情事实。台账里的故事状态只带来源
  指针，不构成第二个取值权威。

## 跨产物引用

引用回答一个问题：**这份产物是从哪些产物做出来的**。

`sources` 只记录**派生来源**——本文件的内容依赖它、它变了本文件就可能要重做的那些产物。
同层产物互相指名不是派生：occurrence 可以指向它喂给的 decision，那个 decision 也指回它
消费的 occurrence，两者都成立，但只有后者是派生。**只有派生关系必须无环**，互相指名不受
此限。把非派生的指名写进 `sources`，会让派生图出现假环，也会让「上游变了要重做什么」这个
问题答不准。

同一个上游被一个文件反复引用时，在开头声明一次，之后每条引用只写快照键和记录 ID。
声明本身也占篇幅，所以只被引用一两次的上游直接把 `owner`、`artifact` 写在那条引用里。

`.jsonl` 的第一行是声明记录：

```json
{"record_type":"sources","schema_version":"1.0.0","sources":{"screenplay-index":{"owner":"short-drama-write","artifact":"剧集/EP003/screenplay-index.jsonl"},"characters":{"owner":"short-drama-assets","artifact":"设定集/characters.jsonl"}}}
```

`.json` 用顶层 `"sources"` 对象，条目形状相同。

条目只有 `owner` 与 `artifact`：**引用指名产物，不携带产物的字节**。产物里不写任何哈希——
写在引用里的哈希要手工维护，而从来没有任何校验器比对过它。真正在比对字节的只剩生命周期
状态与交付包校验和，那两处由工具自己维护、会真的重算。

`sources` 的键短、小写，由产物文件名派生（`characters`、`looks`、`locations`、
`location-views`、`props`、`prop-states`、`occurrences`、`screenplay-index`），在本文件内
唯一且稳定。

引用写成：

```json
{"src":"characters","record_id":"CHAR-GUHE"}
```

指向记录中某个字段时加 `field`（JSON pointer）；引用方需要区分权威等级时加 `authority`
（`accepted` / `candidate`），它属于这一条引用，不属于来源声明。指向整份产物或产物级字段时
省略 `record_id`。

产物存在不等于它里面有你指的那个东西，所以这两件事分两处判：

- **同时拿到引用方与被引用文件时，`record_id` 由检查器当场解析**。资产检查器同时读
  `characters.jsonl` 与 `looks.jsonl`，所以外观指向不存在的角色会被它直接报出来。
- **跨文件的 `field` pointer 由仓库层的 `tests/test_reference_integrity.py` 判定**，
  它把随发布的模板与一个完整项目里的每条指针都走到底。检查器只拿到命令行给它的那几个
  文件，指向没拿到的文件时它无从解析——这一点此前写成了「都会被检查」。

## 制作形态需要什么

视觉风格不是贴在提示词前面的标签。创作者已接受的视觉方向与制作形态由项目层决定并传入，
**本技能不加载形态卡，也不自行选择形态**；本节只说明本阶段需要形态回答什么、以及拿到
答案后投影成哪些字段。

形态决定属于 `craft_default`：创作者说明理由即可覆盖。形态不能创造新的
`structural_invariant`，也不能改写身份、地理、持物归属与可读文字政策。审查者不得单凭
形态偏好阻断交付。

不要用“加一句风格前缀”处理形态差异。前缀只改变检索标签；形态改变的是**必须出现和
可以省略的字段**，只有后者会被执行，也只有后者能被审查。

本阶段要向形态决定问四件事：

- **身份锚点载体**：靠什么让人物跨镜可辨认——轮廓、线条、比例、结构差异还是材质。
- **层级拆分**：身份层、环境层、可动层、效果层各包含什么，同一事实由谁负责。
- **材质与光色**：材料怎样响应光，色彩关系承担什么信息；不罗列质量词。
- **连续性必带项**：本形态下哪些字段必须逐镜传递、哪些可以省。不同形态答案差别很大，
  不要照抄别的形态的必带串。

本阶段新增：轮廓、材料、层拆、稳定比例与版本差异。

## 本阶段规则

### `AST`

| ID | Class | Knowledge |
|---|---|---|
| AST-01 | structural_invariant | Extract occurrences with a declared source snapshot and block ID before creating or binding an asset. |
| AST-02 | reviewed_invariant | Reconcile each occurrence as reuse, new identity, new variant, or unresolved—never guess an ambiguous name/pronoun. |
| AST-03 | craft_default | Separate Character/Look, Location/View, and Prop/State. |
| AST-04 | reviewed_invariant | Persistent identifying anchors and mutable state are not mixed. |
| AST-05 | structural_invariant | Every downstream binding resolves to an accepted identity and valid variant. |
| AST-06 | craft_default | Track only asset facts needed for recognition, reuse, prompt writing, or continuity. |
| AST-07 | reviewed_invariant | Persistent voice identity and pronunciation refs stay separate from scene-level breath, emotion, volume, and delivery state. |
| AST-08 | reviewed_invariant | A voice reference binding states what it controls and what it must not; the take's emotion, its recording space, and its background never enter identity. |
| AST-09 | reviewed_invariant | A claim about what is audible in a reference requires a creator or rights-holder description, or an authorized listening observation bound to the inspected bytes; otherwise admission stays unverified. |
| AST-10 | structural_invariant | An accepted pronunciation of a proper noun appears in exactly one spelling across the 设定集. |
| AST-11 | reviewed_invariant | Characters designed together are not bound to confusable references; each names the audible trait telling it apart from its nearest neighbour, and names that character. |
| AST-12 | craft_default | Selection criteria are few, audible and counter-exampled; they judge a candidate reference or a clone result, they do not stand in for one. |

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
