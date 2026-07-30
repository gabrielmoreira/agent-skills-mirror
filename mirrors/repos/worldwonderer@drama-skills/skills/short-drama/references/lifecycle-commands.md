# 项目命令与审核记录

## 目录

1. 发布与创作者确认
2. 独立审查记录
3. 过期影响与依赖检查（含把共享文件的失效半径收窄到记录）
4. 恢复与打包（含交付完整性枚举）

只在实际调用 `project_tool.py`、诊断命令失败或核对审核记录时读取本文。
从 `short-drama` 技能安装目录调用脚本，不依赖当前工作目录：

```text
python3 <short-drama-skill-dir>/scripts/project_tool.py init <project> --title <title>
python3 <short-drama-skill-dir>/scripts/project_tool.py status <project>
python3 <short-drama-skill-dir>/scripts/project_tool.py recover <project>
python3 <short-drama-skill-dir>/scripts/project_tool.py publish <project> --owner short-drama-write --artifact-id EP001:script --output episodes/EP001/screenplay.md=inputs/EP001-screenplay.candidate.md [--input <upstream-path>=<sha256> ...] [--input-record <upstream-path>=<record-id> ...]
python3 <short-drama-skill-dir>/scripts/project_tool.py accept <project> --artifact-id EP001:script --decision accepted --target episodes/EP001/screenplay.md=<candidate-sha256> --evidence-artifact creator-decisions/EP001-script.json --evidence-hash <decision-file-sha256> --evidence-record-id <decision-id>
python3 <short-drama-skill-dir>/scripts/project_tool.py review <project> --artifact-id EP001:script --verdict approve --target episodes/EP001/screenplay.md=<accepted-sha256> --verdict-owner short-drama-review --verdict-artifact reviews/EP001-verdict.json --verdict-hash <verdict-file-sha256>
python3 <short-drama-skill-dir>/scripts/project_tool.py package <project> --episode EP001 --include <accepted-path> [...] [--omit <accepted-path> ...]
```

## 发布与创作者确认

`publish --output <target>=<source>` 可以重复使用；来源文件必须是项目内的 UTF-8
Markdown、JSON 或 JSONL。命令把来源文件和 `--input` 依赖的准确路径与 `hash` 写入
预写日志，只发布 `candidate`，且只检查文件格式；`validation_state` 保持 `not_run`，不能同时写入创作者确认
或独立审查结论。

`accept` 使用创作者决定记录，把所有准确的 `candidate` 目标 `hash` 推进为
`accepted`；记录的负责人固定为 `creator`。

**决定与审查证据按产物分文件存放**：默认约定是 `creator-decisions/<artifact-id>.json`
与 `reviews/<EP>-findings.jsonl`，**一个产物一份**。原因是证据引用绑定的是**整文件
hash**：把全项目的决定追加进同一个 `creator-decisions.jsonl` 时，接受第二集会改变该
文件的 hash，于是第一集那条已经冻结的证据引用永久指向一个不再存在的字节状态。

这不会让命令报错——`package` 与 `review` 不重新校验存量引用，所以链条**看起来**是完好的。
失效是静默的：除最近一次接受外，此前每一次接受的证据都无法再被复核，而 hash 绑定的
全部意义就是可复核。工具本身不限制路径，共享单文件在只有一个产物时也能跑通；但它不是
可扩展的布局，不要用它开新项目。

JSONL 记录必须用 `--evidence-record-id` 唯一定位同名 `decision_id`；JSON 证据必须是对象；所定位记录的
`status` 或 `decision` 必须与命令的 `accepted/rejected` 一致。用于产物生命周期的记录
还必须声明 `decision_kind:"artifact_acceptance"`、当前 `artifact_id` 和与全部 `--target`
完全相同的 `target_hashes`；其他已接受决定不能代替本次接受。

## 独立审查记录

`review` 的审查结论 JSON 必须列出同一组结构化的受审 `ArtifactRef`。`reviewer` 至少包含
与审查结论负责人一致的 `owner`、`kind`、`independent:true`，并在
`excluded_owner_skills` 中准确排除被审文件的负责人。`findings_ref` 必须由审查者所有，
绑定当前有效的 `hash`，并指向可解析的 JSONL；其中所有未关闭的致命、错误或阻断问题 ID 必须与 `blocking_findings` 完全一致，
`open_blocker_count` 再与之对齐。

`structural_validation` 必须是 `pass | pass_with_warnings | fail`，并由这份准确的审查结论
更新校验状态；结构校验未通过或仍有阻断问题时不能批准。后续目标文件或任一
审核记录的 `hash` 改变，都要重新确认或审查。

## 过期影响与依赖检查

接受时把 `candidate` 的准确输入清单保存为 `accepted_inputs`。发布新 `candidate` 时，
同一预写日志清单会找出直接和间接受影响的下游文件：保留旧的创作者确认记录，
但把受影响的下游构建状态标为 `stale`，清空校验与审查就绪状态，并阻止交付。

