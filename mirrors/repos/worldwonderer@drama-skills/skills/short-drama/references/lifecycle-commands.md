# 项目命令

从 `short-drama` 技能安装目录运行，不依赖当前工作目录：

```text
python3 <core>/scripts/project_tool.py init <project> --title <title>
python3 <core>/scripts/project_tool.py status <project>
python3 <core>/scripts/project_tool.py publish <project> --owner short-drama-write --artifact-id EP001:script --output 剧集/EP001/screenplay.md=_work/screenplay.next.md --input 项目开发/episode-map.jsonl
python3 <core>/scripts/project_tool.py accept <project> --artifact-id EP001:script --decision accepted [--note <note>]
python3 <core>/scripts/project_tool.py review <project> --artifact-id EP001:script --verdict approve [--reviewer <label>] [--note <note>]
python3 <core>/scripts/project_tool.py set-authority <project> --field /creator_authority/production_profile --decision-ref 创作者决策/decisions.jsonl#CD-PROFILE-001
python3 <core>/scripts/project_tool.py package <project> --episode EP001 --include 剧集/EP001/screenplay.md [--omit <path>=<reason>]
python3 <core>/scripts/project_tool.py verify <project> --episode EP001
```

## 发布

`publish --output <target>=<source>` 可重复。source 必须是项目内安全的 UTF-8 Markdown、
JSON 或 JSONL；命令先验证全部 source，再逐文件用临时文件和原子替换发布。每个 artifact 的
output 路径只能有一个 owner。

`--input <path>` 只声明该产物实际读取的直接项目文件。工具内部保存当前摘要，用于之后判断
`update_needed`；调用者不计算、不粘贴 hash，也不声明传递依赖。若 A 直接读 B，就声明 B；
B 又读 C 不会让 A 自动过期，只有 A 下次实际重建时才读取当前 B。

**失效图就是这份清单，漏一条就是一条静默的边**：产物文件首行 `sources` 声明了什么，
`--input` 就逐个列什么。少列一个，那个上游改了它不会变 `update_needed`，会带着过期的绑定
停在 `accepted`，而这与真的还是最新的看起来完全一样。身份与变体成对出现的上游尤其容易漏
一半（`props.jsonl` 列了、`prop-states.jsonl` 没列）。各阶段的完整清单写在自己的 SKILL.md 里。

默认只允许发布到标准阶段目录。`输入/**`、`.short-drama/**`、`交付/**` 和任何
`short-drama.json` 都不可作为 publish 目标；`short-drama.json` 里的 `creator_authority/*`、
`format/target_seconds_per_episode` 与 `format/pacing` 用 `set-authority` 写。`set-authority` 只认它所引用的那一个
决策文件，同一条决策的撤回要写在同一个文件里。分集目录
使用 `EP001` 形式。未登记的临时路径必须显式加 `--allow-unregistered-path`。

发布逐个文件原子完成：进程中断最多留下未被采用的临时文件，已完成的每个目标都是完整文件。
再次运行同一条发布命令即可继续。

## 接受与复核

发布后状态是 `needs_confirmation`。创作者决定当前版本：

```text
... accept <project> --artifact-id <id> --decision accepted
... accept <project> --artifact-id <id> --decision rejected --note <reason>
```

接受不要求单独证据文件或 target hash。输出或直接输入已变化时命令拒绝沿用旧决定。

接受后可记录复核：

```text
... review <project> --artifact-id <id> --verdict approve --reviewer 同事复核
... review <project> --artifact-id <id> --verdict revise --note <bounded-fix>
```

`approve_with_notes` 也计为通过；`provisional` 保持未批准。reviewer 是创作质量实践，
不是 CLI 身份认证协议：有独立上下文时使用，没有时诚实填写自检标签。

重新 `publish` 会清除该 artifact 的旧接受与复核。`status` 在读取时检查当前输出和直接输入，
只报告 `update_needed`，不修改状态文件，也不传播或保存“下游闭包”。

## 写回创作者权威

创作者定下制作形态、视觉方向、播放面、集长目标或语速后，先把这条决定作为一条创作者决策记录
发布到 `创作者决策/` 并 `accept`，再写回 `short-drama.json`。三步都要走，缺一步 `set-authority`
会拒绝——决策文件必须先是**已发布且已接受**的产物：

