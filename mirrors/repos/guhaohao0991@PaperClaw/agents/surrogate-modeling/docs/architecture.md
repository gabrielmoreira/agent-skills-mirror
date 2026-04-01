# 架构设计文档

本文档详细说明 PaperAgent 的系统架构、设计原则和实现细节。

---

## 📋 目录

- [架构概述](#架构概述)
- [系统分层](#系统分层)
- [核心组件](#核心组件)
- [数据流](#数据流)
- [设计原则](#设计原则)
- [技术栈](#技术栈)
- [扩展性设计](#扩展性设计)

---

## 架构概述

PaperAgent 采用分层架构设计，从上到下分为：

1. **Agent 定义层**：定义 Agent 的角色、任务和专业领域
2. **技能模块层**：实现具体的技能功能
3. **数据存储层**：管理论文数据和元数据
4. **外部服务层**：集成第三方服务

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Platform                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Surrogate-Modeling Expert Agent             │  │
│  │                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│  │  │ arXiv Search │  │ Paper Review │  │Weekly Rpt │ │  │
│  │  │    Skill     │  │    Skill     │  │   Skill   │ │  │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Workspace: 3d_surrogate_proj              │
│                                                              │
│  papers/                        weekly_reports/              │
│  ├── DeepONet/                  └── 2026-03-02_weekly.md    │
│  │   ├── DeepONet.pdf                                          │
│  │   ├── summary.md                                            │
│  │   ├── scores.md                                             │
│  │   └── metadata.json                                         │
│  ├── FNO/                                                      │
│  └── ...                                                       │
│                                                              │
│  papers/evaluated_papers.json (论文索引)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services                                │
│                                                              │
│  arXiv API          Semantic Scholar      百度知识库          │
│  (论文检索)         (引用数据)          (文档管理)           │
│                                                              │
│  如流消息 (SO)                                                │
│  (周报推送)                                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 系统分层

### 1. Agent 定义层

**位置**：`agent/`

**文件**：
- `AGENT.md`：Agent 核心定义
- `README.md`：Agent 使用说明
- `models.json`：模型配置

**职责**：
- 定义 Agent 的角色定位
- 描述专业领域和任务场景
- 配置模型和参数

### 2. 技能模块层

**位置**：`skills/`

**技能模块**：
- `arxiv-search/`：arXiv 论文检索
- `paper-review/`：论文总结和评估
- `weekly-report/`：周报生成和推送
- `semantic-scholar/`：引用数据获取

**职责**：
- 实现具体的技能功能
- 提供统一的 API 接口
- 管理技能依赖

### 3. 数据存储层

**位置**：`workspace/3d_surrogate_proj/`

**目录结构**：
```
workspace/3d_surrogate_proj/
├── papers/              # 论文存储
│   ├── <paper_title>/
│   │   ├── *.pdf
│   │   ├── summary.md
│   │   ├── scores.md
│   │   └── metadata.json
│   └── evaluated_papers.json
├── weekly_reports/      # 周报存储
├── search_logs/         # 检索日志
└── scripts/            # 辅助脚本
```

**职责**：
- 管理论文数据
- 存储周报和日志
- 提供数据访问接口

### 4. 外部服务层

**服务列表**：
- arXiv API：论文检索
- Semantic Scholar API：引用数据
- 百度知识库 API：文档管理
- 如流消息 API：消息推送

**职责**：
- 集成第三方服务
- 提供统一的服务接口
- 处理服务错误和重试

---

## 核心组件

### 1. arXiv Search Skill

**功能**：
- 从 arXiv 检索论文
- 智能去重
- 筛选高质量论文
- 下载论文 PDF

**核心方法**：
```python
def search_arxiv(query, max_results=30):
    """搜索 arXiv 论文"""
    pass

def deduplicate_papers(papers):
    """去重论文"""
    pass

def select_top_papers(papers, top_n=3):
    """筛选 Top N 论文"""
    pass

def download_paper(pdf_url, title, save_dir):
    """下载论文 PDF"""
    pass
```

**输入**：
- 检索关键词
- 最大结果数

**输出**：
- 论文列表
- 下载的 PDF 文件

### 2. Paper Review Skill

**功能**：
- 生成论文总结
- 多维度评分
- Date-Citation 权衡
- 更新论文索引

**核心方法**：
```python
def check_duplicate(arxiv_id):
    """检查论文是否已评估"""
    pass

def get_paper_metadata(arxiv_id):
    """获取论文元数据"""
    pass

def generate_summary(paper):
    """生成论文总结"""
    pass

def evaluate_paper(paper):
    """评估论文"""
    pass

def calculate_date_citation_adjustment(metadata):
    """计算 Date-Citation 调整因子"""
    pass

def update_evaluated_papers(paper):
    """更新已评估论文列表"""
    pass
```

**输入**：
- 论文元数据
- 论文 PDF

**输出**：
- `summary.md`：论文总结
- `scores.md`：论文评分
- `metadata.json`：元数据

### 3. Weekly Report Skill

**功能**：
- 读取已评估论文
- 筛选本周论文
- 生成周报
- 创建知识库文档
- 发送如流消息

**核心方法**：
```python
def load_evaluated_papers():
    """加载已评估论文"""
    pass

def filter_week_papers(papers, days=7):
    """筛选本周论文"""
    pass

def sort_and_select_top(papers, top_n=3):
    """排序并选择 Top N"""
    pass

def generate_weekly_report(week_papers, top_papers):
    """生成周报"""
    pass

def create_knowledge_base_docs(top_papers):
    """创建知识库文档"""
    pass

def send_weekly_report(report, recipients):
    """发送周报"""
    pass
```

**输入**：
- 已评估论文列表
- 周报配置

**输出**：
- 周报 Markdown 文件
- 知识库文档
- 如流消息

### 4. Semantic Scholar Skill

**功能**：
- 获取论文元数据
- 获取引用数据
- 获取作者信息

**核心方法**：
```python
def get_paper_by_arxiv(arxiv_id):
    """通过 arXiv ID 获取论文"""
    pass

def get_paper_by_title(title):
    """通过标题获取论文"""
    pass

def get_citation_count(paper_id):
    """获取引用数"""
    pass

def get_authors(paper_id):
    """获取作者信息"""
    pass
```

**输入**：
- arXiv ID 或论文标题

**输出**：
- 论文元数据（JSON 格式）

---

## 数据流

### 1. 论文检索流程

```
用户触发/定时任务
    ↓
arXiv Search Skill
    ↓
检索 arXiv API
    ↓
返回论文列表
    ↓
智能去重
    ↓
筛选 Top 3
    ↓
下载 PDF
    ↓
保存到 papers/<paper_title>/
```

### 2. 论文评估流程

```
论文 PDF
    ↓
Paper Review Skill
    ↓
检查是否已评估
    ↓
获取 Semantic Scholar 元数据
    ↓
生成 summary.md
    ↓
计算评分（四维评分 + Date-Citation）
    ↓
生成 scores.md
    ↓
更新 evaluated_papers.json
```

### 3. 周报生成流程

```
定时任务（每周日 10:00）
    ↓
Weekly Report Skill
    ↓
读取 evaluated_papers.json
    ↓
筛选本周论文
    ↓
排序并选择 Top 3
    ↓
读取 summary.md 和 scores.md
    ↓
生成周报 Markdown
    ↓
为精选论文创建知识库文档
    ↓
创建周报知识库文档
    ↓
发送如流消息
```

---

## 设计原则

### 1. 模块化设计

**原则**：
- 每个技能模块独立
- 模块之间通过数据文件通信
- 模块可独立测试和部署

**实现**：
- 技能模块封装在 `skills/` 目录
- 每个技能有独立的 `SKILL.md`
- 模块之间通过 JSON 文件交换数据

### 2. 数据驱动

**原则**：
- 所有数据持久化到文件
- 避免内存中的临时数据
- 便于恢复和调试

**实现**：
- 论文数据存储在 `papers/` 目录
- 元数据使用 JSON 格式
- 周报使用 Markdown 格式

### 3. 可扩展性

**原则**：
- 易于添加新的技能模块
- 易于扩展评分系统
- 易于集成新的外部服务

**实现**：
- 技能模块插件化
- 评分系统可配置
- 外部服务接口统一

### 4. 可维护性

**原则**：
- 代码结构清晰
- 文档完善
- 易于调试

**实现**：
- 详细的文档
- 清晰的目录结构
- 完善的错误处理

---

## 技术栈

### 核心技术

| 技术 | 用途 | 版本 |
|------|------|------|
| Python | 主要编程语言 | 3.8+ |
| OpenClaw | AI Agent 框架 | v1.0+ |
| GLM-4.7 | 大语言模型 | internal |

### 依赖库

| 库 | 用途 | 版本 |
|----|------|------|
| requests | HTTP 请求 | 2.28+ |
| python-dateutil | 日期处理 | 2.8.2+ |

### 外部服务

| 服务 | 用途 | API |
|------|------|-----|
| arXiv | 论文检索 | http://export.arxiv.org/api/query |
| Semantic Scholar | 引用数据 | https://api.semanticscholar.org |
| 百度知识库 | 文档管理 | 内部 API |
| 如流消息 | 消息推送 | 内部 API |

---

## 扩展性设计

### 1. 添加新的技能模块

**步骤**：
1. 在 `skills/` 下创建新目录
2. 创建 `SKILL.md` 文件
3. 实现技能功能
4. 在 `AGENT.md` 中引用

**示例**：
```
skills/
└── new-skill/
    ├── SKILL.md
    └── scripts/
        └── new_skill.py
```

### 2. 扩展评分系统

**步骤**：
1. 在 `paper-review/SKILL.md` 中添加新的评分维度
2. 更新评分公式
3. 更新 `scores.md` 模板

**示例**：
```markdown
### 6. 新评分维度 (New Dimension)

**评分**: [1-10]

**评分理由**:
[详细说明]
```

### 3. 集成新的外部服务

**步骤**：
1. 在 `skills/` 下创建新技能
2. 实现服务客户端
3. 在现有技能中调用

**示例**：
```python
# 新技能：Google Scholar
skills/
└── google-scholar/
    ├── SKILL.md
    └── google_scholar_api.py
```

---

## 下一步

了解架构设计后，请参考：

- [API_REFERENCE.md](API_REFERENCE.md) - API 参考
- [data_structure.md](data_structure.md) - 数据结构说明
- [workflow.md](workflow.md) - 工作流程详解

---

<div align="center">

**架构设计完成！现在可以开始扩展 PaperAgent 了 🎉**

</div>
