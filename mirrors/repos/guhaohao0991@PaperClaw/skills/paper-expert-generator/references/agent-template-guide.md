# AGENT.md Authoring Guide

## Table of Contents
1. [File Structure Overview](#1-file-structure-overview)
2. [Section-by-Section Guide](#2-section-by-section-guide)
3. [Task 1: Paper Research (Template)](#3-task-1-paper-research)
4. [Task 2: Paper Evaluation (Template)](#4-task-2-paper-evaluation)
5. [Task 3: Daily Search (Template)](#5-task-3-daily-search)
6. [Task 4: Weekly Report (Template)](#6-task-4-weekly-report)
7. [Common Mistakes to Avoid](#7-common-mistakes-to-avoid)

---

## 1. File Structure Overview

A complete AGENT.md has these sections in order:

```
# <Agent Name>

## 角色定位

## 关键词库

## 核心任务

### 任务1：论文检索与总结（Paper Researching）
### 任务2：论文评估（Paper Reviewing）
### 任务3：每日论文检索（Daily Paper Search）
### 任务4：每周总结报告（Weekly Report）
```

---

## 2. Section-by-Section Guide

### Section: 角色定位 (Role Definition)

Purpose: Establish the agent's expert identity and evaluation lens.

Requirements:
- State the domain clearly in the first sentence
- List 3–4 core sub-areas with representative techniques
- List top publication venues (defines quality bar)
- State what the agent prioritizes in evaluation

See `domain-adaptation-guide.md` Section 4 for persona templates.

### Section: 关键词库 (Keyword Library)

Purpose: Define the search scope for `arxiv-search` and `daily-search` skills.

Format:
```markdown
## 关键词库

### 核心关键词（arXiv ti: 查询）
- `ti:<query1>`
- `ti:<query2>`
...

### 方法关键词
- `ti:<query>`
...

### 排除关键词（过滤无关领域）
`<term1>`, `<term2>`, `<term3>`
```

See `domain-adaptation-guide.md` Section 1 for keyword examples.

---

## 3. Task 1: Paper Research

```markdown
### 任务1：论文检索与总结（Paper Researching）

**触发条件**：用户提供论文标题、arXiv ID 或 URL

**执行流程**：

1. 确认论文来源（arXiv ID、URL 或标题搜索）
2. 下载 PDF 至 `workspace/papers/<short_title>/`
3. 创建 `metadata.json`（基础字段：arxiv_id, title, short_title, authors, abstract）
4. 撰写 `summary.md`，**必须回答以下10个问题**：

---

**summary.md 必须回答的10个问题**：

1. 论文试图解决什么问题？
2. 这是一个新问题吗？已有工作的局限是什么？
3. 验证的科学假设/核心主张是什么？
4. 有哪些相关研究？关键研究者和代表工作是什么？
5. 解决方案的核心技术贡献是什么？
6. [DOMAIN-SPECIFIC Q6]
7. [DOMAIN-SPECIFIC Q7]
8. [DOMAIN-SPECIFIC Q8]
9. [DOMAIN-SPECIFIC Q9]
10. [DOMAIN-SPECIFIC Q10]

---

**输出路径**：
```
workspace/papers/<short_title>/
├── metadata.json   ← 基础元数据（arxiv_id, title, authors, abstract）
└── summary.md      ← 回答上述10个问题的深度总结
```
```

Replace Q6–Q10 with domain-specific questions from `domain-adaptation-guide.md` Section 3.

---

## 4. Task 2: Paper Evaluation

```markdown
### 任务2：论文评估（Paper Reviewing）

**触发条件**：summary.md 撰写完成后，或用户明确要求评估

**前置检查（去重门控）**：
执行评估前，必须检查 `workspace/evaluated_papers.json`，如果 arXiv ID 或标题已存在，跳过评估，直接返回已有评分。

**Semantic Scholar 数据获取（每篇论文仅调用一次）**：
```bash
python skills/semantic-scholar/semantic_scholar_api.py \
  paper-by-arxiv "<arxiv_id>" --format json > workspace/papers/<short_title>/metadata.json
```
提取关键字段：`citationCount`, `publicationDate`, `venue`, `openAccessPdf.url`

**评分流程（必须使用 `<think>...</think>` 标签记录推理）**：

<think>
[在此详述每个维度的评分理由，引用论文中的具体证据]
- <DIM1>: X/10 because...
- <DIM2>: X/10 because...
- <DIM3>: X/10 because...
- <DIM4>: X/10 because...
- Impact calculation: citations=N, age_months=M → adjustment_factor=X
</think>

**四维评分（1–10分）**：

| 维度 | 描述 | 得分 |
|------|------|------|
| <DIM1_NAME> | <DIM1_DESC> | X/10 |
| <DIM2_NAME> | <DIM2_DESC> | X/10 |
| <DIM3_NAME> | <DIM3_DESC> | X/10 |
| <DIM4_NAME> | <DIM4_DESC> | X/10 |

**评分公式**：
```
base_score = (<dim1> + <dim2> + <dim3> + <dim4>) / 4
impact_score = date_citation_adjustment(citations, age_months)  # 见 semantic-scholar/SKILL.md
final_score = base_score × 0.9 + impact_score × 0.1
```

**评估完成后，执行以下操作（顺序不可变）**：

1. 将评分写入 `metadata.json` 的 `scores` 字段：
```json
"scores": {
  "<dim1_key>": X.0,
  "<dim2_key>": X.0,
  "<dim3_key>": X.0,
  "<dim4_key>": X.0,
  "impact": X.X,
  "final_score": X.XX
}
```

2. 生成 `scores.md` 评分报告（供人类阅读）

3. 使用文件锁安全更新注册表：
```bash
python skills/paper-review/scripts/update_registry.py \
  --id "<arxiv_id>" \
  --title "<full_title>" \
  --short_title "<short_title>" \
  --score <final_score>
```
```

Replace `<DIM1_NAME>` etc. with the domain-specific dimensions from `domain-adaptation-guide.md` Section 2.

---

## 5. Task 3: Daily Search

```markdown
### 任务3：每日论文检索（Daily Paper Search）

**触发方式**：定时任务（见 `schedules.json`）或用户执行"每日检索"

**执行流程**：

1. 运行批量检索脚本：
```bash
python skills/daily-search/scripts/daily_paper_search.py --top 3
```

2. 脚本自动完成：
   - 使用关键词库执行 arXiv 批量搜索
   - 三层去重（ID去重 → 标题去重 → 与 evaluated_papers.json 比对）
   - 相关性评分排序，选出 Top 3
   - 生成 `workspace/pending_evaluation_YYYY-MM-DD.json`
   - 发送如流消息摘要

3. 查看待评估清单：
```bash
cat workspace/pending_evaluation_$(date +%Y-%m-%d).json
```

4. 对每篇论文依次执行 **任务1（检索总结）+ 任务2（深度评估）**

**注意**：每篇评估中必须包含 `<think>...</think>` 推理标签。
```

---

## 6. Task 4: Weekly Report

```markdown
### 任务4：每周总结报告（Weekly Report）

**触发方式**：定时任务（每周日 10:00）或用户请求"生成周报"

**执行流程**：

1. 运行周报生成脚本：
```bash
python skills/weekly-report/scripts/generate_weekly_report_v2.py
```

2. 脚本自动完成：
   - 读取 `workspace/evaluated_papers.json`（直接从 JSON 读取，不解析 scores.md）
   - 筛选本周评估的论文，按 `final_score` 降序排列
   - 选出 Top 3，为每篇创建独立知识库文档
   - 生成 Markdown 周报（含知识库链接，不内嵌完整总结）
   - 通过如流 webhook 推送给目标用户

3. 确认：
   - [ ] 知识库文档已创建（每篇论文一个文档）
   - [ ] 如流消息已发送
   - [ ] 周报文件已保存至 `workspace/reports/weekly_report_YYYY-WNN.md`
```

---

## 7. Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Using regex to parse `scores.md` for scores | Read `metadata.json` → `scores` field directly |
| Calling Semantic Scholar API multiple times per paper | Call once, save to `metadata.json`, read from there |
| Skipping `<think>` tags in evaluation | Always required for Task 2 |
| Writing to `evaluated_papers.json` directly | Always use `update_registry.py` with file locking |
| Evaluating already-evaluated papers | Always check `evaluated_papers.json` first |
| Mixing arXiv ID formats (with/without `v1`) | Normalize to base ID (e.g., `2401.12345` not `2401.12345v1`) |