```text
# 1. 写决策记录（首行 sources 声明，其后每行一条决定）
{"record_type":"sources","schema_version":"1.0.0","sources":{"short-drama":{"owner":"short-drama","artifact":"short-drama.json"}}}
{"decision_id":"CD-PACING-001","status":"accepted","accepted_value":{"spoken_characters_per_second":5.0,"seconds_per_action_paragraph":2.5},"target_locators":[{"src":"short-drama","field":"/format/pacing"}],"decided_by":"creator","decided_at":"2026-01-01T00:00:00Z"}

# 2. 发布并接受
... publish <project> --owner short-drama --artifact-id creator:decisions --output 创作者决策/decisions.jsonl=_work/decisions.jsonl
... accept <project> --artifact-id creator:decisions --decision accepted

# 3. 逐个字段写回
... set-authority <project> --field /format/pacing --decision-ref 创作者决策/decisions.jsonl#CD-PACING-001
... set-authority <project> --field /creator_authority/delivery_surface --decision-ref 创作者决策/decisions.jsonl#CD-SURFACE-001
... set-authority <project> --field /format/target_seconds_per_episode --decision-ref 创作者决策/decisions.jsonl#CD-LENGTH-001
```

`/format/pacing` 收一个速率对象（每个速率是正数），剧本与分镜两个阶段都读它折算秒数。

`status` 的 `authority` 一节逐个回报已绑定字段的现状——`set-authority` 记下了它写进去的值，
所以直接改 `short-drama.json` 会在这里显示出来：

| 取值 | 含义 |
|---|---|
| `bound` | manifest 当前值仍是那条决策写进去的值 |
| `hand_edited` | 值被 `set-authority` 之外的东西改过 |
| `missing` | manifest 里已经没有这个槽位 |
| `not_authority_field` | 绑定记录指向一个不再属于白名单的字段 |

这一节是给 CLI 与 reviewer 看的，创作台不显示它——创作台按设计过滤掉生命周期内部信息。

对象槽位（`/format/pacing`、`creator_authority` 里带 `choices` 的块）是**并入**而不是整体替换：
一条只写了一半速率的决策，另一半会保持原样，因此 `set-authority` 校验的是合并之后的结果。

`--field` 只接受 `/creator_authority/*`、`/format/target_seconds_per_episode` 与 `/format/pacing`；
`creator_authority/decisions_artifact` 是目录布局，由 `init` 定下。被引用的记录 `status`
必须是 `accepted`，`target_locators` 必须含 `{"src":"short-drama","field":"<同一 field>"}`，
命令写入它的 `accepted_value`，并只写进 manifest 已声明的槽位、保持该槽位原有的 JSON 类型。

写到 `visual_direction`、`production_profile`、`delivery_surface` 这类带 `status` 的块时，
`accepted_value` 的键并入该块的 `choices`（该块没有 `choices` 就并入块本身），`status` 置为
`accepted`。直接写 `.../choices` 同样是并入，已记下的选择不会被这次写掉；写更深的单个选择
（如 `.../choices/look_development`）会把它所在的块一并置为 `accepted`。集长目标写正数秒。
下游读到的就是这里已 `accepted` 的值。

## 打包与复核

`package` 要求每个 `--include` 都属于本集并且当前为 `approved`。它把所选文本/JSON 复制到
`交付/<EP>/artifacts/`，写入 manifest 与 checksums，并记录 `--omit` 的理由。再次打包用新目录
原子替换旧包。

`verify` 重新计算交付文件校验和，并报告缺失、篡改或未登记新增文件。校验和只服务于准确交付，
不参与创作状态或依赖传播。

## Dashboard 启动

```text
python3 <core>/scripts/dashboard_server.py --workspace <workspace> --port 0 --open
```

`--host` 只接受回环主机。服务拒绝符号链接和路径越界，使用每次启动独立的本机会话。
Dashboard 是展示与有限文本编辑层，不承担生成、接受、复核或打包编排。保存使用当前文件版本
做冲突检查；项目文件已被其他工具修改时返回冲突，不覆盖新内容。
