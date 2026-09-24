# 迭代、批次、选片与停止条件

## 核心判断

同一提示词多次生成只是在抽样，不等于产生了多个创作方案。每次生产记录必须区分：

```text
prompt_id + version  创作契约
batch_id             同一提示词和参数的一组抽样
generation_id        一次真实生成
selection_id         一次评审决定
iteration_id         一次有假设的修改与复测
```

## 批次定义

一个批次内固定：

- 提示词版本。
- provider、model 和主要参数。
- 输入参考及其权重。
- 时长、画幅和分辨率设置。
- 首尾帧或控制输入。

批次内观察随机差异；任何一项改变都建立新批次。不要在同一 `batch_id` 下偷偷修改提示词。

## 迭代记录

每次迭代写：

```text
iteration_id
shot_id
prompt_id
batch_id
observed_failure_codes
responsibility_layer
changed_variables
hypothesis
expected_improvement
result_generation_ids
decision
next_action
```

### changed_variables

只列真正改变的字段，例如：

```text
camera_end
asset_state_version
dialogue_timing
risk_focus
reference_scope.exclude
provider_adapter.motion_strength
```

不要写 `changed_variables=全部优化`。

### hypothesis

用可证伪句子：

```text
如果只把摄影机主运动从“推进+环绕”缩减为“缓慢推进”，人物出画和路径漂移应减少，同时身份与动作保持不变。
```

### decision

推荐值：

- `continue_same_batch`：继续观察随机差异。
- `new_prompt_version`：创作契约需要改变。
- `new_adapter_version`：只改平台设置。
- `revise_asset`：身份或状态资产不足。
- `split_shot`：镜头复杂度超出时长/能力。
- `select`：候选通过门。
- `stop_budget`：达到批准预算。
- `route_post`：转入剪辑、合成或后期修复。

## 变量隔离顺序

一次失败先定位责任层：

```text
资产事实 → 场景/镜头契约 → 主提示词表达 → 平台适配 → 生成随机性 → 后期
```

推荐每次只改变一个主要责任层。可以同时改同一层内强相关字段，例如 `camera_start/path/end` 作为完整摄影机契约一起改，但不要同时换脸参考、动作、运镜、光线和模型。

## 三类批次

### 探索批次

目标：快速验证构图、资产或动作方向。使用较低复杂度和明确预算；结果不直接进入 locked。

### 控制批次

目标：在已批准契约下观察随机差异。提示词、参数和参考完全相同。

### 修复批次

目标：验证一个失败假设。必须记录上一批失败码和 changed_variables。

## 选片评分

候选按镜头门评审，不以“最漂亮”为唯一标准：

| 维度 | 核心问题 |
|---|---|
| 叙事功能 | 观众是否读懂本镜目标 |
| 身份/状态 | 是否为批准角色和当前版本 |
| 数量/空间 | 人数、方向、布局、唯一物体是否正确 |
| 表演/动作 | 因果、重心、接触和落定是否成立 |
| 摄影机 | 起点、路径、终点、对焦和切点是否正确 |
| 光色/材质 | 光源逻辑、曝光和表面响应是否成立 |
| 对白/声音 | 逐字内容、口型、环境和混音是否正确 |
| 连续性 | 与前后镜头能否连接 |
| 技术缺陷 | 变形、闪烁、抖动、文字和压缩问题 |

项目可设权重，但身份、精确人数、逐字对白和关键连续性等 hard gate 不应被平均分抵消。

## 选片记录

至少写：

```text
selection_id
shot_id
generation_id
decision: shortlist / reject / select / supersede
passed_gates
known_defects
continuity_impact
rationale
reviewer
reviewed_at
```

已选择不等于完美。已知缺陷必须进入豁免、后期修复或返工，不在备注中消失。

## 失败分布

按错误码统计：

- 每个镜头失败次数。
- 每个责任层占比。
- 同一错误连续批次是否改善。
- 哪些 prompt version 解决或引入问题。
- 每个可用镜头尝试次数。
- 已记录成本和时间；缺失成本不推断为零。

统计用于改进方法，不用于责怪创作者或证明某模型绝对优劣。

## 停止条件

出现任一情况停止盲目生成：

- 候选通过 hard gate 和项目质量阈值。
- 连续两个批次在同一错误上无改善；回到责任层重写或拆镜。
- 达到批准预算、调用次数或时间上限。
- 失败属于已知能力边界，继续抽样不能改变结构限制。
- 拆镜、降低复杂度、重新做资产或后期修复的预期成本更低。
- 已有候选足以通过剪辑、声音或局部后期修复达到交付。

停止不是失败，而是把资源转向更有效的层。

## 继续生成前的问题

- 失败是随机差异还是结构性错误？
- 当前 batch 是否真的固定所有变量？
- 是否有一个明确 hypothesis？
- 下一个批次只改变什么？
- 预期改善怎样被观察？
- 预算还允许多少次？
- 若再失败，next_action 是什么？

答不出来时，不应继续同一提示词抽卡。

## 最小复测示例

```text
观察：F-CAMERA-CONFLICT，摄影机一边环绕一边快速推进，人物出画。
责任层：镜头契约。
changed_variables：camera_path、camera_end。
hypothesis：只保留缓慢直线推进，并写清双人近景终点，能减少出画。
保持不变：资产、站位、动作、对白、光线、provider adapter。
decision：new_prompt_version。
next_action：同参数生成一个控制批次，比较路径和身份。
```

## 质量门

- [ ] prompt、batch、generation、selection、iteration 分开。
- [ ] 批次内提示词和参数固定。
- [ ] changed_variables 具体且属于一个主要责任层。
- [ ] hypothesis 可证伪。
- [ ] 候选按 hard gate 和镜头目标评审。
- [ ] 失败码和已知缺陷可追溯。
- [ ] 满足质量阈值、连续无改善、预算、能力边界或后期修复条件时停止。