### 把共享文件的失效半径收窄到记录

`bible/*.jsonl` 这类文件是全项目共享输入。只按整文件 `hash` 绑定时，第 48 集新增一个
配角会把此前 47 集引用过该文件的产物全部标为 `stale`——它们其实一个字都没受影响。

发布时用 `--input-record <path>=<selector>` 声明**这份候选实际读了哪几条记录**
（可重复；仍需同时用 `--input` 绑定该文件的整文件 `hash`）：

```text
--input bible/characters.jsonl=<sha256> \
--input-record bible/characters.jsonl=CHAR-GUHE \
--input-record bible/characters.jsonl=CHAR-LINYE
```

此后该文件的其余部分怎么改都不影响这份产物；只有被绑定的记录本身变化、消失或变得
不唯一时，它才会被标为 `stale`。`review` 与 `package` 的逐层复验同样改为核对这几条
记录，所以文件 `hash` 前进之后产物依然可以交付。

- **JSONL 选择器是记录 ID**：取值为某个以 `_id` 结尾的顶层字段，且在该文件中只出现
  一次。出现零次或多次一律拒绝，不做猜测。
- **JSON 选择器是 RFC 6901 指针**，例如 `/creator_authority/production_profile`。
- 记录 `hash` 按键名排序后的规范形式计算，所以重排字段或改动缩进不会误判为变化。
- **Markdown 不能做记录级绑定**：它没有可机器校验的记录身份，收窄只会变成一句无法
  验证的承诺。剧本类依赖仍按整文件绑定，需要更小半径就先拆文件。

`accepted_inputs` 中保留的整文件 `hash` 此时是**绑定当时的快照**，用于按 `hash` 取回
那一版字节；判断是否仍然有效的依据是被绑定的那几条记录。

`review` 和 `package` 会逐层复验输入的当前 `hash`、唯一且状态为 `accepted` 的提供方，
以及提供方本身的构建、确认状态和输入。外部编辑、循环或含糊依赖不能靠手改状态字符串
绕过。若多文件产物的新 `candidate` 不再包含旧的 `accepted/candidate` 目标，该路径也会
被列入受影响的下游清单；旧文件不会被静默删除，但新版本接受后，它不再拥有已接受权限，
也不能被单独打包。

`publish` 会读取 JSON 或 JSONL 候选文件中带 `owner/artifact/hash` 的引用：
指向同次输出时，`hash` 必须匹配该候选文件内容；其他引用必须以相同路径和 `hash` 出现在
`--input`。遗漏或不一致会在写预写日志前被拒绝；Markdown 依赖无法可靠推断，仍必须由
负责人明确声明。

## 恢复与打包

`recover --transaction <txid>` 只处理指定事务。`package` 会重新验证状态文件中保存的创作者
决定和独立审查记录，只打包当前 `hash` 与已接受快照一致、并且各项交付状态都已就绪的
Markdown、JSON 或 JSONL。

### 完整性由工具枚举，取舍由创作者声明

手写的 `--include` 清单**漏了东西时和没漏时长得一模一样**。状态文件里已经记着本集有哪些
已接受文件，所以这份枚举由 `package` 来做：本集 `episodes/<EP>/` 下每一个已接受路径，
要么在 `--include` 里，要么在 `--omit` 里，否则拒绝打包并逐条列出。

`--omit` 不是绕过，是留痕：清单的 `omitted` 段会记下每条被排除的路径、它的负责产物，
以及排除原因是「已就绪但主动不交付」还是「尚未就绪」。后者尤其重要——正在返工的产物
是最容易被无声绕过的，而收件方从一份看不出缺件的交付包里读不出这件事。

`--omit` 只接受本集的已接受路径：多文件产物换掉旧目标后，旧路径不再有已接受负责人，
既不能交付也不能被声明省略。其他分集的产物不进入本集的枚举范围。故事中确实需要交付屏显网址或屏显机器路径时，要有明确的例外
文件，绑定准确的文字、路径、字段、来源和文字呈现方法；其他网址与机器路径默认阻断。
例外只释放它逐字声明的那一个字符串：路径必须写到完整的那一条，只写盘符或目录开头会被
拒绝，整段文档也不能当作一条例外。文件协议网址、私钥与结构化凭据字段无条件阻断，
没有例外通道。

每条例外必须写齐七个字段，缺一即整体拒绝：`exact_text`（逐字原文）、`path`（绑定到哪个
交付文件）、`field`（该文字在产物中的字段位置）、`purpose`（固定为 `on_screen_text`）、
`provenance`（`creator_supplied` 或 `story_world_authored`）、`text_policy`
（`visible_on_screen` 或 `fictional_interface_text`）、`allow_delivery`（必须为 `true`）。
