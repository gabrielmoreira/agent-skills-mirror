---
user-invocable: true
description: Add field definitions to existing research outline.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Fields - Supplement Research Fields

## Trigger
`/research-add-fields`

## Workflow

### Step 1: Auto-locate Fields File
Find `*/fields.yaml` file in current working directory, auto-read existing fields definitions.

### Step 2: Get Supplement Source
Ask user to choose:
- **A. User direct input**: User provides field names and descriptions
- **B. Web Search**: Launch agent to search common fields in this domain

### Step 3: Display and Confirm
- Display suggested new fields list
- User confirms which fields to add
- User specifies field category and detail_level

### Step 4: Save Update
Append confirmed fields to fields.yaml, save file.

## Output
Updated `{topic}/fields.yaml` file (in-place modification, requires user confirmation)

## 触发方式
`/research-add-fields`

## 执行流程

### Step 1: 自动定位Fields文件
在当前工作目录查找 `*/fields.yaml` 文件，自动读取现有fields定义。

### Step 2: 获取补充来源
询问用户选择：
- **A. 用户直接输入**：用户提供字段名称和描述
- **B. Web Search搜索**：启动web-search-agent搜索该领域常用字段

### Step 3: 展示并确认
- 展示建议的新字段列表
- 用户确认哪些字段需要添加
- 用户指定字段分类和detail_level

### Step 4: 保存更新
将确认的字段追加到fields.yaml，保存文件。

## 输出
更新后的 `{topic}/fields.yaml` 文件（原地修改，需用户确认）
