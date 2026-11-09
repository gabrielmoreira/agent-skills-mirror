# Agent 配合应用编辑：单条 rules 扩展任务

适用：已核实的 Clash Verge Rev 2.5.8、一个已经存在且当前 profile 独占的 rules 扩展、一个用户明确选择的 DOMAIN 和现有出站组。先核对实际安装版本；其他版本需要对应适配，不要求用户为匹配本例升级。此处不创建扩展、不修改订阅原文／生成配置、不切换 profile。

## 已实现的辅助接口

`scripts/agent_rules_task.py` 是供宿主 Agent 调用的纯内存库，没有文件读取、应用执行或联网 CLI：

- `prepare_rules_task(...)`：复用 `rules_extension_plan.compile_rules_extension` 与 `clash_verge_258.inspect_linkage(..., extension_kind='rules')`，生成私有候选、明确步骤和公开摘要
- `assess_supplied_readback(task, ...)`：重新核对供给的来源／归属与内容，区分完全相同、语义相同但字节不同、未改变、意外差异及绑定变化；不会代替真实读回

宿主调用形式（参数来自已经核实且获准的私有上下文，不是可直接执行的占位输入）：

```python
task = prepare_rules_task(request, binding, app_plist=app_plist,
    profile_index=profile_index, extension=extension, base=base,
    selected_uid=selected_uid, selected_basename=selected_basename,
    base_basename=base_basename, entry_request=entry_request,
    refs=refs, source_kinds=source_kinds)
summary = task.public_report()
private_diff = task.private_review()  # 仅私有用户/宿主审阅
private_content = task.private_material()  # 原文和候选，不是授权
```

`refs` 只含 task_ref、host_scope_ref、app_ref、profile_ref、backup_ref、recovery_ref 六个别名。`source_kinds` 明确 app_plist、profile_index、extension、base 四个角色；前两项必须是 file_bytes，后两项可为 file_bytes 或 app_text，标签不证明真实来源。`base_basename` 必须与选中 profile 的声明链一致。比较时提供同名的新来源参数、选中 UID／文件名、entry_request 和 source_kinds 给 `assess_supplied_readback(task, ...)`。

任务到期后仍可取回原文、比较已供给数据，但必须重新审阅后续动作；取消或入口改变后仍可检查保留原文，比较器分别报告未比较或绑定变化。实际动作必须重新核对当前许可／目标，这些材料不恢复权限。

原 request、binding 和规则编译校验继续使用，不再建立第二套规则引擎。本批只支持恰好含 prepend／append／delete 三个键的文档，三序列最初必须为空；prepend 仍须是共享编译器支持的单行空内联序列，多行 flow 空序列返回 EMPTY_INLINE_PREPEND_REQUIRED。合法头尾／行尾注释可以保留，底层只在选定序列内按字节插入规则，保留其余原文，包括中文／emoji、UTF-8 BOM、CRLF 和注释。额外键、非空 append／delete 仍不支持，不能为了通过检查删除用户内容或注释。

只识别共享编译器支持的单行内联序列完整精确重复为 no_change，包括含注释原文；其他非空 prepend 返回范围不支持。若 GUI 将已保存规则改为块式 YAML，只有无注释任务可能取得下述有限语义比较结果；含注释任务的非精确读回必须重新审阅。重新 prepare 块式非空 prepend 仍返回 NONEMPTY_PREPEND_UNSUPPORTED；Agent 应据实际内容停止重复写入并解释限制，不强行改格式或追加规则。无改动时结束该写入任务，不创建备份、操作或恢复回执。

私有审阅的 format_scope 随原文／候选内容变化：任一含 `#` 时为 comment_preserving_three_sequence_yaml_exact_bytes_required；两者均无 `#` 时为 comment_free_three_sequence_yaml_formatting_only。这是保守的字节标记检查，不是新建注释解析器；后一范围也要求实际读回没有 `#` 才能做有限语义比较。原文字节及其摘要始终保留在私有材料中，供独立恢复审阅使用，不以去注释或重新序列化的文档替代备份。

SEMANTIC_PLAN_BLOCKED 来自既有 compile_plan 语义前提检查，与本次注释格式支持独立；其条件是 request.template 不是 keep-existing，或 compile_plan 的 blocker 代码集合不等于原有 NATIVE_SCHEMA_ADAPTER_NOT_IMPLEMENTED、VERSION_CAPABILITY_UNVERIFIED、NATIVE_ACCEPTANCE_NOT_RUN 三项。本修正不改变该条件。实际请求遇到此错误时检查其真实 template、blockers 及对应规则完整性、来源链、组和保护优先级事实，缺失或未知就保留阻塞，不能为了编译通过改写意图或补造 facts。

