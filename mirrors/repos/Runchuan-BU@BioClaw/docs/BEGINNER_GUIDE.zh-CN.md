# BioClaw 新手详细使用指南

这份文档面向：

- 第一次接触命令行、Docker、环境变量的用户
- 能跑起 BioClaw，但不清楚 `.env`、workspace、挂载、allowlist 分别是什么的用户
- 想让 BioClaw 访问宿主机某个目录，但不知道该改哪里的人
- 想知道 BioClaw 到底能干什么、怎么用它跑真实生物分析的人

如果你只想先把 BioClaw 跑起来，不想理解全部内部机制，直接按照第一部分的 **5 分钟快速上手** 走完就行。后面的章节可以等到遇到具体问题再回来查。

---

## 目录

**第一部分：最快 5 分钟上手**
- [1. 前置清单（三件东西）](#1-前置清单三件东西)
- [2. 第一次跑起来的完整命令流程](#2-第一次跑起来的完整命令流程)
- [3. 让 BioClaw 干第一件事](#3-让-bioclaw-干第一件事)

**第二部分：你需要先理解的几个基础概念**
- [4. 一句话介绍 BioClaw](#4-一句话介绍-bioclaw)
- [5. 终端、命令行、shell 是什么](#5-终端命令行shell-是什么)
- [6. Docker、容器、镜像是什么](#6-docker容器镜像是什么)
- [7. API Key / provider / 模型是什么](#7-api-keyprovider模型是什么)
- [8. workspace 是什么](#8-workspace-是什么)
- [9. skill 是什么](#9-skill-是什么)
- [10. MCP 是什么](#10-mcp-是什么)
- [11. 挂载和 allowlist 是什么（用"U 盘"类比）](#11-挂载和-allowlist-是什么用u-盘类比)

**第三部分：安装和配置**
- [12. 系统要求和各 OS 安装步骤](#12-系统要求和各-os-安装步骤)
- [13. 先记住这 4 个关键位置](#13-先记住这-4-个关键位置)
- [14. `.env` 配置详解](#14-env-配置详解)

**第四部分：日常使用**
- [15. 启动和停止 BioClaw](#15-启动和停止-bioclaw)
- [16. 聊天里的常用 slash commands](#16-聊天里的常用-slash-commands)
- [17. 大多数用户根本不需要额外挂载](#17-大多数用户根本不需要额外挂载)
- [18. 切换 provider 和 model](#18-切换-provider-和-model)
- [19. workspace 详解](#19-workspace-详解)

**第五部分：常见使用场景实战**
- [20. 分析一个上传的 CSV 文件](#20-分析一个上传的-csv-文件)
- [21. 跑 BLAST 同源搜索](#21-跑-blast-同源搜索)
- [22. Bulk RNA-seq 差异表达分析](#22-bulk-rna-seq-差异表达分析)
- [23. 单细胞 RNA-seq 分析](#23-单细胞-rna-seq-分析)
- [24. 查询 PDB / UniProt / AlphaFold 结构](#24-查询-pdb--uniprot--alphafold-结构)
- [25. PubMed 文献搜索 + 综述](#25-pubmed-文献搜索--综述)
- [26. 生成技术报告（Typst / SEC）](#26-生成技术报告typst--sec)
- [27. 分析 SDS-PAGE 凝胶图](#27-分析-sds-page-凝胶图)
- [28. 让 BioClaw 通过 SSH 连接远程服务器 / HPC](#28-让-bioclaw-通过-ssh-连接远程服务器--hpc)

**第六部分：高级——挂载宿主机目录**
- [29. 什么时候需要 allowlist](#29-什么时候需要-allowlist)
- [30. 第一次配置 allowlist（一步一步来）](#30-第一次配置-allowlist一步一步来)
- [31. 额外挂载到底挂到哪里](#31-额外挂载到底挂到哪里)
- [32. 把宿主机目录挂给某个 workspace](#32-把宿主机目录挂给某个-workspace)
- [33. 如何验证挂载是否成功](#33-如何验证挂载是否成功)
- [34. 推荐的最小可用配置示例](#34-推荐的最小可用配置示例)

**第七部分：遇到问题怎么办**
- [35. 新手最容易卡住的点](#35-新手最容易卡住的点)
- [36. 遇到问题的排障顺序](#36-遇到问题的排障顺序)
- [37. 诊断命令速查](#37-诊断命令速查)
- [38. 去哪里寻求帮助](#38-去哪里寻求帮助)

**第八部分：推荐路径 + 相关文档**
- [39. 三条推荐的新手使用路径](#39-三条推荐的新手使用路径)
- [40. 相关文档](#40-相关文档)

---

# 第一部分：最快 5 分钟上手

## 1. 前置清单（三件东西）

开始之前，你的电脑上需要这三样东西：

| 东西 | 作用 | 检查命令 |
|---|---|---|
| **Node.js 20+** | BioClaw 用它启动消息通道和 Web UI | `node -v` 显示 `v20.x.x` 或更高 |
| **Docker** | BioClaw 所有生物分析都跑在 Docker 容器里 | `docker -v` 显示 `Docker version 20.x` 或更高 |
| **一个 API Key** | 调用大模型的凭据（Anthropic 或 OpenRouter 等） | 去 [anthropic.com](https://console.anthropic.com/) 或 [openrouter.ai](https://openrouter.ai/keys) 申请 |

如果这三个还没准备好，跳到 [第 12 节](#12-系统要求和各-os-安装步骤) 看安装步骤。

> **Windows 用户：** 请先看 [docs/WINDOWS.zh-CN.md](./WINDOWS.zh-CN.md)。BioClaw 在 Windows 上需要 WSL2 环境，直接在 Windows PowerShell / cmd 里跑不起来。

## 2. 第一次跑起来的完整命令流程

打开终端（macOS/Linux: Terminal；Windows: 在 WSL2 里的 Ubuntu），**按顺序**逐条执行：

```bash
# 1) 把代码克隆到本地（随便找个文件夹）
git clone https://github.com/Runchuan-BU/BioClaw.git
cd BioClaw

# 2) 装 Node 依赖（第一次需要几分钟）
npm install

# 3) 复制一份环境变量模板
cp .env.example .env

# 4) 打开 .env 文件，填入 API key（见下方说明）
#    Linux / macOS 用 nano 或 vim：
nano .env
#    如果你熟悉 VS Code，也可以 code .env
```

在 `.env` 里，找到 `ANTHROPIC_API_KEY=` 这一行，替换成你真正的 key：

```bash
ANTHROPIC_API_KEY=sk-ant-api03-真实的key
```

保存退出（nano 里是 `Ctrl+O`、`Enter`、`Ctrl+X`）。

继续：

```bash
# 5) 构建 BioClaw 的容器镜像（第一次需要 5-10 分钟）
docker build -t bioclaw-agent:latest container/

# 6) 启动 BioClaw 本地网页版
npm run web
```

看到类似这样的输出就说明启动成功了：

```
[bioclaw] Local web UI listening on http://localhost:3000
```

## 3. 让 BioClaw 干第一件事

1. 打开浏览器，访问 `http://localhost:3000`
2. 在聊天框里输入一句问候，确认能收到 Agent 的回复
3. 把一个 CSV 或 FASTA 文件拖进聊天框上传
4. 问 BioClaw：

   ```text
   帮我看看这个文件的内容，前 10 行是什么？
   ```

5. 等 Agent 回复。这时它会在容器里跑 `head`、`cat`、或 Python 读取你的文件。

**恭喜，你已经完整地用了一次 BioClaw。** 到这一步，你没有碰过 allowlist、挂载、SQL。那些都是后面才需要的高级功能。

---

# 第二部分：你需要先理解的几个基础概念

## 4. 一句话介绍 BioClaw

> **BioClaw 是一个把生物信息学分析"藏"在聊天里的 AI 助手。**
>
> 你在聊天窗口里提问或上传文件，它在后台的 Docker 容器里帮你跑 BLAST、RNA-seq、BWA、samtools、scanpy、PyMOL 等工具，然后把结果用图表或报告发回给你。

所以用 BioClaw 的心智模型不是"装一个软件"，而是"打开一个窗口让一个懂生物信息学的助手在后面帮你干活"。

## 5. 终端、命令行、shell 是什么

如果你从没听过这些词，不用紧张，关键点：

- **终端（Terminal）** 就是一个让你能敲命令的黑色窗口
- macOS：在"启动台"里搜 `Terminal`；或按 `⌘+Space` 搜 `Terminal`
- Linux：按 `Ctrl+Alt+T`
- Windows：装好 WSL2 后，在"开始菜单"搜 `Ubuntu`

所有这份文档里带 `$` 或出现在代码块里的命令，都是在终端里敲的。不需要你从头学 bash，只要能**复制粘贴并回车**就行。

几个最基础的命令：

| 命令 | 意思 |
|---|---|
| `pwd` | 我现在在哪个文件夹？ |
| `ls` | 列出当前文件夹里的东西 |
| `cd 路径` | 切换文件夹 |
| `cd ..` | 回到上一级文件夹 |
| `cat 文件名` | 打印文件内容 |
| `Ctrl+C` | 中止当前正在跑的命令 |

## 6. Docker、容器、镜像是什么

用一个类比：

- **镜像（image）** = 一个打包好的"环境光盘"，里面有 Python、BLAST、samtools 等一堆生物信息学工具
- **容器（container）** = 把这张"光盘"实际跑起来的那个进程。它是隔离的，不会污染你的宿主机
- **Docker** = 管理这些镜像和容器的软件

BioClaw 的生物分析**全部**都跑在容器里。这么做的好处：

- 你宿主机不用装 BLAST、samtools、scanpy 这一整套工具
- 分析环境跟你本机环境隔离，不会互相干扰
- 换台机器也能一致复现

你只要记住：`docker build` 负责造镜像，`docker run` 负责起容器。BioClaw 启动时会自动起容器，你平时**基本不需要自己碰 Docker 命令**，除非要排障。

## 7. API Key / provider / 模型是什么

- **provider（服务商）** = 提供大模型的公司或平台。BioClaw 支持 **Anthropic**、**OpenRouter**、**OpenAI-compatible**、**Codex CLI** 四种
- **API Key** = 你在这家服务商的"通行证"。长得像 `sk-ant-xxxx` 或 `sk-or-v1-xxxx`，填到 `.env` 里
- **模型** = 服务商提供的具体某个大模型，比如 `claude-opus-4`、`gemini-2.5-flash`、`deepseek-chat-v3.1`

BioClaw 的聊天线程可以**在不同 provider/模型之间切换**，配置好多个 key 之后，在聊天里输 `/provider switch openrouter`、`/model switch google/gemini-2.5-flash` 就能换。

**API Key 怎么申请：**

| provider | 链接 | 备注 |
|---|---|---|
| Anthropic | [console.anthropic.com](https://console.anthropic.com/) | Claude 原厂，质量最好，海外信用卡 |
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) | 一个 key 能调 Claude / Gemini / DeepSeek / GPT 等几十个模型，支持国内支付 |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | 国产，支持微信/支付宝付费 |

## 8. workspace 是什么

**workspace（工作区）** 是一个文件夹，它扮演"当前这个聊天 / 这个群"的工作目录。

- 你上传的文件都进入某个 workspace
- Agent 跑分析时默认的输入输出也在那里
- 不同聊天 / 不同群可以用不同的 workspace，互相隔离

在宿主机上，workspace 的路径通常是：

```
BioClaw/groups/<workspace-name>/
```

在容器里，它被挂进：

```
/workspace/group
```

所以你看 Agent 说"文件在 `/workspace/group/xxx.csv`"，意思就是你上传的 `xxx.csv` 在 `BioClaw/groups/<工作区名>/xxx.csv`。

## 9. skill 是什么

**skill = BioClaw 预装的某一类工作流。** 每个 skill 是一份 `SKILL.md`，告诉 Agent："遇到 xxx 场景时该用这些工具、按这些步骤走"。

BioClaw 自带 **40+ 个生物学 skill**，覆盖：

- **序列 / 数据库**：BLAST 搜索、查 UniProt / PDB / AlphaFold / KEGG / Reactome / ClinVar / GEO / InterPro / Ensembl / OpenTarget
- **组学分析**：bulk RNA-seq 差异表达、单细胞 RNA-seq、ATAC-seq、ChIP-seq、宏基因组、蛋白组
- **可视化 / 报告**：高质量图表（火山图、热图、散点图）、PPT 自动生成、手稿大纲/草稿、Typst 技术报告
- **湿实验辅助**：SDS-PAGE 凝胶图分析、PubMed 文献检索、创新性检查
- **系统 / 元信息**：任务路由、数据集发现、人工 feedback 审批

**好消息是：你不需要背这些 skill 的名字。** Agent 会根据你的问题自动挑合适的 skill 用。你要做的只是**清楚地描述你的任务**。

在聊天里输 `/skills` 可以看到所有已安装 skill 的列表。

另外还有 [**Bioclaw_Skills_Hub**](https://github.com/zongtingwei/Bioclaw_Skills_Hub) 里有 70+ 个社区共享的额外 skill，Agent 会在需要时动态拉取。

## 10. MCP 是什么

**MCP (Model Context Protocol)** 是 BioClaw 内部用来让 Agent 调用工具的协议。

**你不用管。** 它完全是内部机制，开发者才需要碰。你不需要配置 MCP，就像用微信聊天不需要懂 TCP/IP 一样。

唯一可能你会在文档里看到 MCP 这个词的地方是 `send_image` / `send_file` 这类"Agent 主动发图/发文件"的能力——它们底层用 MCP 实现，你直接让 Agent 发就行。

## 11. 挂载和 allowlist 是什么（用"U 盘"类比）

这是很多新手卡住的地方。用一个类比来讲：

- **容器**就像一台隔离的、干净的电脑
- **挂载（mount）** 就像往这台电脑上**插 U 盘**——把你宿主机的某个文件夹"插"进容器，让容器能看到你宿主机的真实文件
- **allowlist**（允许清单）就像**一张审批表**——你得先在表上登记好"哪些文件夹允许被插成 U 盘"，然后才能真插上去。没登记的一律不行

为什么要有 allowlist？**因为挂载是危险动作**：
- 如果你不小心把 `~/.ssh` 挂进去，Agent 就能读你的 SSH 私钥
- 如果你把 `/` 挂进去，Agent 就能看你整个硬盘

所以 BioClaw 故意设计成：默认只有你"填过表"的目录才能挂。这就是 `~/.config/bioclaw/mount-allowlist.json` 的作用。

**但是——** 很多新手根本不需要挂载。如果你只是从网页上传文件让 BioClaw 分析，你**不需要** allowlist。详见 [第 17 节](#17-大多数用户根本不需要额外挂载)。

---

# 第三部分：安装和配置

## 12. 系统要求和各 OS 安装步骤

### 12.1 macOS

**需要：** macOS 12 以上，CPU 随便（M1/M2/M3/Intel 都行）

```bash
# 装 Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 装 Node.js 20
brew install node@20

# 装 Docker Desktop
brew install --cask docker

# 启动 Docker Desktop（从应用程序启动台打开）
# 第一次启动会要求登录 Docker ID 或跳过
```

验证：

```bash
node -v     # 应该显示 v20.x.x
docker -v   # 应该显示 Docker version 24.x 之类
```

### 12.2 Linux (Ubuntu / Debian)

```bash
# 装 Node.js 20（用 NodeSource 官方仓库）
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 装 Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
# 重新登录一次终端让权限生效，或者临时：
newgrp docker
```

验证同上。

### 12.3 Windows

Windows **不能**直接跑 BioClaw。必须先装 WSL2 + Ubuntu，然后在 Ubuntu 里按 12.2 步骤来。

详细步骤见 [docs/WINDOWS.zh-CN.md](./WINDOWS.zh-CN.md)。

### 12.4 HPC / 集群（没有 Docker 权限）

BioClaw 支持 **Apptainer/Singularity** 作为 Docker 替代，详见 [docs/APPTAINER.md](./APPTAINER.md) 和 [docs/CLUSTER_DEPLOYMENT.zh-CN.md](./CLUSTER_DEPLOYMENT.zh-CN.md)。

## 13. 先记住这 4 个关键位置

假设你 clone 的 BioClaw 在：

```bash
/path/to/BioClaw
```

那你最常接触的是下面 4 个位置：

1. **项目根目录**

   就是 `BioClaw/` 本身。里面有 `package.json`、`README`、`container/`、`groups/`、`store/`。几乎所有命令都在这里执行。

2. **`.env` 文件**

   ```bash
   /path/to/BioClaw/.env
   ```

   决定你用哪个 API/provider（Anthropic、OpenRouter、OpenAI-compatible、Codex），以及哪些消息通道开启。

3. **workspace 目录**

   ```bash
   /path/to/BioClaw/groups/<workspace-name>/
   ```

   BioClaw 默认挂进容器的工作目录。你上传的文件最终会到这里。容器里对应 `/workspace/group`。

4. **mount allowlist 文件**

   **注意：这个文件不在项目里，而在当前用户的 home 目录下：**

   ```bash
   ~/.config/bioclaw/mount-allowlist.json
   ```

   它决定：哪些宿主机目录**允许**被额外挂载进容器。没这个文件，就不能挂载任何宿主机目录。

## 14. `.env` 配置详解

### 14.1 最小可用配置（三选一）

**选项 A：Anthropic（最简单，Claude 原厂）**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-你的key
```

**选项 B：OpenRouter（推荐，一个 key 调几十个模型）**

```bash
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-你的key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash
```

**选项 C：OpenAI-compatible（DeepSeek / 本地大模型 / 其他中转服务）**

```bash
MODEL_PROVIDER=openai-compatible
OPENAI_COMPATIBLE_API_KEY=你的key
OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com/v1
OPENAI_COMPATIBLE_MODEL=deepseek-chat
```

### 14.2 打开本地 Web UI

```bash
ENABLE_LOCAL_WEB=true
LOCAL_WEB_PORT=3000
```

这两行加上之后，`npm run web` 启动就会有 `http://localhost:3000` 的 Web 聊天界面。

### 14.3 消息通道（可选）

BioClaw 支持这些通道，都是"可选"的——不用它们完全不影响使用：

| 通道 | `.env` 开关 | 配置复杂度 |
|---|---|---|
| WhatsApp | `ENABLE_WHATSAPP=true` | 扫码登录，最简单 |
| 企业微信 WeCom | `WECOM_BOT_ID=` + `WECOM_SECRET=` | 需要管理员创建机器人 |
| 飞书 Feishu | `FEISHU_APP_ID=` + `FEISHU_APP_SECRET=` | 需要自建应用 |
| Discord | `DISCORD_BOT_TOKEN=` | 需要创建 Bot 应用 |
| Slack | `SLACK_BOT_TOKEN=` + `SLACK_APP_TOKEN=` | Socket Mode，需要在 api.slack.com 建 app |
| QQ 官方机器人 | `QQ_APP_ID=` + `QQ_CLIENT_SECRET=` | 需要审核 |
| 个人微信 | `ENABLE_WECHAT=true` | 扫码登录 |

每个通道的详细配置见 [docs/CHANNELS.zh-CN.md](./CHANNELS.zh-CN.md)。

### 14.4 容器运行时（一般不用改）

```bash
CONTAINER_RUNTIME=docker          # 默认 docker；HPC 环境可以用 apptainer
CONTAINER_IMAGE=bioclaw-agent:latest
```

---

# 第四部分：日常使用

## 15. 启动和停止 BioClaw

### 15.1 三种启动命令

在项目根目录：

```bash
# 只启动本地 Web UI（最常用）
npm run web

# 启动所有配置好的消息通道（WhatsApp / Feishu / Discord / Web 等）
npm run dev

# 后台运行（长时间挂机用）
nohup npm run dev > bioclaw.log 2>&1 &
```

### 15.2 停止

- 前台运行的终端：按 `Ctrl+C`
- 后台跑的（`nohup`）：`ps aux | grep bioclaw` 找到进程号，`kill <pid>`

### 15.3 重启

很多修改（`.env` 改了、allowlist 改了、container_config 改了）都需要重启才能生效。步骤：

```bash
# 1) 按 Ctrl+C 停止当前 BioClaw
# 2) 再次启动
npm run web   # 或 npm run dev
```

### 15.4 如何清理 Docker 容器（偶尔需要）

如果发现容器卡住或状态诡异：

```bash
# 看所有 bioclaw 相关容器
docker ps -a | grep bioclaw

# 停并删掉某个容器
docker rm -f <container-id>

# 把所有容器都清掉（只在确认没有其它 Docker 项目时做）
docker ps -aq | xargs docker rm -f
```

## 16. 聊天里的常用 slash commands

BioClaw 的控制是在**聊天窗口里**完成的，不是在终端里。常用命令如下：

### 16.1 查看当前状态

```text
/status       # 线程、provider、模型、workspace、工作目录
/doctor       # 健康检查：provider 可达性、容器状态等
/workspace current
/dir show
```

### 16.2 切换 provider 和 model

```text
/provider list                          # 看已配置的 provider
/provider switch openrouter             # 切到 OpenRouter（必须 .env 里配过）
/model show                             # 看当前模型
/model switch google/gemini-2.5-flash   # 切模型（仅 OpenRouter 支持）
```

### 16.3 线程管理

```text
/threads           # 列出当前聊天里所有线程
/new               # 开一个新线程
/use <thread-id>   # 切到某个线程
/rename 重要项目    # 重命名当前线程
/archive           # 归档当前线程
```

### 16.4 工作区和工作目录

```text
/workspace current       # 我现在在哪个 workspace
/workspace bind local-web   # 把当前线程绑到别的 workspace
/dir analysis            # 让当前线程默认在 analysis/ 子目录下工作
/dir reset               # 恢复到 workspace 根目录
```

### 16.5 Skills 管理

```text
/skills          # 看所有已安装 skill，并可标记偏好
/commands        # 给常用工作流起快捷键
/alias           # 配命令别名
```

### 16.6 SSH / 远程

```text
/ssh list        # 看 ~/.ssh/config 里配置过的 host 别名
```

配合 SSH，你可以直接让 BioClaw 在远程 HPC 上跑命令，详见 [第 28 节](#28-让-bioclaw-通过-ssh-连接远程服务器--hpc)。

### 16.7 Agent 记忆

```text
/memory set 我是做肿瘤免疫的，实验以小鼠为主
```

这句话会进入 Agent 的系统记忆，后续对话都会带上这个上下文。

## 17. 大多数用户根本不需要额外挂载

如果你的需求只是：

- 在本地网页里聊天
- 上传图片、CSV、FASTA、FASTQ、PDF、压缩包
- 让 BioClaw 分析这些上传的文件

那**不需要** `allowlist`，也**不需要** `additionalMounts`。

上传的文件默认就会进入当前 workspace，Agent 在容器里直接从 `/workspace/group` 读取。

只有在下面这种场景，你才需要"额外挂载"：

- 你的数据已经放在宿主机某个很大的目录里，不想复制一份到 `groups/`
- 你希望 BioClaw 直接读一个现成数据盘，比如 `/mnt/lab-data`
- 你想让 BioClaw 把结果直接写回宿主机某个固定目录

挂载的完整步骤见 [第六部分](#第六部分高级挂载宿主机目录)。

## 18. 切换 provider 和 model

BioClaw 里有两种"切换"：

### 18.1 切当前聊天线程的 provider / model（临时）

直接在聊天里输入：

```text
/provider list
/provider switch openrouter
/model show
/model switch google/gemini-2.5-flash
```

适合：

- 这个线程临时想换模型（比如某个模型更擅长代码，另一个更擅长写作）
- 同一个 BioClaw 实例里，不同线程想用不同 provider
- A/B 对比不同模型的回答

注意：

- 只有当前环境里已经配置好对应 API key 才能切过去
- `anthropic` 目前不支持像 OpenRouter 那样按线程单独切模型

### 18.2 切整个实例的默认 API/provider（永久）

改 `.env`，然后重启 BioClaw：

```bash
# 1) 编辑 .env，改 MODEL_PROVIDER / API_KEY / MODEL
# 2) Ctrl+C 停止当前进程
# 3) 再启动
npm run web
```

适合：

- 你想让整个实例默认都用 OpenRouter
- 你要换 API key 或 base URL

## 19. workspace 详解

容器里经常会出现这几个路径：

| 容器内路径 | 含义 |
|---|---|
| `/workspace/group` | 当前 workspace 的主工作目录（最常用） |
| `/workspace/project` | 整个 BioClaw 项目根目录，仅 `main` workspace 默认有 |
| `/workspace/global` | 全局共享目录，如果宿主机存在 `groups/global` |
| `/workspace/ipc` | BioClaw 内部 IPC 目录，Agent 的中间文件 |
| `/workspace/extra/...` | 额外挂载的宿主机目录（见第六部分） |

最重要的就是：

- **你的默认工作目录几乎总是 `/workspace/group`**
- 你上传的文件通常就在这里或它的子目录里

### 19.1 查看当前 workspace

```text
/workspace current
/status
/dir show
```

### 19.2 把线程切到别的 workspace

```text
/workspace bind lab-project-2024
```

### 19.3 改线程的默认工作目录

让当前线程默认在 `analysis/` 下工作：

```text
/dir analysis
```

恢复到 workspace 根目录：

```text
/dir reset
```

---

# 第五部分：常见使用场景实战

下面这些例子都假设你已经完成了第一部分的"5 分钟上手"，BioClaw 正在本地 Web UI 上跑。

## 20. 分析一个上传的 CSV 文件

**场景：** 你有一份基因表达矩阵的 CSV，想看整体结构。

**操作：**

1. 把 CSV 拖进聊天框上传
2. 问：

   ```text
   这个文件是一份基因表达矩阵。请：
   1) 告诉我有多少行多少列、表头是什么
   2) 统计每列的分布（均值、标准差、缺失值占比）
   3) 画一张样本之间的相关性热图
   ```

**Agent 会**：
- 在容器里用 `pandas` 读文件
- 用 `seaborn` 画热图
- 把图片直接发到聊天里

## 21. 跑 BLAST 同源搜索

**场景：** 你有一段未知来源的蛋白序列，想找同源。

**操作：**

```text
下面是一段蛋白序列，请：
1) 用 BLAST 对 NCBI nr 库做同源搜索（E-value < 1e-10）
2) 列出前 5 个同源命中及其物种来源
3) 告诉我这段序列最可能是哪一类酶

>my_unknown
MKVLWAALLVTFLAGCQAKVEQAVETEPEPELRQQTEWQSGQRWELALGRFWDYLRWVQTL
SEQVAKKQKEEPALEVVEQE
```

**Agent 会**：用 `blast-search` skill 跑在线 BLAST，拉回结果，整理成表格发回。

## 22. Bulk RNA-seq 差异表达分析

**场景：** 你有处理组和对照组的 count 矩阵 + 样本元数据。

**操作：**

1. 上传两个文件：
   - `counts.tsv`（gene × sample 计数矩阵）
   - `coldata.csv`（sample, condition 两列）
2. 问：

   ```text
   我有 bulk RNA-seq 的 count 矩阵和样本元数据。请用 PyDESeq2 做差异表达分析，
   比较 treated vs control，给我：
   1) 显著差异基因表（adj-p < 0.05, |log2FC| > 1）
   2) 火山图
   3) 前 20 个上调基因和下调基因的 GO 富集
   ```

**Agent 会**：用 `differential-expression` + `bio-figure-design` skill，调用 PyDESeq2 + g:Profiler，整套跑完把图表发回。

## 23. 单细胞 RNA-seq 分析

**场景：** 10x Genomics 的 filtered_feature_bc_matrix 文件夹。

**操作：**

1. 把整个 `filtered_feature_bc_matrix/` 压缩成 `.zip` 上传（或用挂载，见第六部分）
2. 问：

   ```text
   这是一份 10x scRNA-seq 数据。请用 scanpy 完整跑一遍预处理：
   1) 质量过滤（min_genes=200, min_cells=3, pct_mt<20）
   2) normalize + log
   3) 高变基因筛选 + PCA + UMAP
   4) Leiden 聚类（resolution=0.5）
   5) 自动细胞类型注释
   6) 输出 UMAP 图 + 每类的 top marker gene
   ```

**Agent 会**：用 `scrna-preprocessing-clustering` + `cell-annotation` skill 跑完整 pipeline。

## 24. 查询 PDB / UniProt / AlphaFold 结构

**场景：** 想知道某个基因的三维结构。

**操作：**

```text
TP53 这个蛋白：
1) 它的 UniProt ID 是什么？全长多少氨基酸？
2) PDB 里有哪些结构？推荐最有代表性的 2-3 个
3) AlphaFold 预测结构的 pLDDT 平均分怎么样？
4) 标出 DNA 结合 domain 和 tetramerization domain 在序列上的位置
```

**Agent 会**：用 `query-uniprot`、`query-pdb`、`query-alphafold` 三个 skill 并行查询，汇总成报告。

## 25. PubMed 文献搜索 + 综述

**场景：** 想快速了解一个领域的最新进展。

**操作：**

```text
帮我做一个关于"CRISPR-Cas13 在 RNA 编辑方向"的文献综述：
1) PubMed 搜 2022-2025 年的论文，筛出高引用的 30 篇
2) 分成：基础机制、治疗应用、安全性问题、新型变体 四类
3) 每类给一段 200 字总结，并列出 3-5 篇代表文献
```

**Agent 会**：用 `pubmed-search` + `bio-manuscript-outline` skill 配合完成。

## 26. 生成技术报告（Typst / SEC）

**场景：** 刚跑完一组实验，想做一份正式的技术报告。

**操作：**

```text
基于刚才的差异表达分析结果，帮我生成一份 Typst 格式的技术报告，
包含：背景、方法、结果、讨论、结论，以及所有图表。输出 PDF。
```

**Agent 会**：用 `sec-report` + `report-template` skill，调用 Typst 把报告渲染成 PDF 发回。

## 27. 分析 SDS-PAGE 凝胶图

**场景：** 你拍了一张 SDS-PAGE 的照片，想知道结果怎么样。

**操作：**

1. 把凝胶图片上传
2. 问：

   ```text
   这是一张 SDS-PAGE 凝胶图。请：
   1) 标出 ladder 位置和每个样品泳道
   2) 估算目的带（约 55 kDa）的大致分子量和丰度
   3) 判断是否有明显降解或非特异带
   ```

**Agent 会**：用 `sds-gel-review` skill 做图像分析。

## 28. 让 BioClaw 通过 SSH 连接远程服务器 / HPC

**场景：** 数据太大，不想传到本地，让 BioClaw 直接去远程服务器上跑。

**前置：**

1. 在你的本机 `~/.ssh/config` 里配好远程 host 别名，例如：

   ```ssh-config
   Host hpc-login
       HostName 10.0.0.42
       User your-username
       IdentityFile ~/.ssh/id_rsa
   ```

2. 在 `.env` 里限制 BioClaw 能访问哪些 host（可选，但建议）：

   ```bash
   BIOCLAW_SSH_ALLOWED_HOSTS=hpc-login,lambda-cloud-a100
   ```

**用法：**

```text
/ssh list
```

会列出所有已配的 host。然后直接说：

```text
通过 hpc-login 在远程服务器跑 samtools flagstat /scratch/data/sample.bam，把结果报给我
```

Agent 会用 SSH 连到远程服务器，跑命令，把输出带回来。

---

# 第六部分：高级——挂载宿主机目录

这一部分是**只有你真的需要挂载宿主机目录时才要看**。如果你只是上传文件来分析，可以跳过。

## 29. 什么时候需要 allowlist

只有当你要把**宿主机上的额外目录**挂进容器时，才需要 allowlist。

例如，你宿主机上有：

```bash
/home/you/lab-data
```

你想让 BioClaw 在容器里看到它，就不能直接写"挂载这个目录"。必须分两步：

1. 先在 `~/.config/bioclaw/mount-allowlist.json` 里允许这个目录所在根路径
2. 再在某个 workspace/group 的 `container_config` 里声明要挂哪个目录

如果第一步没做，第二步会被拒绝。

## 30. 第一次配置 allowlist（一步一步来）

### 30.1 创建配置目录

```bash
mkdir -p ~/.config/bioclaw
```

### 30.2 创建 allowlist 文件

```bash
cat > ~/.config/bioclaw/mount-allowlist.json <<'EOF'
{
  "allowedRoots": [
    {
      "path": "~/lab-data",
      "allowReadWrite": false,
      "description": "实验数据目录，只读"
    },
    {
      "path": "~/lab-results",
      "allowReadWrite": true,
      "description": "结果输出目录，可写"
    }
  ],
  "blockedPatterns": [
    "password",
    "secret",
    "token"
  ],
  "nonMainReadOnly": true
}
EOF
```

这几个字段的意思：

- `allowedRoots`
  允许挂载的宿主机根目录列表。只有在这些根目录下面的路径，才允许被挂进容器。

- `allowReadWrite`
  这个根目录是否允许读写。

- `blockedPatterns`
  即使路径在 `allowedRoots` 下，只要命中这些敏感模式，也会被拒绝。BioClaw 另外还有内置的硬性屏蔽（`.ssh`、`.env`、`credentials` 等），不可能绕过。

- `nonMainReadOnly`
  如果设为 `true`，那么**非 main workspace** 即使请求读写，也会被强制变成只读。

### 30.3 非常重要：修改 allowlist 后要重启 BioClaw

因为 allowlist 会在进程里缓存。所以改完这个文件后请重启：

```bash
# Ctrl+C 停止
npm run dev   # 或 npm run web
```

## 31. 额外挂载到底挂到哪里

额外挂载不会直接挂成你自己写的绝对路径。

BioClaw 会把它们统一挂到：

```bash
/workspace/extra/<containerPath>
```

例如你写：

```json
{
  "hostPath": "~/lab-data/projectA",
  "containerPath": "projectA-data",
  "readonly": true
}
```

那么容器里实际看到的是：

```bash
/workspace/extra/projectA-data
```

**不是** `/lab-data/projectA`，**也不是** `/workspace/group/projectA-data`。这个设计是为了防止 Agent 把挂载目录和 workspace 真正的文件混淆。

## 32. 把宿主机目录挂给某个 workspace

### 32.1 先确认你要改哪个 workspace

先看当前已注册的 chat / workspace：

```bash
npm run agents -- chats
```

或者直接查数据库：

```bash
sqlite3 store/messages.db "SELECT jid, name, folder, workspace_folder FROM registered_groups;"
```

你会看到类似：

```text
local-web@local.web|Local Web Chat|local-web|local-web
...
```

通常你会改某个 `folder`，例如：

- `main`
- `local-web`
- 某个群对应的 folder

### 32.2 用 SQL 写入 `container_config`

假设你要给 `local-web` workspace 加两个额外挂载：

```bash
sqlite3 store/messages.db <<'EOF'
UPDATE registered_groups
SET container_config = json('{
  "additionalMounts": [
    {
      "hostPath": "~/lab-data/projectA",
      "containerPath": "projectA-data",
      "readonly": true
    },
    {
      "hostPath": "~/lab-results/projectA",
      "containerPath": "projectA-results",
      "readonly": false
    }
  ]
}')
WHERE folder = 'local-web';

SELECT folder, container_config
FROM registered_groups
WHERE folder = 'local-web';
EOF
```

这里每个字段的意思：

- `hostPath`
  宿主机上的真实目录。支持 `~`。

- `containerPath`
  容器内最终会变成 `/workspace/extra/<containerPath>`。不要写绝对路径，也不要带 `..`。

- `readonly`
  `true` 表示只读，`false` 表示希望读写。最终是否真的可写还要看 allowlist 里 `allowReadWrite` 和 `nonMainReadOnly`。

### 32.3 再次重启 BioClaw

`registered_groups.container_config` 在启动时加载到内存，所以改完后也要重启。

## 33. 如何验证挂载是否成功

推荐按这个顺序检查。

### 33.1 看 BioClaw 状态

在聊天里输入：

```text
/status
/doctor
```

### 33.2 直接让 Agent 看目录

在聊天里问：

```text
请列出 /workspace/extra 下有哪些目录
```

或者：

```text
请读取 /workspace/extra/projectA-data 目录结构，只显示前两层
```

### 33.3 看容器日志

BioClaw 启动时会把挂载配置打到日志里。你可以查看容器日志确认实际挂了哪些路径：

```bash
# 先看有哪些容器
docker ps

# 再看具体容器的日志
docker logs <container-name>
```

## 34. 推荐的最小可用配置示例

### 34.1 `.env`

```bash
MODEL_PROVIDER=openrouter
OPENROUTER_API_KEY=你的_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.5-flash

ENABLE_LOCAL_WEB=true
LOCAL_WEB_PORT=3000
```

### 34.2 allowlist

```json
{
  "allowedRoots": [
    {
      "path": "~/lab-data",
      "allowReadWrite": false,
      "description": "只读数据目录"
    },
    {
      "path": "~/lab-results",
      "allowReadWrite": true,
      "description": "结果输出目录"
    }
  ],
  "blockedPatterns": [
    "password",
    "secret",
    "token"
  ],
  "nonMainReadOnly": true
}
```

### 34.3 `container_config`

```json
{
  "additionalMounts": [
    {
      "hostPath": "~/lab-data/projectA",
      "containerPath": "projectA-data",
      "readonly": true
    },
    {
      "hostPath": "~/lab-results/projectA",
      "containerPath": "projectA-results",
      "readonly": false
    }
  ]
}
```

---

# 第七部分：遇到问题怎么办

## 35. 新手最容易卡住的点

### 35.1 "为什么我明明加了 additionalMounts，容器里却没有？"

常见原因有 5 个：

1. 你没有创建 `~/.config/bioclaw/mount-allowlist.json`
2. `hostPath` 在宿主机上不存在（路径拼错、`~` 展开失败）
3. `hostPath` 不在 `allowedRoots` 下面
4. 改完 allowlist 或 `container_config` 后没有重启 BioClaw
5. `containerPath` 写成了绝对路径或带 `..`

### 35.2 "为什么我请求了读写，最后却只有只读？"

可能是下面两种情况：

1. 你的 `allowedRoots` 里 `allowReadWrite: false`
2. `nonMainReadOnly: true`，而你当前 workspace 不是 `main`

### 35.3 "为什么我不能挂 `~/.ssh`、`.env`、credentials 之类目录？"

这是故意的安全限制。BioClaw 默认会阻止这类敏感目录挂进容器。设计上认为：如果你真的需要 SSH 到某台机器，应该走 `/ssh list` 那条路径（见 [第 28 节](#28-让-bioclaw-通过-ssh-连接远程服务器--hpc)），而不是把私钥挂进容器。

### 35.4 "我只是想让 BioClaw 处理几个文件，真的要走挂载吗？"

**不用。** 最简单的办法仍然是：

- 用本地网页上传文件
- 或手动把文件放到 `groups/<workspace>/`

这样最省事，也最不容易出安全问题。

### 35.5 "Agent 好像卡住了不回"

常见原因：

1. **API Key 无效或额度用完**——`.env` 里换一个 key，重启
2. **网络不通**——`/doctor` 会直接报 provider 不可达
3. **容器构建失败**——`docker images | grep bioclaw` 看镜像是否存在。不在的话重新 `docker build`
4. **容器在拉取大模型或依赖**——第一次可能很慢，看 `docker logs <container>` 确认

### 35.6 "Web UI 打开是空白 / 打不开"

1. 确认 `.env` 里有 `ENABLE_LOCAL_WEB=true`
2. 确认端口 `LOCAL_WEB_PORT=3000` 没被别的进程占用（`lsof -i :3000`）
3. 看启动日志有没有 `Local web UI listening on...` 这行
4. 在浏览器地址栏确认访问的是 `http://localhost:3000`（不是 `https`）

## 36. 遇到问题的排障顺序

以后遇到"为什么文件看不到"、"为什么 provider 不工作"、"为什么写不进去"这类问题，可以按下面顺序排查：

1. `.env` 有没有配对（API key、MODEL_PROVIDER、URL）
2. `npm run dev` 或 `npm run web` 是否已经重启（所有配置改动都需要重启）
3. `/status` 和 `/doctor` 是否正常
4. 当前 workspace 是哪个（`/workspace current`）
5. 文件是不是本来就应该放到 `groups/<workspace>/`
6. 如果用了额外挂载：
   - allowlist 文件在不在
   - `hostPath` 存不存在
   - 是否在 `allowedRoots` 下
   - 是否被强制只读（`nonMainReadOnly` + 非 main workspace）
7. 容器有没有在运行：`docker ps | grep bioclaw`
8. 容器日志里有没有报错：`docker logs <container>`

## 37. 诊断命令速查

### 37.1 聊天里

```text
/status                  # 当前线程、provider、模型、workspace、cwd
/doctor                  # 完整系统自检（provider 可达性、容器状态）
/workspace current       # 当前 workspace
/dir show                # 当前工作目录
/threads                 # 线程列表
/skills                  # 已安装 skill 列表
```

### 37.2 终端里

```bash
# 看 BioClaw 进程
ps aux | grep -E "node|bioclaw" | grep -v grep

# 看 Docker 容器
docker ps                        # 正在跑的
docker ps -a                     # 包括已停止的
docker logs <container-id>       # 容器日志
docker exec -it <container-id> bash   # 进入容器调试

# 看 BioClaw 镜像是否在
docker images | grep bioclaw

# 查 SQLite 数据库
sqlite3 store/messages.db "SELECT folder, container_config FROM registered_groups;"

# 看端口占用
lsof -i :3000                    # Linux/macOS
netstat -ano | findstr :3000     # Windows

# 验证 Node 和 Docker 版本
node -v && docker -v
```

### 37.3 重置到初始状态

如果彻底搞乱了想从头再来：

```bash
# 停 BioClaw
# Ctrl+C

# 清容器
docker ps -aq | xargs docker rm -f

# 重建镜像
docker build -t bioclaw-agent:latest container/

# （可选）重置会话数据库——⚠ 会丢失所有历史聊天和 workspace 绑定
rm -rf store/messages.db

# 再启动
npm run web
```

## 38. 去哪里寻求帮助

1. **官方文档**：`docs/` 目录下还有 [CHANNELS](./CHANNELS.zh-CN.md)、[WINDOWS](./WINDOWS.zh-CN.md)、[SECURITY](./SECURITY.md)、[DASHBOARD](./DASHBOARD.md)、[CLUSTER_DEPLOYMENT](./CLUSTER_DEPLOYMENT.zh-CN.md)、[CUSTOM_SKILLS](./CUSTOM_SKILLS.md)
2. **GitHub Issues**：[github.com/Runchuan-BU/BioClaw/issues](https://github.com/Runchuan-BU/BioClaw/issues)——提 issue 前先贴 `/doctor` 输出和 `docker logs` 的最后 50 行
3. **微信群**：扫 [官网](https://ivegotmagicbean.github.io/BioClaw-Page/zh.html) 上的二维码加群
4. **技术论文**：[bioRxiv](https://www.biorxiv.org/content/10.64898/2026.04.11.716807v1) 和 [arXiv](https://arxiv.org/abs/2507.02004) 上有详细架构说明

---

# 第八部分：推荐路径 + 相关文档

## 39. 三条推荐的新手使用路径

如果你是第一次用，建议按下面某一条来：

### 路线 A：最简单（99% 新手应该走这条）

1. 配 `.env`（选 Anthropic 或 OpenRouter）
2. `docker build -t bioclaw-agent:latest container/`
3. `npm run web`
4. 在本地网页上传文件
5. 直接让 BioClaw 分析上传的文件

这条路线**不需要** allowlist，**不需要** SQL，**不需要** 额外挂载。

### 路线 B：你已经有宿主机数据目录（大数据集）

1. 配 `.env`
2. 建 `~/.config/bioclaw/mount-allowlist.json`
3. 先只挂一个只读目录（稳一点，不至于误写）
4. 改 `registered_groups.container_config`
5. 重启 BioClaw
6. 在聊天里验证 `/workspace/extra/...` 能不能看到

### 路线 C：你想让 BioClaw 直接把结果写回宿主机

在路线 B 基础上再做两件事：

1. 对应 `allowedRoots` 设 `allowReadWrite: true`
2. `additionalMounts` 里把 `readonly` 设成 `false`

如果仍然只读，优先检查是不是 `nonMainReadOnly: true` 导致的。

## 40. 相关文档

- [README.zh-CN.md](../README.zh-CN.md) — 项目总览和快速介绍
- [docs/CHANNELS.zh-CN.md](./CHANNELS.zh-CN.md) — WhatsApp / 飞书 / 企业微信 / Discord / Slack / QQ 等各通道详细配置
- [docs/WINDOWS.zh-CN.md](./WINDOWS.zh-CN.md) — Windows 用户的 WSL2 安装步骤
- [docs/SECURITY.md](./SECURITY.md) — 完整的信任模型和安全边界说明
- [docs/DEBUG_CHECKLIST.md](./DEBUG_CHECKLIST.md) — 更深入的排障清单
- [docs/DASHBOARD.md](./DASHBOARD.md) — 可视化 Lab Trace（看 Agent 干了什么）
- [docs/CUSTOM_SKILLS.md](./CUSTOM_SKILLS.md) — 怎么自己开发新 skill
- [docs/CLUSTER_DEPLOYMENT.zh-CN.md](./CLUSTER_DEPLOYMENT.zh-CN.md) — HPC / 集群部署
- [docs/APPTAINER.md](./APPTAINER.md) — 没有 Docker 权限时用 Apptainer/Singularity

如果你已经能跑起来，只是想研究更高级的部署、安全策略、HPC 使用、自定义 skill，再继续看后面这些文档。

如果你只是想先把 BioClaw 用起来跑生物分析，**这一篇应该够了**。
