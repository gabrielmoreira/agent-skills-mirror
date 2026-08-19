# 审查阶段契约

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

- **本阶段拥有**：审查问题、审查结论与修订请求；证据指向被审查的产物与其中的准确记录。
- **本阶段继承**：精确的 artifact 引用、已接受限制与创作者覆盖。
- **本阶段不越权**：不修改负责人的来源文件，不用个人偏好替代证据，也不把 owner 修订动作
  冒充审查动作。Self-review may record any evidence-supported verdict when it is labeled honestly.
  Prefer an uninvolved reviewer to reduce confirmation bias, but never retry isolation as a completion strategy.

## 制作形态需要什么

视觉风格不是贴在提示词前面的标签。创作者已接受的视觉方向与制作形态由项目层决定并传入，
**本技能不加载形态卡，也不自行选择形态**；本节只说明本阶段需要形态回答什么、以及拿到
答案后投影成哪些字段。

形态决定属于 `craft_default`：创作者说明理由即可覆盖。形态不能创造新的
`structural_invariant`，也不能改写身份、地理、持物归属与可读文字政策。审查者不得单凭
形态偏好阻断交付。

不要用“加一句风格前缀”处理形态差异。前缀只改变检索标签；形态改变的是**必须出现和
可以省略的字段**，只有后者会被执行，也只有后者能被审查。

本阶段对形态只问一件事：**叙事职责是否真的落到了本形态可执行的字段**——形、层、
材质、光、动作或声音。

检查时不问“有没有写风格名”，而问：连续性必带项是否按本形态取舍、而不是照抄别的形态；
同一决定是否只由一个负责人写入。已选择的形态或单镜预算不可执行时，回到对应负责人请求
批准，不把拆镜或换形态默认为已经授权的替代。

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

### `REV`

| ID | Class | Knowledge |
|---|---|---|
| REV-01 | structural_invariant | Run mechanical checks before spending creative review attention. |
| REV-02 | structural_invariant | A finding binds its target through the file's `sources` declaration (`src` plus record), and includes evidence, impact, required fix, owner, severity, and status. |
| REV-03 | reviewed_invariant | Semantic invention cites the source fact and conflicting downstream fact. |
| REV-04 | craft_default | Prefer a reviewer who did not author the current targets; disclose self-review, and keep reviewer findings separate from owner edits. |
| REV-05 | craft_default | Diagnose repeated structure or generic language with location and impact; do not label output merely "AI-ish". |
| REV-06 | taste_option | Alternatives remain notes unless they violate an accepted creator constraint. |
| REV-07 | structural_invariant | An end-to-end drafting request cannot impersonate creator acceptance; preview chains remain provisional and undeliverable. |
| REV-08 | craft_default | When authorized text notes report production defects, trace text/subtitle residue, music-boundary violations, wardrobe drift, axis breaks, or lip-sync mismatch to the exact prompt/spec text and keep unobserved outcomes unknown. |
| REV-09 | reviewed_invariant | After prompt revision or repackaging, recheck source coverage and every applicable accepted directive; correct asset bindings alone do not prove compliance. |
| REV-10 | reviewed_invariant | A project-calibration finding distinguishes input-reference from generated-result observation, binds the exact project, the prompt/spec records it observed, stable reference slots, production configuration, method and limits, and—when its disposition calls for a change (see REV-11)—proposes the smallest owner-routed one with a preserve set; it does not generalize across projects or infer quality from task state. |
| REV-11 | reviewed_invariant | A calibration finding carries `disposition` (keep, post_production, targeted_edit, resubmit, rewrite) and `disposition_rationale` before any revision text, justified by whether the defect is text-controllable and whether it has already recurred. Dispositions that call for no change leave `required_change` empty rather than inventing one. Resubmitting identical text and appending quality adjectives are not repairs; a recurring defect routes to a structural change instead. Findings outside project calibration use `not_applicable`. |

规则分级由高到低：`structural_invariant`（结构缺陷，阻断）、
`reviewed_invariant`（需证据判断）、`craft_default`（常用做法，可覆盖）、
`taste_option`（创作者选择，不作缺陷）。创作者已接受的事实优先于本表。
