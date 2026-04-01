# 配置说明

本文档详细说明 PaperAgent 的各种配置选项，包括环境变量、知识库配置、定时任务配置等。

---

## 📋 目录

- [环境变量配置](#环境变量配置)
- [知识库配置](#知识库配置)
- [如流消息配置](#如流消息配置)
- [定时任务配置](#定时任务配置)
- [检索关键词配置](#检索关键词配置)
- [评分系统配置](#评分系统配置)
- [周报生成配置](#周报生成配置)
- [高级配置](#高级配置)

---

## 环境变量配置

### 环境变量文件

PaperAgent 使用 `.env` 文件管理环境变量。创建 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑文件
nano .env
```

### 环境变量列表

#### 必需变量

| 变量名 | 说明 | 示例 |
|-------|------|------|
| `BAIDU_API_KEY` | 百度智能云 API Key | `bce-v3/ALTAK-xxx` |
| `COMATE_AUTH_TOKEN` | Comate 认证 Token | `Bearer-eyJ0eXAiOiJKV1QiLCJhbGc...` |

#### 可选变量

| 变量名 | 说明 | 示例 |
|-------|------|------|
| `SERPAPI_KEY` | SerpAPI Key（Google Scholar） | `89c2a9d42175eab6076128d63919085a...` |
| `BAIDU_MAP_AK` | 百度地图 Access Key | `your_baidu_map_ak_here` |

### 获取 API Key

#### BAIDU_API_KEY

1. 访问 https://cloud.baidu.com/
2. 登录百度账号
3. 进入控制台
4. 创建应用
5. 获取 API Key

**用途**：
- 百度学术搜索
- 百度百科
- 百度搜索

#### COMATE_AUTH_TOKEN

1. 联系你的百度内部管理员
2. 或从现有的百度内部工具中获取
3. Token 格式：`Bearer-eyJ0eXAiOiJKV1QiLCJhbGc...`

**用途**：
- 百度知识库 API
- 如流消息 API

#### SERPAPI_KEY（可选）

1. 访问 https://serpapi.com/
2. 注册账号
3. 进入控制台
4. 获取 API Key

**用途**：
- Google Scholar 搜索
- 学术引用数据

#### BAIDU_MAP_AK（可选）

1. 访问 https://lbsyun.baidu.com/
2. 登录百度账号
3. 创建应用
4. 选择 Web 服务 API
5. 获取 AK（Access Key）

**用途**：
- 百度地图服务
- 地点搜索
- 天气查询

### 环境变量优先级

环境变量的加载优先级（从高到低）：

1. 系统环境变量（`export VAR=value`）
2. `.env` 文件
3. 默认值（代码中硬编码）

---

## 知识库配置

### 配置文件位置

编辑周报生成脚本：

```bash
~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py
```

### 配置项

```python
# 知识库配置
self.ku_repo_id = "your_repository_guid"  # 知识库ID
self.ku_parent_doc_id = "your_parent_doc_guid"  # 父文档ID
```

### 获取知识库 ID

1. 访问百度知识库 https://ku.baidu-int.com/
2. 进入你的知识库
3. 查看浏览器地址栏
4. URL 格式：
   ```
   https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/qv-vZnw7HE/jnGipY319RaSyz
   ```

**URL 解析**：
- `HFVrC7hq1Q` - spaceGuid（空间ID，URL使用）
- `pKzJfZczuc` - groupGuid（群组ID，URL使用）
- `qv-vZnw7HE` - repositoryGuid（知识库ID，API调用使用）
- `jnGipY319RaSyz` - parent_doc_guid（父文档ID，API调用使用）

**重要说明**：
- API 调用只需要 `repositoryGuid` 和 `parent_doc_guid`
- URL 中的 `spaceGuid` 和 `groupGuid` 不用于 API 调用

### 知识库 API 调用示例

```python
from ku_api_client import KuApiClient

client = KuApiClient()

# 创建文档
result = client.create_doc(
    repository_guid="qv-vZnw7HE",  # 知识库ID
    creator_username="guhaohao",    # 创建者用户名
    title="文档标题",
    content="文档内容",
    parent_doc_guid="jnGipK319RaSyz",  # 父文档ID
    create_mode=2
)
```

### 知识库文档结构

```
知识库根目录
└── PaperAgent: Surrogate-Modeling Weekly Report (jnGipY319RaSyz)
    ├── 2026-03-02 周报
    ├── 2026-03-02 DeepONet - 论文总结
    ├── 2026-03-02 FNO - 论文总结
    └── 2026-03-02 CViT - 论文总结
```

---

## 如流消息配置

### 配置文件位置

编辑周报生成脚本：

```bash
~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py
```

### 配置项

```python
# 如流消息接收人
self.recipients = ["username1", "username2"]
```

### 获取如流用户名

1. 登录如流 https://so.baidu-int.com/
2. 查看个人资料
3. 用户名通常是拼音或工号

**示例**：
- `guhaohao`（拼音）
- `12345678`（工号）

**注意**：
- 用户名不是邮箱
- 用户名区分大小写
- 多个用户名用逗号分隔

### 如流消息格式

```python
message = f"""
📊 **三维几何代理模型研究周报** - {report_date}

**报告周期**: {week_start} - {report_date}
**评估论文总数**: {len(week_papers)}
**精选推荐**: Top 3 精选论文

🏆 **本周Top 3论文**:
1. [论文1] - 评分: X.XX
2. [论文2] - 评分: X.XX
3. [论文3] - 评分: X.XX

📎 **周报链接**: {doc_url}

📄 **精选论文完整总结**:
1. [论文1](链接1)
2. [论文2](链接2)
3. [论文3](链接3)
"""
```

### 如流消息发送示例

```python
from send_message import GroupMessageSender

sender = GroupMessageSender()

result = sender.send_app_message(
    to_users="guhaohao|hesensen",  # 多个用户用 | 分隔
    msg_type="text",
    content=message
)

print(result)
```

---

## 定时任务配置

### 配置方式

使用 OpenClaw 的 cron 功能配置定时任务：

```bash
# 查看所有定时任务
openclaw cron list

# 添加定时任务
openclaw cron add <job-config.json>

# 更新定时任务
openclaw cron update <job-id> --patch <patch.json>

# 删除定时任务
openclaw cron remove <job-id>

# 立即执行任务
openclaw cron run <job-id>
```

### 每日论文检索配置

#### 任务配置

```json
{
  "name": "Daily Paper Search - Surrogate Modeling",
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日论文检索任务：检索三维几何代理模型领域的最新论文",
    "model": "glm/glm-4.7-internal"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
```

#### Cron 表达式说明

```
0 21 * * *
│ │ │ │ │
│ │ │ │ └─ 星期几 (0-6, 0=周日)
│ │ │ └─── 月份 (1-12)
│ │ └───── 日期 (1-31)
│ └─────── 小时 (0-23)
└───────── 分钟 (0-59)
```

**常用时间**：
- `0 21 * * *` - 每天 21:00
- `0 9 * * 1-5` - 工作日 9:00
- `0 */6 * * *` - 每 6 小时
- `0 0 * * 0` - 每周日 0:00

#### 时区配置

```json
"tz": "Asia/Shanghai"  # 北京时间（UTC+8）
```

**常用时区**：
- `Asia/Shanghai` - 北京时间
- `Asia/Singapore` - 新加坡时间
- `America/New_York` - 美国东部时间
- `Europe/London` - 伦敦时间

### 每周报告生成配置

#### 任务配置

```json
{
  "name": "Weekly Report - Surrogate Modeling",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * 0",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "生成三维几何代理模型研究周报，创建知识库文档并发送给指定用户",
    "model": "glm/glm-4.7-internal"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
```

#### Cron 表达式说明

```
0 10 * * 0
│ │ │ │ │
│ │ │ │ └─ 星期日 (0=周日)
│ │ │ └─── 每月
│ │ └───── 每天
│ └─────── 10:00
└───────── 0分钟
```

**常用时间**：
- `0 10 * * 0` - 每周日 10:00
- `0 9 * * 1` - 每周一 9:00
- `0 18 * * 5` - 每周五 18:00

### 禁用/启用任务

```bash
# 禁用任务
openclaw cron update <job-id> --patch '{"enabled": false}'

# 启用任务
openclaw cron update <job-id> --patch '{"enabled": true}'
```

### 查看任务运行历史

```bash
# 查看任务运行历史
openclaw cron runs <job-id>

# 查看最近 10 次运行
openclaw cron runs <job-id> --limit 10
```

---

## 检索关键词配置

### 配置文件位置

编辑 Agent 定义文件：

```bash
~/.openclaw/agents/surrogate-modeling-expert/AGENT.md
```

### 核心关键词

```markdown
### 核心关键词（几何感知神经算子）
- geometry-aware neural operator
- neural operator 3D mesh
- neural operator unstructured mesh

### 算子学习与几何
- operator learning arbitrary geometry
- operator learning complex domain
- mesh-based neural operator

### PDE求解与几何
- transformer PDE solver 3D
- neural PDE solver geometry
- deep learning CFD surrogate

### 物理信息与几何
- physics-informed neural network 3D geometry
- physics-informed mesh
- geometry-aware physics-informed

### 代理模型与几何
- surrogate model 3D geometry
- deep learning surrogate CFD
- neural surrogate structural mechanics

### 特定应用场景
- neural network pressure field prediction
- deep learning aerodynamics surrogate
- neural operator fluid dynamics
```

### 排除关键词

```markdown
### 排除关键词（避免不相关领域）
- epidemic, epidemiology, disease modeling
- population dynamics, social network
- finance, economics
- NLP, language model, text
```

### 添加自定义关键词

在 `AGENT.md` 中添加你的关键词：

```markdown
### 自定义关键词
- your_keyword_1
- your_keyword_2
- your_keyword_3
```

---

## 评分系统配置

### 评分维度

PaperAgent 使用四维评分系统：

| 维度 | 权重 | 范围 | 说明 |
|------|------|------|------|
| 工程应用价值 | - | 1-10 | 解决实际工程问题的能力、工业级验证、部署可行性 |
| 网络架构创新 | - | 1-10 | 架构设计新颖性、模块机制创新、对比优势 |
| 理论贡献 | - | 1-10 | 数学框架、定理证明、理论连接、理论深度 |
| 结果可靠性 | - | 1-10 | 实验严谨性、开源支持、可复现性 |
| 影响力评分 | - | 1-10 | 科研应用价值 + Date-Citation权衡调整 |

### 最终评分公式

```python
四维基础评分 = (工程应用 + 架构创新 + 理论贡献 + 可靠性) / 4
最终综合评分 = 四维基础评分 × 0.9 + 影响力评分 × 0.1
```

### Date-Citation 权衡配置

#### 年龄边界

```python
# 最新论文
age_months <= 3

# 中期论文
3 < age_months <= 24

# 成熟论文
age_months > 24
```

#### 调整因子

```python
# 最新论文（≤ 3个月）
adjustment_factor = 0.2

# 中期论文（3-24个月）
if citations >= 50:
    adjustment_factor = 0.5
elif citations >= 20:
    adjustment_factor = 0.3
elif citations >= 10:
    adjustment_factor = 0.2
else:
    adjustment_factor = 0.1

# 成熟论文（> 24个月）
if citations >= 200:
    adjustment_factor = 0.5
elif citations >= 100:
    adjustment_factor = 0.4
elif citations >= 50:
    adjustment_factor = 0.3
elif citations >= 20:
    adjustment_factor = 0.2
else:
    adjustment_factor = 0.0
```

#### 引用密度奖励

```python
citation_density = citations / age_months

if citation_density >= 10:
    density_bonus = 0.2
elif citation_density >= 5:
    density_bonus = 0.1
else:
    density_bonus = 0.0
```

### 自定义评分标准

编辑 `skills/paper-review/SKILL.md`，找到"评分标准详细说明"部分，调整评分标准。

---

## 周报生成配置

### 配置文件位置

编辑周报生成脚本：

```bash
~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py
```

### 周报模板

```python
def generate_weekly_report(self, week_papers, top_papers):
    """生成周报 Markdown"""
    report_date = datetime.now().strftime("%Y-%m-%d")
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    report = f"""# 📊 三维几何代理模型研究周报

**报告周期**: {week_start} - {report_date}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**报告人**: Surrogate-Modeling Expert Agent

---

## 📌 本周概览

- **评估论文总数**: {len(week_papers)}
- **精选推荐论文**: Top {len(top_papers)}

---

## 🌟 本周精选论文 Top {len(top_papers)}

"""

    # 添加精选论文
    for i, paper in enumerate(top_papers, 1):
        report += self.generate_paper_section(paper, i)

    # 添加完整评分列表
    report += self.generate_score_list(week_papers)

    # 添加附录
    report += self.generate_appendix(top_papers)

    return report
```

### 自定义周报格式

修改 `generate_weekly_report` 函数，调整周报格式。

---

## 高级配置

### 工作目录配置

默认工作目录：`~/.openclaw/workspace/3d_surrogate_proj/`

修改工作目录：

```python
# 编辑周报生成脚本
self.workspace_dir = Path("/your/custom/workspace")
```

### 论文目录结构配置

默认目录结构：

```
papers/
├── DeepONet/
│   ├── DeepONet.pdf
│   ├── summary.md
│   ├── scores.md
│   └── metadata.json
├── FNO/
└── ...
```

### 检索策略配置

默认检索策略：
- 8 个核心关键词
- 每个关键词检索 30 篇论文
- 筛选 Top 3 精选论文

修改检索策略：

```python
# 编辑 arxiv-search 技能
KEYWORDS = [
    "keyword1",
    "keyword2",
    # ... 添加更多关键词
]

MAX_RESULTS_PER_KEYWORD = 30  # 每个关键词检索的论文数
TOP_PAPERS_TO_SELECT = 3  # 精选论文数量
```

### 模型配置

编辑 `agent/models.json`：

```json
{
  "providers": {
    "glm": {
      "baseUrl": "http://oneapi-comate.baidu-int.com/v1",
      "apiKey": "your_api_key",
      "api": "openai-completions",
      "models": [
        {
          "id": "glm-4.7-internal",
          "name": "glm Coding",
          "reasoning": false,
          "input": ["text"],
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          },
          "contextWindow": 200000,
          "maxTokens": 8192
        }
      ]
    }
  }
}
```

---

## 配置验证

### 验证环境变量

```bash
# 检查环境变量
echo $BAIDU_API_KEY
echo $COMATE_AUTH_TOKEN

# 或查看 .env 文件
cat ~/.openclaw/.env
```

### 验证知识库配置

```python
from ku_api_client import KuApiClient

client = KuApiClient()
result = client.get_doc(
    repository_guid="your_repository_guid",
    doc_guid="your_parent_doc_guid"
)
print(result)
```

### 验证如流消息配置

```python
from send_message import GroupMessageSender

sender = GroupMessageSender()
result = sender.send_app_message(
    to_users="your_username",
    msg_type="text",
    content="测试消息：PaperAgent 配置正常"
)
print(result)
```

### 验证定时任务

```bash
# 查看所有定时任务
openclaw cron list

# 查看任务详情
openclaw cron list --id <job-id>

# 手动执行任务
openclaw cron run <job-id>
```

---

## 配置备份

### 备份配置文件

```bash
# 备份环境变量
cp ~/.openclaw/.env ~/.openclaw/.env.backup

# 备份 Agent 配置
tar -czf agent_config_backup_$(date +%Y%m%d).tar.gz ~/.openclaw/agents/surrogate-modeling-expert/

# 备份定时任务配置
openclaw cron list > cron_jobs_backup_$(date +%Y%m%d).json
```

### 恢复配置文件

```bash
# 恢复环境变量
cp ~/.openclaw/.env.backup ~/.openclaw/.env

# 恢复 Agent 配置
tar -xzf agent_config_backup_20260302.tar.gz -C ~/.openclaw/agents/

# 恢复定时任务
# 需要手动重新添加
```

---

## 下一步

配置完成后，请参考：

- [QUICKSTART.md](QUICKSTART.md) - 快速入门指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [API_REFERENCE.md](API_REFERENCE.md) - API 参考

---

<div align="center">

**配置完成！现在可以开始使用 PaperAgent 了 🎉**

</div>
