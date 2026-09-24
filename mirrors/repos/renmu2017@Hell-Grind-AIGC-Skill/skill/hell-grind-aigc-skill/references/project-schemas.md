# 项目 schema v2

## ID 与版本

| 对象 | v2 格式 | 示例 |
|---|---|---|
| 项目 | `PRJ-*` | `PRJ-DEMO-001` |
| 角色 | `AST-CHAR-*` | `AST-CHAR-001` |
| 生物 | `AST-CREA-*` | `AST-CREA-002` |
| 道具 | `AST-PROP-*` | `AST-PROP-007` |
| 地点 | `AST-LOC-*` | `AST-LOC-003` |
| 视效 | `AST-VFX-*` | `AST-VFX-002` |
| 资产状态 | `<asset_id>@v###` | `AST-CHAR-001@v003` |
| 场次 | `SC###` | `SC012` |
| 镜头 | `SC###-SH###` | `SC012-SH004` |
| 提示词 | `<shot_id>-P###` | `SC012-SH004-P001` |
| 提示词版本 | `v###` | `v002` |
| 生成 | `GEN-*` | `GEN-SC012-SH004-0003` |
| 选择 | `SEL-*` | `SEL-SC012-SH004-001` |
| 豁免 | `WVR-*` | `WVR-SC012-SH004-001` |

v1 的 `CHR/CRT/PROP/LOC/VFX-*` 只在兼容校验中接受。新项目使用 v2 格式。ID 一经引用不重命名；变化使用版本和状态表达。

## `00_brief/project.yaml`

必填：

```yaml
schema_version: 2
project_id: PRJ-DEMO-001
project_name: "Demo"
created_date: "YYYY-MM-DD"
aspect_ratio: "16:9"
default_fps: 24
default_resolution: "1920x1080"
status: development
generation_authorized: false
publication_authorized: false
budget_currency: "unspecified"
budget_limit: ""
```

生成和发布授权必须分开。

## `02_assets/assets.csv`

```text
asset_id,asset_type,name,version,status,identity_invariants,reference_ids,rights_status,approved_by,notes
```

`asset_type`：`character/creature/prop/location/vfx`。`status`：`proposed/reference_ready/approved/deprecated`。

## `02_assets/reference-scope.csv`

```text
reference_id,asset_id,source_path_or_url,rights_status,inherit_identity,inherit_state,inherit_material,inherit_space,inherit_composition,inherit_camera,inherit_lighting,inherit_color,exclude,approval_status,notes
```

布尔字段使用 `true/false`；URL 仅记录用户明确提供或有权使用的来源，仓库模板不含第三方 URL。

## `02_assets/asset-state-matrix.csv`

```text
asset_version_id,asset_id,version,state_name,identity_invariants,state_variables,costume_or_surface,damage_or_weathering,carried_props,reference_ids,approval_status,notes
```

## `03_scenes/scenes.csv`

```text
scene_id,scene_order,title,location_id,time_of_day,story_goal,open_state,close_state,status,notes
```

`location_id` 引用批准 `AST-LOC-*`。

## `03_scenes/spatial-map.csv`

```text
scene_id,zone_id,zone_name,screen_relation,depth_layer,entry_exit,anchor_objects,allowed_assets,lighting_source,continuity_notes
```

多值字段使用分号分隔。

## `04_shots/shots.csv`

```text
shot_id,scene_id,shot_order,duration_seconds,status,narrative_goal,asset_version_ids,open_state,close_state,camera_start,camera_path,camera_end,continuity_in,continuity_out,must_hold,changes_here,must_not_appear,risk_focus,prompt_id,selected_generation_id,notes
```

`status`：`planned/contract_ready/prompt_ready/generated/reviewed/selected/locked/needs_revision`。

## `04_shots/beat-sheet.csv`

```text
shot_id,beat_order,start_seconds,end_seconds,actor_or_source,trigger,action,contact_target,reaction,end_state,dialogue_id,audio_cue_id
```

时间必须在镜头时长内，start < end；同镜 beat_order 唯一。

## `04_shots/audio-cues.csv`

```text
audio_cue_id,shot_id,start_seconds,end_seconds,category,source,content_or_effect,spatial_position,mix_priority,continuity_key,notes
```

`category`：`dialogue/foley/ambience/music/silence`。

## `05_prompts/prompt-index.csv`

```text
prompt_id,shot_id,version,status,richness,master_prompt_path,adapter_path,parent_version,change_reason,changed_variables,prompt_sha256,approved_by,notes
```

`status`：`draft/checked/approved/superseded`。主提示词和 adapter 使用不同文件路径。

## `06_generations/generation-log.csv`

```text
generation_id,shot_id,prompt_id,batch_id,provider,model,seed,parameters_json,created_at,status,output_path,cost,currency,failure_codes,notes
```

每次真实调用追加一行，包括失败。成本未知时留空并说明，不用空白代表免费。

## `06_generations/iteration-log.csv`

```text
iteration_id,shot_id,prompt_id,batch_id,observed_failure_codes,responsibility_layer,changed_variables,hypothesis,expected_improvement,result_generation_ids,decision,next_action
```

## `07_review/selection-log.csv`

```text
selection_id,shot_id,generation_id,decision,passed_gates,known_defects,continuity_impact,rationale,reviewer,reviewed_at,notes
```

`decision`：`shortlist/reject/select/supersede`。

## `07_review/continuity-matrix.csv`

```text
shot_id,asset_version_ids,screen_direction,spatial_state,costume_state,injury_state,prop_state,environment_state,action_in,action_out,audio_state,open_issues,notes
```

## `07_review/waivers.csv`

```text
waiver_id,shot_id,gate_code,issue,rationale,impact,approved_by,approved_at,expires_or_scope,notes
```

豁免必须有批准人和范围，不能用空记录跳过 hard gate。

## 状态与引用规则

- `contract_ready` 必须有可执行首尾状态和时间线。
- `prompt_ready` 必须引用 checked/approved prompt。
- `generated` 及以后必须有 generation。
- `selected/locked` 必须有 decision=select 的 selection。
- `locked` 不允许未处理 error，除非存在有效 waiver。
- selected_generation_id 必须与 selection log 一致。
- generation 引用 prompt ID，不只引用模糊版本号。
- iteration 必须有 changed_variables、hypothesis 和 next_action。
- 不覆盖失败生成、评审意见或被引用旧版本。

## 文件路径

- 项目内相对路径优先。
- 校验器拒绝解析到项目外的受管文件路径。
- 输出媒体可以记录绝对路径，但移动/上传需另行授权。
- CSV 使用 UTF-8，第一行是稳定表头。
- 多值字段用分号，不用不稳定自然语言列表。
