---
user-invocable: true
description: Read research outline, launch independent agent for each item for deep research. Disable task output.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - Deep Research

## Trigger
`/research-deep`

## Workflow

### Step 1: Auto-locate Outline
Find `*/outline.yaml` file in current working directory, read items list, execution config (including items_per_agent).

### Step 2: Resume Check
- Check completed JSON files in output_dir
- Skip completed items

### Step 3: Batch Execution
- Batch by batch_size (need user approval before next batch)
- Each agent handles items_per_agent items
- Launch web-search-agent (background parallel, disable task output)

**Parameter Retrieval**:
- `{topic}`: topic field from outline.yaml
- `{item_name}`: item's name field
- `{item_related_info}`: item's complete yaml content (name + category + description etc.)
- `{output_dir}`: execution.output_dir from outline.yaml (default: ./results)
- `{fields_path}`: absolute path to {topic}/fields.yaml
- `{output_path}`: absolute path to {output_dir}/{item_name_slug}.json (slugify item_name: replace spaces with _, remove special chars)

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

**Prompt Template**:
```python
prompt = f"""## Task
Research {item_related_info}, output structured JSON to {output_path}

## Field Definitions
Read {fields_path} to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
{output_path}

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
Task is complete only after validation passes.
"""
```

**One-shot Example** (assuming researching GitHub Copilot):
```
## Task
Research name: GitHub Copilot
category: International Product
description: Developed by Microsoft/GitHub, first mainstream AI coding assistant, ~40% market share, output structured JSON to /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## Field Definitions
Read /home/weizhena/AIcoding/aicoding-history/fields.yaml to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
/home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f /home/weizhena/AIcoding/aicoding-history/fields.yaml -j /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json
Task is complete only after validation passes.
```

### Step 4: Wait and Monitor
- Wait for current batch to complete
- Launch next batch
- Display progress

### Step 5: Summary Report
After all complete, output:
- Completion count
- Failed/uncertain marked items
- Output directory

## Agent Config
- Background execution: Yes
- Task Output: Disabled (agent has explicit output file when complete)
- Resume support: Yes

## 触发方式
`/research-deep`

## 执行流程

### Step 1: 自动定位Outline
在当前工作目录查找 `*/outline.yaml` 文件，读取items列表、execution配置（含items_per_agent）。

### Step 2: 断点续传检查
- 检查output_dir下已完成的JSON文件
- 跳过已完成的items

### Step 3: 分批执行
- 按batch_size分批（完成一批需要得到用户同意才可进行下一批）
- 每个agent负责items_per_agent个项目
- 启动web-search-agent（后台并行，禁用task output）

**参数获取**：
- `{topic}`: outline.yaml中的topic字段
- `{item_name}`: item的name字段
- `{item_related_info}`: item的完整yaml内容（name + category + description等）
- `{output_dir}`: outline.yaml中execution.output_dir（默认./results）
- `{fields_path}`: {topic}/fields.yaml的绝对路径
- `{output_path}`: {output_dir}/{item_name_slug}.json的绝对路径（slugify处理item_name：空格替换为_，移除特殊字符）

**硬约束**：以下prompt必须严格复述，仅替换{xxx}中的变量，禁止改写结构或措辞。

**Prompt模板**：
```python
prompt = f"""## 任务
调研 {item_related_info}，输出结构化JSON到 {output_path}

## 字段定义
读取 /home/weizhena/AIcoding/aicoding-history/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## 验证
完成JSON输出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/weizhena/AIcoding/aicoding-history/fields.yaml -j /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json
验证通过后才算完成任务。
```

### Step 4: 等待与监控
- 等待当前批次完成
- 启动下一批
- 显示进度

### Step 5: 汇总报告
全部完成后输出：
- 完成数量
- 失败/不确定标记的items
- 输出目录

## 任务
调研 name: GitHub Copilot
category: 国际产品
description: Microsoft/GitHub开发，首个主流AI编程助手，市场份额约40%，输出结构化JSON到 /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## Agent配置
- 后台执行: 是
- Task Output: 禁用（agent完成时有明确输出文件）
- 断点续传: 是