输入由已经获准的私有宿主提供：选定扩展、基础 profile、应用 plist、配置索引的完整有界字节，以及已核对的版本、当前来源和非识别性别名。真实路径、域名、组名、订阅或认证资料不进入公开摘要。仅在私有操作审阅中读取任务的私有材料；不能 pickle、公开上传或把完整配置打印进诊断报告。

先复用 [环境入口](host-libraries.md#environment-entry) 选择本轮路线并绑定实际目标；准备内存候选不证明目标可用，真正采集和配置动作仍分别使用 offline_precheck／configuration 入口。VM 宿主和来宾分开绑定；已有 VPS 出口不把本机任务变成 VPS 任务。退出、改选、证据过期或目标变化后，旧任务不能直接执行。

## Agent 的实际操作

1. 核对已安装应用、用户／目标、当前 profile 和唯一扩展；确认各份来源对应实际对象。不能把 plist 的版本字符串当作已安装进程证明
2. 展示唯一 DOMAIN→组的差异、顺序影响与受保护规则。编译器输出的未知链、优先级和原生证据缺口仍须逐项解释或调查，不直接删除 blocker
3. 在获准私有位置保留并读回原扩展及必要元数据观察，先准备不依赖在线 Agent 的恢复步骤。专属扩展外的内容不随备份公开
4. 取得具体许可：目标／应用／扩展、单条改动、备份、可能的验证／重载／内核重启／DNS 同步及连接中断、读回与恢复条件。审批范围须覆盖 Save 已知的连带效果
5. 解决旧编辑窗口和其他写入者；不要擅自丢弃未保存内容。紧邻 Save 前重新以 `environment_entry.require_entry(current_entry, "configuration", target_ref)` 校验当前入口，并与任务原入口核对；变化就重新计划。重新读取来源，确认与已审阅内容一致，再通过该版本受支持的编辑界面保存一次。关闭窗口本身不证明无其他写入者
6. Save 已触发应用更新时不重复额外重载。响应丢失或超时标记 save_uncertain，先检查状态，不盲目再保存。外加重启或网络操作仍需对应许可
7. 重新观察文件／应用内容、当前归属、载入结果和有效规则；实际流量另按获准程序、路径、端点及预算验证。不接触 Claude，不默认执行订阅刷新、健康检查、DNS 查询或读取全部连接
8. 如需恢复，先看当前内容及归属。仅在具体批准的条件仍成立且没有后续改动时逆转本次变更；有冲突、换 profile、未知字节或权限撤回时停下，重新审阅恢复范围，不能把旧整文件强行覆盖回去

这些动作由真实 Agent 和已提供的受支持应用工具执行。该辅助库不自动化 UI，不注入 JavaScript，不开启 DevTools 或新控制通道；应用内部 Tauri 函数不是可直接调用的外部公开 API。

## 内容核验不能替代实际效果

- `file_bytes` 只比较宿主实际供给的原文件字节，文件身份与采集可信度仍由宿主建立
- `app_text` 只表示应用文本观察，不能填成文件字节／inode 验证；应用内对象重新序列化也不是原文件
- 比较器的 exact_match／semantic_match_bytes_differ 等结论不是批准，也不是“保存成功”。没有实际来源时不得填入预期候选假装读回
- 通过现有来源／归属和内容校验后，比较器优先识别候选字节 exact_match 与原文字节 unchanged。只有 original／candidate／readback 三者均无 `#`，且三个序列恰好符合候选，才可能报告 semantic_match_bytes_differ；宿主仍须事先明确批准有限格式化范围。任一含 `#` 时，非精确 GUI 重排、注释删除／新增／修改／移动乃至仅换行或空白变化，都报告 unexpected_delta／conflict_requires_new_review，不能把注释当作可丢格式。额外字段、丢失自定义内容或多出规则也不能忽略。记录真实保存后的摘要，不冒称候选字节摘要
- 恢复读回目前只直接识别原文字节完全相同；若应用将原文重排成语义相同的三空序列，比较器仍保守报告 unexpected_delta，需宿主独立审阅，不据此断言恢复失败或自动覆盖。
- 保存、文件内容、元数据、应用载入、有效规则、真实路由和恢复分别记录。保存返回正常不填满后面几层，也不证明 IPv4-only 或免封

## 内置事务与权限边界

原 `repair_cli` 和生产事务／恢复门禁保持原样。只读或元数据能力不支持时，先明确其原因；另一个合法且已授权的应用／宿主读取可提供独立的供给数据，但不能篡改旧预检结果或模拟 native session。

权限拒绝、审批拒绝、PC0、目标不符、范围撤回及恢复冲突都不是能力缺口，不能改走界面或其他工具规避。新 macOS 私有控制文件读取子集也不是 Info.plist 或任意配置的通用安全读取器。

本接口的合成测试仅证明候选组织与内容比较。真实应用编辑、保存副作用、并发、载入、生效和恢复仍需对应版本的设备验收。受支持应用操作路径不取消具体授权、最小差异和独立恢复要求。
