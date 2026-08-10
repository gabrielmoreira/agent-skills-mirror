# 来源中立的方法蒸馏

## 目的与边界

来源中立不是删除出处。完整来源身份、locator、原始证据、claim、correction、权利和审核历史
始终保留在私有 owning distillation 中；下游 candidate tree、可公开 references 和任务输出只
保留完成稳定任务所需的中立方法。不得用“去标识”掩盖证据断链，也不得把来源作者的偏好、
修辞、案例或结论升级为普遍真理。

本约束不增加知识层或 Gate 版本。继续使用：

```text
evidence → claim → relation / capability rule → candidate specification
→ Gate 3 approved-for-eval → materialization → eval run → Gate 4 decision
```

第一性原理重建使用现有 `source_position: distiller-synthesis`、`transformation: T3` 和人工决定；
任务行为仍使用 T4 capability rule。来源中立投影是 Gate 3 审阅的 candidate bytes，不是新的
权威 YAML 或自动真实性证明。

## 第一性原理重建

在形成 T4 rule 前，用已有 claim、relation、`scope`、`limitations` 和人工审阅视图显式回答：

1. **problem**：稳定任务要解决什么问题；不得用书名、章节名或来源案例代替任务。
2. **premises**：哪些已接受 claim、关系和项目约束是推导前提。
3. **invariant**：无论来源措辞如何，哪些条件或关系必须保持。
4. **derivation**：每个检查、动作、输出和停止条件如何从前提与 invariant 得出。
5. **assumptions**：哪些条件未由目标输入直接观察到；不得把假设写成事实。
6. **boundaries / falsifiers / stops**：何时结论降级、何种反证推翻应用、缺什么就停止。

若上述任一项只能借助专名、原句、叙事顺序或可识别案例才能成立，则该内容保持
`reference-only`、`needs-verification` 或 review，不得强行生成来源中立候选。

## 私有记录与来源中立投影

私有治理记录继续保留 `source_id`、locator、最短必要原文、书中地位、T0-T4、限制和完整
追溯闭包。method-transfer 的三层 canonical 记录仍为 `method-source-evidence`、
`target-material-evidence`、`analogy-hypothesis`；第一层只供私有审计，不进入公开投影。

下游 candidate/public output 只可表达：

- 目标输入中直接可见的观察；
- 来源中立的检查、推理和结果；
- 假设、替代解释、限制、未知项和停止理由。

不得包含来源题名、作者、出版者、ISBN、系列名、原文件名或路径、归因句、引文、连续近似
改写、章节/页码/locator、私有 ID，或可识别的命名案例。候选的 trigger、nontrigger、示例、
reference 和输出模板都受同一约束。公共结果不得把 `method-source-evidence` 渲染给用户，也
不得把来源案例事实迁移为目标材料事实。

## 去标识与重写规则

- 只对 candidate/public projection 去标识；不修改私有 evidence、claim 或 manifest 历史。
- 用任务角色、输入变量、约束和失败条件重新推导，不以“某书”“某作者”或化名替换身份。
- 删除专名、独特隐喻、叙事顺序和案例特有数字；只有任务本身必需且有独立语义支持的领域
  术语或阈值可以保留。
- 示例必须从 stable task 重新构造，不得只替换来源案例中的名称。
- 公开候选若依法必须携带会暴露来源的归因，则停止公开投影并请求权利处置；不得静默删除
  必需归因，也不得违反本约束发布。

### 必需的私有 extra-terms

Gate 2 必须把方法来源明确分类为 `provenance_role: method-source`、`source_role: primary-book |
method-source | supplementary-book` 或 `type: book | book-*`；无法确认分类时 fail closed。lint
只从这些方法来源记录提取身份，避免把 project-policy 路径或目标论文身份误拦为图书泄漏。

manifest 的显式书目字段只能提供字面身份，无法自动发现未登记的语义别名。只要来源存在
译名、转写/romanization、旧 slug、来源派生 slug、系列别名、特有术语或具名案例，就必须在
私有 extra-terms 记录中完整列出，并在 Gate 3 candidate lint 与 Gate 5 发布前 lint 中同时
提供。该记录不是可选便利项；存在上述变体但缺失、为空或覆盖不完整时 fail closed。

extra-terms 只供本地私有 lint，不能复制进 candidate tree、公开日志或任务输出。机器 lint
只能匹配 manifest 和 extra-terms 已声明的字面形式；未声明的翻译、转写、别名、近义改写或
可识别叙事仍需人工并排审阅，lint PASS 不证明不存在语义泄漏。

## Gate 3 与 fail closed

Gate 3 前并排审核私有追溯闭包与来源中立 candidate tree，并确认：每个 T4 item 有逐项
semantic support；T3 重建的问题、前提、invariant、推导、假设和边界完整；candidate 不读取
方法来源才能执行；候选和 public output contract 不含上述禁项。当前
`gate3-approval-snapshot:v2` 已绑定完整 candidate tree 与权威治理文件，继续使用该契约，
不新增 Gate 版本。若适用，Gate 3/Gate 5 lint 必须加载完整 private extra-terms；不得以未提供
该文件的较弱扫描代替。

disclosure lint 只接受其 allowlist 内的 UTF-8 文本。非 UTF-8、未知二进制、缓存或 symlink
必须先移出 candidate tree；若二进制是运行时必需资产，则在建立格式专用且可复核的审计路径
前保持 Gate 3 blocked，不能以“scanner 跳过”代替审核。

结构 validator 不能证明重建合理或识别所有语义泄漏。任何身份残留、可识别案例、强行类比、
缺失目标证据、无法闭合的推导或权利冲突都使相应候选保持 review/revise；只允许修复和重新
取得 Gate 3 决定，不得物化、评测、公开或部署该漂移版本。
