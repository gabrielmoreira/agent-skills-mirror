# 详细安装指南

本文档提供 PaperAgent 的详细安装步骤，包括各种环境下的安装方法和常见问题的解决方案。

---

## 📋 目录

- [系统要求](#系统要求)
- [安装方式](#安装方式)
  - [方式 1: 使用 OpenClaw CLI（推荐）](#方式-1-使用-openclaw-cli推荐)
  - [方式 2: 手动安装](#方式-2-手动安装)
  - [方式 3: Docker 安装](#方式-3-docker-安装)
- [依赖安装](#依赖安装)
- [环境配置](#环境配置)
- [验证安装](#验证安装)
- [常见问题](#常见问题)
- [卸载](#卸载)

---

## 系统要求

### 最低要求

- **操作系统**: Linux, macOS, Windows (WSL2)
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM（推荐 8GB+）
- **磁盘空间**: 500MB 可用空间（不含论文数据）
- **网络**: 稳定的互联网连接

### 推荐配置

- **操作系统**: Ubuntu 20.04+, macOS 12+, Windows 10/11 (WSL2)
- **Python**: 3.10 或 3.11
- **内存**: 16GB RAM
- **磁盘空间**: 10GB+ 可用空间
- **网络**: 高速互联网连接

### 软件依赖

- **OpenClaw**: v1.0.0 或更高版本
- **Git**: 2.20 或更高版本
- **pip**: 20.0 或更高版本

---

## 安装方式

### 方式 1: 使用 OpenClaw CLI（推荐）

这是最简单快捷的安装方式，适合大多数用户。

#### 步骤 1: 确认 OpenClaw 已安装

```bash
# 检查 OpenClaw 版本
openclaw --version

# 如果未安装，请先安装 OpenClaw
# 参考 https://docs.openclaw.ai/
```

#### 步骤 2: 克隆或下载项目

```bash
# 克隆项目（推荐）
git clone https://github.com/yourusername/PaperAgent_Open.git
cd PaperAgent_Open

# 或下载 ZIP 压缩包
wget https://github.com/yourusername/PaperAgent_Open/archive/refs/heads/main.zip
unzip main.zip
cd PaperAgent_Open-main
```

#### 步骤 3: 安装 Python 依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤 4: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

填写以下必需的环境变量：

```bash
# 百度智能云 API Key（必需）
BAIDU_API_KEY=your_baidu_api_key_here

# Comate Auth Token（必需）
COMATE_AUTH_TOKEN=your_comate_token_here

# SerpAPI Key（可选）
SERPAPI_KEY=your_serpapi_key_here

# 百度地图 API Key（可选）
BAIDU_MAP_AK=your_baidu_map_ak_here
```

#### 步骤 5: 部署 Agent 到 OpenClaw

```bash
# 创建新 Agent
openclaw agent create surrogate-modeling-expert

# 复制 Agent 文件
cp -r agent/* ~/.openclaw/agents/surrogate-modeling-expert/
cp -r skills/* ~/.openclaw/agents/surrogate-modeling-expert/skills/

# 验证部署
openclaw agent list
```

#### 步骤 6: 配置知识库和如流消息

编辑 `~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py`：

```python
# 找到以下配置项并修改

# 知识库配置
self.ku_repo_id = "your_repository_guid"  # 替换为你的知识库ID
self.ku_parent_doc_id = "your_parent_doc_guid"  # 替换为你的父文档ID

# 如流消息接收人
self.recipients = ["your_username"]  # 替换为你的如流用户名
```

#### 步骤 7: 配置定时任务

```bash
# 配置每日论文检索（每天 21:00）
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

# 配置每周报告生成（每周日 10:00）
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

# 验证定时任务
openclaw cron list
```

---

### 方式 2: 手动安装

如果你不使用 OpenClaw CLI，可以手动安装。

#### 步骤 1: 准备工作目录

```bash
# 创建工作目录
mkdir -p ~/.openclaw/agents/surrogate-modeling-expert/skills
mkdir -p ~/.openclaw/workspace/3d_surrogate_proj/{papers,weekly_reports,search_logs,scripts}
```

#### 步骤 2: 复制 Agent 文件

```bash
# 复制 Agent 定义
cp agent/AGENT.md ~/.openclaw/agents/surrogate-modeling-expert/
cp agent/README.md ~/.openclaw/agents/surrogate-modeling-expert/
cp agent/models.json ~/.openclaw/agents/surrogate-modeling-expert/

# 复制技能模块
cp -r skills/arxiv-search ~/.openclaw/agents/surrogate-modeling-expert/skills/
cp -r skills/paper-review ~/.openclaw/agents/surrogate-modeling-expert/skills/
cp -r skills/weekly-report ~/.openclaw/agents/surrogate-modeling-expert/skills/
cp -r skills/semantic-scholar ~/.openclaw/agents/surrogate-modeling-expert/skills/
```

#### 步骤 3: 安装 Python 依赖

```bash
# 创建虚拟环境
python3 -m venv ~/.openclaw/venv
source ~/.openclaw/venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 步骤 4: 配置环境变量

```bash
# 创建 .env 文件
cat > ~/.openclaw/.env << 'EOF'
BAIDU_API_KEY=your_baidu_api_key_here
COMATE_AUTH_TOKEN=your_comate_token_here
SERPAPI_KEY=your_serpapi_key_here
BAIDU_MAP_AK=your_baidu_map_ak_here
EOF

# 编辑 .env 文件
nano ~/.openclaw/.env
```

#### 步骤 5: 配置知识库和如流消息

同方式 1 的步骤 6。

#### 步骤 6: 配置定时任务

同方式 1 的步骤 7。

---

### 方式 3: Docker 安装

使用 Docker 可以确保环境一致性，适合生产环境部署。

#### 步骤 1: 创建 Dockerfile

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建工作目录
RUN mkdir -p /app/workspace/3d_surrogate_proj/{papers,weekly_reports,search_logs,scripts}

# 设置环境变量
ENV PYTHONPATH=/app
ENV OPENCLAW_WORKSPACE=/app/workspace

# 暴露端口（如果需要）
# EXPOSE 8080

# 启动命令
CMD ["python", "-m", "openclaw.cli"]
```

#### 步骤 2: 创建 docker-compose.yml

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  paperagent:
    build: .
    container_name: paperagent
    volumes:
      - ./workspace:/app/workspace/3d_surrogate_proj
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - BAIDU_API_KEY=${BAIDU_API_KEY}
      - COMATE_AUTH_TOKEN=${COMATE_AUTH_TOKEN}
      - SERPAPI_KEY=${SERPAPI_KEY}
      - BAIDU_MAP_AK=${BAIDU_MAP_AK}
    restart: unless-stopped
    # ports:
    #   - "8080:8080"
```

#### 步骤 3: 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 依赖安装

### Python 依赖

创建 `requirements.txt`：

```
requests>=2.28.0
python-dateutil>=2.8.2
```

安装依赖：

```bash
pip install -r requirements.txt
```

### OpenClaw 依赖

PaperAgent 依赖 OpenClaw 平台，请确保已安装：

```bash
# 检查 OpenClaw 安装
openclaw --version

# 如果未安装，请参考官方文档安装
# https://docs.openclaw.ai/
```

### 可选依赖

如果你需要使用额外的功能，可以安装以下依赖：

```bash
# 用于 PDF 处理
pip install PyPDF2

# 用于数据可视化
pip install matplotlib

# 用于数据分析
pip install pandas numpy

# 用于 Web 界面
pip install flask
```

---

## 环境配置

### 环境变量说明

创建 `.env` 文件：

```bash
# 百度智能云 API Key（必需）
# 用于访问百度智能云 API 服务
BAIDU_API_KEY=your_baidu_api_key_here

# Comate Auth Token（必需）
# 用于访问百度知识库和如流消息
COMATE_AUTH_TOKEN=your_comate_token_here

# SerpAPI Key（可选）
# 用于 Google Scholar 搜索
SERPAPI_KEY=your_serpapi_key_here

# 百度地图 API Key（可选）
# 用于百度地图服务
BAIDU_MAP_AK=your_baidu_map_ak_here
```

### 获取 API Key 的方法

#### BAIDU_API_KEY

1. 访问 https://cloud.baidu.com/
2. 登录百度账号
3. 进入控制台
4. 创建应用
5. 获取 API Key

#### COMATE_AUTH_TOKEN

1. 联系你的百度内部管理员
2. 或从现有的百度内部工具中获取
3. Token 格式：`Bearer-eyJ0eXAiOiJKV1QiLCJhbGc...`

#### SERPAPI_KEY

1. 访问 https://serpapi.com/
2. 注册账号
3. 进入控制台
4. 获取 API Key

#### BAIDU_MAP_AK

1. 访问 https://lbsyun.baidu.com/
2. 登录百度账号
3. 创建应用
4. 选择 Web 服务 API
5. 获取 AK（Access Key）

### 知识库配置

编辑 `~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py`：

```python
# 知识库配置
self.ku_repo_id = "your_repository_guid"  # 你的知识库ID
self.ku_parent_doc_id = "your_parent_doc_guid"  # 你的父文档ID
```

**获取知识库 ID**：

1. 访问百度知识库 https://ku.baidu-int.com/
2. 进入你的知识库
3. 查看浏览器地址栏
4. URL 格式：`https://ku.baidu-int.com/knowledge/HFVrC7hq1Q/pKzJfZczuc/qv-vZnw7HE/jnGipY319RaSyz`
   - `qv-vZnw7HE` 是 repositoryGuid（知识库ID）
   - `jnGipY319RaSyz` 是 parent_doc_guid（父文档ID）

### 如流消息配置

编辑 `~/.openclaw/agents/surrogate-modeling-expert/skills/weekly-report/scripts/generate_weekly_report_v2.py`：

```python
# 如流消息接收人
self.recipients = ["username1", "username2"]  # 替换为你的用户名
```

**获取如流用户名**：

1. 登录如流 https://so.baidu-int.com/
2. 查看个人资料
3. 用户名通常是拼音或工号

---

## 验证安装

### 验证 Agent 部署

```bash
# 列出所有 Agent
openclaw agent list

# 应该看到 surrogate-modeling-expert
```

### 验证技能模块

```bash
# 检查技能文件是否存在
ls ~/.openclaw/agents/surrogate-modeling-expert/skills/

# 应该看到以下目录：
# arxiv-search/
# paper-review/
# weekly-report/
# semantic-scholar/
```

### 验证环境变量

```bash
# 检查环境变量是否设置
echo $BAIDU_API_KEY
echo $COMATE_AUTH_TOKEN

# 或查看 .env 文件
cat ~/.openclaw/.env
```

### 验证定时任务

```bash
# 列出所有定时任务
openclaw cron list

# 应该看到以下任务：
# Daily Paper Search - Surrogate Modeling
# Weekly Report - Surrogate Modeling
```

### 测试运行

```bash
# 手动触发一次论文检索
# 在 OpenClaw 对话中输入：
# "执行每日论文检索任务"

# 检查论文目录
ls ~/.openclaw/workspace/3d_surrogate_proj/papers/

# 查看检索日志
cat ~/.openclaw/workspace/3d_surrogate_proj/search_logs/*.json
```

---

## 常见问题

### 问题 1: Python 版本不兼容

**症状**：
```
SyntaxError: invalid syntax
```

**解决方案**：
```bash
# 检查 Python 版本
python3 --version

# 如果版本低于 3.8，请升级
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10

# macOS
brew install python@3.10

# Windows
# 从 https://www.python.org/downloads/ 下载安装
```

### 问题 2: pip 安装失败

**症状**：
```
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案**：
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 问题 3: 权限不足

**症状**：
```
Permission denied: '/home/user/.openclaw/agents/surrogate-modeling-expert'
```

**解决方案**：
```bash
# 使用 sudo
sudo cp -r agent/* ~/.openclaw/agents/surrogate-modeling-expert/

# 或修改目录权限
sudo chown -R $USER:$USER ~/.openclaw/
```

### 问题 4: OpenClaw 命令找不到

**症状**：
```
openclaw: command not found
```

**解决方案**：
```bash
# 检查 OpenClaw 是否安装
which openclaw

# 如果未安装，请先安装 OpenClaw
# 参考 https://docs.openclaw.ai/

# 如果已安装但找不到，检查 PATH
echo $PATH

# 添加 OpenClaw 到 PATH
export PATH=$PATH:/path/to/openclaw/bin

# 或创建符号链接
sudo ln -s /path/to/openclaw/bin/openclaw /usr/local/bin/openclaw
```

### 问题 5: Docker 容器无法启动

**症状**：
```
ERROR: for paperagent  Cannot start service paperagent: ...
```

**解决方案**：
```bash
# 查看容器日志
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache

# 检查端口占用
sudo lsof -i :8080

# 清理容器和镜像
docker-compose down -v
docker system prune -a
```

---

## 卸载

### 卸载 Agent

```bash
# 删除 Agent 目录
rm -rf ~/.openclaw/agents/surrogate-modeling-expert/

# 删除工作目录
rm -rf ~/.openclaw/workspace/3d_surrogate_proj/

# 删除定时任务
openclaw cron list | grep "Surrogate Modeling" | awk '{print $1}' | xargs -I {} openclaw cron remove {}
```

### 卸载 Docker 版本

```bash
# 停止并删除容器
docker-compose down -v

# 删除镜像
docker rmi paperagent

# 删除数据卷
docker volume rm paperagent_workspace
docker volume rm paperagent_logs
```

### 完全清理

```bash
# 删除虚拟环境
rm -rf ~/.openclaw/venv

# 删除配置文件
rm ~/.openclaw/.env

# 删除项目目录
rm -rf /path/to/PaperAgent_Open
```

---

## 下一步

安装完成后，请参考：

- [QUICKSTART.md](QUICKSTART.md) - 快速入门指南
- [CONFIGURATION.md](CONFIGURATION.md) - 配置说明
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查

---

<div align="center">

**安装完成！现在可以开始使用 PaperAgent 了 🎉**

</div>
