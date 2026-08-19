# 图片提示词阶段契约

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

- **本阶段拥有**：项目级 lookdev 风格帧、资产图片的构图与定点修改选择；渲染出的提示词文本是缓存。
- **本阶段继承**：已接受的视觉方向与制作配置、资产身份与变体、当前用途、文字政策；高压力
  lookdev frame 还继承准确剧本 block 的场次事实与信息权限。
- **本阶段不越权**：不承载有先后顺序的剧情动作，不改写资产身份、地理或故事状态，不决定
  镜头边界。

## 制作形态需要什么

视觉风格不是贴在提示词前面的标签。创作者已接受的视觉方向与制作形态由项目层决定并传入，
**本技能不加载形态卡，也不自行选择形态**；本节只说明本阶段需要形态回答什么、以及拿到
答案后投影成哪些字段。

形态决定属于 `craft_default`：创作者说明理由即可覆盖。形态不能创造新的
`structural_invariant`，也不能改写身份、地理、持物归属与可读文字政策。审查者不得单凭
形态偏好阻断交付。

不要用“加一句风格前缀”处理形态差异。前缀只改变检索标签；形态改变的是**必须出现和
可以省略的字段**，只有后者会被执行，也只有后者能被审查。

本阶段要向形态决定问：单帧上**形、材质、层次、光色**各自怎么表达身份与状态。

身份段的载体随形态改变写法：实拍写造型状态而不是长相；二维写剪影与色块；三维写比例与
姿态边界；水墨写不可散的边缘；Q 版写头身比与放大记号；强精修画风必须**对比着写**同剧
其他角色的结构差异，否则角色会被拉平。

本阶段新增：单帧可见的形/材质/层次/光色投影。

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

### `IMG`

| ID | Class | Knowledge |
|---|---|---|
| IMG-01 | structural_invariant | Prompt specs bind exact accepted asset and variant IDs. |
| IMG-02 | craft_default | Put distinguishing identity, geometry, scale, or state before generic quality language. |
| IMG-03 | reviewed_invariant | Character sheets preserve identity while depicting one coherent Look. |
| IMG-04 | reviewed_invariant | Location plates preserve geography, orientation, anchors, material, and light, normally without cast. |
| IMG-05 | reviewed_invariant | Prop plates preserve scale, shape, material, wear, function, and text policy. |
| IMG-06 | structural_invariant | Edit prompts declare exact target, changes, preserve set, and expected continuity impact. |
| IMG-07 | structural_invariant | Readable text cannot coexist with a global no-text constraint. |
| IMG-08 | reviewed_invariant | A claim about reference pixels requires a creator/reference-owner description or authorized input-reference observation bound to the inspected bytes; otherwise admission stays unresolved, and a negative prompt cannot stand in for evidence. |
| IMG-09 | reviewed_invariant | Each reference states its purpose, what may be copied, and what must not be copied; a composition-, scale-, or effect-only reference cannot redefine identity, content, text, or story state. |
| IMG-10 | reviewed_invariant | Views of one Location in the same time/weather state share key-light source, colour-temperature relation, and contrast direction; any difference cites a recorded cause and its delta. |
| IMG-11 | reviewed_invariant | A lookdev frame binds accepted visual direction and production profile across a declared character-expression, core-location, or high-pressure test axis; a high-pressure frame also binds exact screenplay blocks for story state and information permission, while style references may control only declared surface treatment and never identity, fixed geography, story state, cast count, or prop text. |
| IMG-12 | reviewed_invariant | Every multi-reference binding carries a stable `slot_id` and explicit unique `order`, so array reordering or insertion cannot silently change a reference's role; until a project validator owns this check, the reviewer cites conflicting slots/orders rather than claiming mechanical enforcement. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
