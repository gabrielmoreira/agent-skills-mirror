# 快速入门指南

欢迎使用 PaperAgent - Surrogate Modeling Expert！本指南将帮助你在 5 分钟内完成部署并开始使用。

---

## 📋 前置检查

在开始之前，请确保你已经：

- ✅ 安装了 Python 3.8 或更高版本
- ✅ 安装了 OpenClaw 平台
- ✅ 拥有百度内部账号（用于知识库和如流消息）
- ✅ 有基本的命令行操作经验

---

## 🚀 5分钟快速部署

### 步骤 1: 获取项目代码

```bash
# 克隆项目（如果你有 GitHub 访问权限）
git clone https://github.com/yourusername/PaperAgent_Open.git
cd PaperAgent_Open

# 或者下载 ZIP 压缩包并解压
unzip PaperAgent_Open.zip
cd PaperAgent_Open
```

### 步骤 2: 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**requirements.txt 内容**：
```
requests>=2.28.0
python-dateutil>=2.8.2
```

### 步骤 3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

**.env 文件内容**：
```bash
# 百度智能云 API Key（必需）
BAIDU_API_KEY=your_baidu_api_key_here

# Comate Auth Token（必需，用于知识库和如流消息）
COMATE_AUTH_TOKEN=your_comate_token_here

# SerpAPI Key（可选，用于 Google Scholar 搜索）
SERPAPI_KEY=your_serpapi_key_here

# 百度地图 API Key（可选）
BAIDU_MAP_AK=your_baidu_map_ak_here
```

**获取 API Key 的方法**：

1. **BAIDU_API_KEY**：
   - 访问 https://cloud.baidu.com/
   - 登录后进入控制台
   - 创建应用并获取 API Key

2. **COMATE_AUTH_TOKEN**：
   - 联系你的百度内部管理员获取
   - 或从现有的百度内部工具中获取

3. **SERPAPI_KEY**（可选）：
   - 访问 https://serpapi.com/
   - 注册账号并获取 API Key

### 步骤 4: 部署 Agent 到 OpenClaw

#### 方式 1: 使用 OpenClaw CLI（推荐）

```bash
# 创建新 Agent
openclaw agent create surrogate-modeling-expert

# 复制 Agent 文件
cp -r agent/* ~/.openclaw/agents/surrogate-modeling-expert/
cp -r skills/* ~/.openclaw/agents/surrogate-modeling-expert/skills/

# 验证部署
openclaw agent list
```

#### 方式 2: 手动复制

```bash
# 创建 Agent 目录
mkdir -p ~/.openclaw/agents/surrogate-modeling-expert/skills

# 复制文件
cp agent/AGENT.md ~/.openclaw/agents/surrogate-modeling-expert/
cp agent/README.md ~/.openclaw/agents/surrogate-modeling-expert/
cp agent/models.json ~/.openclaw/agents/surrogate-modeling-expert/

# 复制技能模块
cp -r skills/* ~/.openclaw/agents/surrogate-modeling-expert/skills/
```

### 步骤 5: 配置知识库和如流消息

编辑 `skills/weekly-report/scripts/generate_weekly_report_v2.py`：

```python
# 找到以下配置项并修改

# 知识库配置
self.ku_repo_id = "your_repository_guid"  # 替换为你的知识库ID
self.ku_parent_doc_id = "your_parent_doc_guid"  # 替换为你的父文档ID

# 如流消息接收人
self.recipients = ["your_username"]  # 替换为你的如流用户名
```

**获取知识库 ID 的方法**：

1. 访问百度知识库 https://ku.baidu-int.com/
2. 进入你的知识库
3. 查看浏览器地址栏，URL 格式为：
   ```
   https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/qv-vZnw7HE/jnGipY319RaSyz
   ```
   - `qv-vZnw7HE` 是 repositoryGuid（知识库ID）
   - `jnGipY319RaSyz` 是 parent_doc_guid（父文档ID）

**获取如流用户名的方法**：

1. 登录如流 https://so.baidu-int.com/
2. 查看个人资料
3. 用户名通常是拼音或工号

### 步骤 6: 配置定时任务

使用 OpenClaw 的 cron 功能配置定时任务：

#### 配置每日论文检索（每天 21:00）

```bash
# 创建每日检索任务
openclaw cron add << 'EOF'
{
  "name": "Daily Paper Search - Surrogate Modeling",
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日论文检索任务：检索三维几何代理模型领域的最新论文"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
EOF
```

#### 配置每周报告生成（每周日 10:00）

