# 图片提示词阶段契约

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

- **本阶段拥有**：资产图片的构图与定点修改选择；渲染出的提示词文本是缓存。
- **本阶段继承**：已接受的资产身份与变体、当前用途、文字政策。
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
- **母版、补拍与替代**：补拍默认只补充、不替代母版。声明 `master | pickup | alternate`，
  用同一文件内稳定的记录 ID 说明母版与补充关系，并把每项原文要求对应到当前字段或说明
  去向。只有下游独立审查结论才能绑定固定 hash 并批准替代，不得回写形成循环引用。

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

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