```bash
# 创建周报生成任务
openclaw cron add << 'EOF'
{
  "name": "Weekly Report - Surrogate Modeling",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * 0",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "生成三维几何代理模型研究周报，创建知识库文档并发送给指定用户"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
EOF
```

#### 验证定时任务

```bash
# 查看所有定时任务
openclaw cron list

# 查看任务详情
openclaw cron list --id <job-id>
```

### 步骤 7: 测试运行

#### 手动触发一次论文检索

在 OpenClaw 对话中输入：

```
帮我检索 geometry-aware neural operator 相关的最新论文
```

或者：

```
执行每日论文检索任务
```

#### 检查运行结果

```bash
# 查看论文目录
ls ~/.openclaw/workspace/3d_surrogate_proj/papers/

# 查看最新论文的总结
cat ~/.openclaw/workspace/3d_surrogate_proj/papers/*/summary.md | head -50

# 查看检索日志
cat ~/.openclaw/workspace/3d_surrogate_proj/search_logs/*.json
```

---

## 📖 基本使用

### 手动触发任务

#### 触发论文检索

在 OpenClaw 对话中输入：

```
帮我检索 [关键词] 相关的最新论文
```

示例：
```
帮我检索 neural operator PDE 相关的最新论文
```

#### 触发周报生成

在 OpenClaw 对话中输入：

```
生成三维几何代理模型研究周报
```

### 查看结果

#### 查看论文总结

```bash
# 列出所有论文
ls ~/.openclaw/workspace/3d_surrogate_proj/papers/

# 查看某篇论文的总结
cat ~/.openclaw/workspace/3d_surrogate_proj/papers/DeepONet/summary.md

# 查看某篇论文的评分
cat ~/.openclaw/workspace/3d_surrogate_proj/papers/DeepONet/scores.md

# 查看论文元数据
cat ~/.openclaw/workspace/3d_surrogate_proj/papers/DeepONet/metadata.json
```

#### 查看周报

```bash
# 列出所有周报
ls ~/.openclaw/workspace/3d_surrogate_proj/weekly_reports/

# 查看最新周报
cat ~/.openclaw/workspace/3d_surrogate_proj/weekly_reports/*.md
```

### 管理定时任务

```bash
# 查看所有定时任务
openclaw cron list

# 禁用任务
openclaw cron update <job-id> --patch '{"enabled": false}'

# 启用任务
openclaw cron update <job-id> --patch '{"enabled": true}'

# 立即执行任务
openclaw cron run <job-id>

# 删除任务
openclaw cron remove <job-id>
```

---

## ⚙️ 自定义配置

### 修改检索关键词

编辑 `agent/AGENT.md`，找到"检索关键词库"部分，修改或添加关键词：

```markdown
### 核心关键词
- geometry-aware neural operator
- neural operator 3D mesh
- operator learning arbitrary geometry
- 添加你的关键词...
```

### 修改评分标准

编辑 `skills/paper-review/SKILL.md`，找到"评分标准详细说明"部分，调整评分标准。

### 修改周报格式

编辑 `skills/weekly-report/scripts/generate_weekly_report_v2.py`，找到周报生成函数，修改 Markdown 格式。

---

## 🔍 故障排查

### 问题 1: Agent 无法启动

**症状**：OpenClaw 中找不到 Agent

**解决方案**：
```bash
# 检查 Agent 文件是否存在
ls ~/.openclaw/agents/surrogate-modeling-expert/

# 重新复制文件
cp -r agent/* ~/.openclaw/agents/surrogate-modeling-expert/

# 重启 OpenClaw
openclaw gateway restart
```

### 问题 2: 论文检索失败

**症状**：检索时提示错误

**解决方案**：
```bash
# 检查网络连接
ping arxiv.org

# 检查 arXiv API 是否可访问
curl http://export.arxiv.org/api/query?search_query=all:neural+operator

# 查看检索日志
cat ~/.openclaw/workspace/3d_surrogate_proj/search_logs/*.json
```

### 问题 3: 知识库文档创建失败

**症状**：周报生成时提示知识库错误

**解决方案**：
```bash
# 检查 COMATE_AUTH_TOKEN 是否正确
echo $COMATE_AUTH_TOKEN

# 检查知识库 ID 是否正确
# 访问知识库 URL，确认 repositoryGuid 和 parent_doc_guid

# 测试知识库 API 连接
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/gem/.openclaw/skills/ku-doc-manage/scripts')
from ku_api_client import KuApiClient

client = KuApiClient()
result = client.get_doc(
    repository_guid="your_repository_guid",
    doc_guid="your_parent_doc_guid"
)
print(result)
EOF
```

### 问题 4: 如流消息发送失败

**症状**：周报生成成功但没有收到如流消息

**解决方案**：
```bash
# 检查用户名是否正确
# 确认用户名是拼音或工号，不是邮箱

# 测试如流消息发送
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/gem/.openclaw/skills/so-send-message/scripts')
from send_message import GroupMessageSender

sender = GroupMessageSender()
result = sender.send_app_message(
    to_users="your_username",
    msg_type="text",
    content="测试消息：PaperAgent 运行正常"
)
print(result)
EOF
```

### 问题 5: 定时任务不执行

**症状**：定时任务配置了但没有自动执行

**解决方案**：
```bash
# 检查任务状态
openclaw cron list

# 确认任务是否启用（enabled: true）

# 检查时区配置
# 确保使用正确的时区（如 Asia/Shanghai）

# 查看任务运行日志
openclaw cron runs <job-id>

# 手动触发任务测试
openclaw cron run <job-id>
```

---

## 📚 下一步

现在你已经成功部署了 PaperAgent，接下来可以：

1. **阅读详细文档**：
   - [INSTALLATION.md](INSTALLATION.md) - 详细安装指南
   - [CONFIGURATION.md](CONFIGURATION.md) - 配置说明
   - [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
   - [API_REFERENCE.md](API_REFERENCE.md) - API 参考

2. **自定义配置**：
   - 修改检索关键词
   - 调整评分标准
   - 自定义周报格式
   - 添加新的技能模块

3. **扩展功能**：
   - 支持更多论文数据库
   - 添加可视化功能
   - 集成其他外部服务

4. **贡献代码**：
   - 报告 Bug
   - 提出新功能建议
   - 提交 Pull Request

---

## 💡 常见问题

### Q1: PaperAgent 可以检索哪些领域的论文？

A: PaperAgent 专注于三维几何代理模型领域，包括：
- 神经算子学习（Neural Operator Learning）
- PDE 求解（Partial Differential Equations）
- 物理信息神经网络（Physics-Informed Neural Networks）
- 计算流体力学代理模型（CFD Surrogate Models）
- 几何深度学习（Geometric Deep Learning）

你可以通过修改 `agent/AGENT.md` 中的关键词来扩展到其他领域。

### Q2: 每天会检索多少篇论文？

A: 默认情况下，每天会检索约 3 篇精选论文。检索流程如下：
1. 使用 8 个核心关键词检索 arXiv
2. 每个关键词检索 30 篇论文
3. 智能去重
4. 基于相关性评分筛选 Top 3

你可以修改检索策略来调整数量。

### Q3: 评分系统是如何工作的？

A: PaperAgent 使用四维评分系统：
- 工程应用价值（1-10分）
- 网络架构创新（1-10分）
- 理论贡献（1-10分）
- 结果可靠性（1-10分）

最终评分 = (四维基础评分 × 0.9) + (影响力评分 × 0.1)

影响力评分包含 Date-Citation 权衡机制，公平对比不同发表时间的论文。

详见 [docs/evaluation_system.md](docs/evaluation_system.md)。

### Q4: 我需要提供哪些 API Key？

A: 必需的 API Key：
- **BAIDU_API_KEY**：用于百度智能云服务
- **COMATE_AUTH_TOKEN**：用于知识库和如流消息

可选的 API Key：
- **SERPAPI_KEY**：用于 Google Scholar 搜索
- **BAIDU_MAP_AK**：用于百度地图服务

### Q5: 如何备份我的数据？

A: PaperAgent 的数据存储在 `~/.openclaw/workspace/3d_surrogate_proj/` 目录下，你可以：

```bash
# 备份整个工作区
tar -czf paperagent_backup_$(date +%Y%m%d).tar.gz ~/.openclaw/workspace/3d_surrogate_proj/

# 备份论文数据
tar -czf papers_backup_$(date +%Y%m%d).tar.gz ~/.openclaw/workspace/3d_surrogate_proj/papers/

# 备份周报
tar -czf reports_backup_$(date +%Y%m%d).tar.gz ~/.openclaw/workspace/3d_surrogate_proj/weekly_reports/
```

---

## 🆘 获取帮助

如果遇到问题，可以通过以下方式获取帮助：

1. **查看文档**：
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查指南
   - [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

2. **提交 Issue**：
   - 访问 https://github.com/yourusername/PaperAgent_Open/issues
   - 描述问题并提供详细信息

3. **参与讨论**：
   - 访问 https://github.com/yourusername/PaperAgent_Open/discussions
   - 提问或分享使用经验

---

<div align="center">

**恭喜！你已经成功部署了 PaperAgent！**

现在可以开始自动化你的论文调研工作了 🎉

</div>
