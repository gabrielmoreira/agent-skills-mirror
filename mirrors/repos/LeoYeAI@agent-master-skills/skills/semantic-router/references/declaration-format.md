# 语义检查声明格式规范

## 架构说明（v7.9+ 当前版本）

自 v7.9 起，semantic-router 采用 **Webhook 服务架构**，不再依赖 `before_agent_start` hook 或 `message-injector` 插件。

### 运行方式

```
┌─────────────────┐     POST /route      ┌─────────────────────────┐
│   OpenClaw      │ ───────────────────→ │  semantic-webhook-      │
│   Gateway       │   {message, pool}    │  server.py (port 9811)  │
└─────────────────┘                      └─────────────────────────┘
                                                  │
                                                  ↓
                                         ┌─────────────────────────┐
                                         │  semantic_check.py      │
                                         │  - 关键词匹配           │
                                         │  - 语义相似度计算       │
                                         │  - 分支决策             │
                                         └─────────────────────────┘
                                                  │
                                                  ↓
                                         ┌─────────────────────────┐
                                         │  返回路由建议            │
                                         │  - branch: B/C/C-auto   │
                                         │  - target_pool          │
                                         │  - declaration          │
                                         └─────────────────────────┘
```

### 启动 Webhook 服务

```bash
# 方式1: 手动启动
python3 ~/.openclaw/workspace/.lib/semantic-webhook-server.py --port 9811

# 方式2: 后台运行（推荐）
nohup python3 ~/.openclaw/workspace/.lib/semantic-webhook-server.py --port 9811 > /dev/null 2>&1 &

# 方式3: 使用 PM2 守护（生产环境）
pm2 start ~/.openclaw/workspace/.lib/semantic-webhook-server.py --name semantic-webhook -- --port 9811
```

### 验证服务运行

```bash
# 健康检查
curl http://127.0.0.1:9811/health
# 预期输出: {"status": "ok", "version": "7.9.x"}

# 测试路由
curl -X POST http://127.0.0.1:9811/route \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我写个Python爬虫", "current_pool": "Highspeed"}'
```

---

## 声明格式（用于调试和日志）

### B分支（延续当前会话）
```
【语义检查】PX-延续｜模型池:【XXX池】｜实际模型:model-id
```

**示例：**
```
【语义检查】P2-延续｜模型池:【高速池】｜实际模型:claude-haiku-4.5
【语义检查】P2-延续｜模型池:【智能池】｜实际模型:claude-opus-4.6
```

### C分支（新会话 + 模型切换）
```
【语义检查】PX-任务描述｜新会话→XXX池｜实际模型:model-id
```

**示例：**
```
【语义检查】P1-执行开发任务｜新会话→智能池｜实际模型:claude-opus-4.6
【语义检查】P2-执行信息检索｜新会话→高速池｜实际模型:claude-haiku-4.5
【语义检查】P3-内容生成｜新会话→人文池｜实际模型:claude-sonnet-4.6
```

## 字段说明

| 字段 | 说明 |
|------|------|
| `PX` | 优先级：P1=开发/自动化/运维，P2=信息检索/协调，P3=内容生成/问答 |
| `模型池:【XXX池】` | 当前所属模型池中文名 |
| `实际模型:` | 当前实际调用的模型 ID 末段（去掉 provider 前缀） |
| `新会话→` | C分支专用，表示触发了 session reset |

## P等级映射

| P等级 | 任务类型 |
|-------|----------|
| P1 | development, automation, system_ops, agentic_tasks |
| P2 | info_retrieval, coordination, web_search, continue |
| P3 | content_generation, reading, q_and_a, training, multimodal |

---

## 历史架构说明（v7.6 之前，已废弃）

<details>
<summary>点击查看旧架构说明（仅供参考）</summary>

### 旧架构：message-injector 插件 + before_agent_start hook

在 v7.6 之前，semantic-router 通过 TypeScript 插件实现：

1. **Hook 注册**: `before_agent_start` hook 触发语义检查
2. **声明注入**: 通过 `prependContext` 将声明注入用户消息前缀
3. **模型切换**: 调用 `sessions.patch` 和 `sessions.reset`

### 为什么废弃旧架构？

1. **缓存失效问题**: 声明字符串含动态字段（ctx_score、dispatch_id），导致 LLM prefix cache 每轮 100% miss
2. **复杂度高**: 需要维护 TypeScript 插件，与 OpenClaw 核心耦合
3. **部署困难**: 需要安装 hook，用户容易配置错误

### 新架构优势

1. **缓存友好**: 动态字段从 prependContext 移除，prefix cache 命中率接近 100%
2. **独立服务**: Webhook 服务可独立运行、独立重启
3. **简单透明**: HTTP API 易于调试和监控

</details>

---

## 故障排除

### Webhook 服务未启动

**症状**: 调用路由 API 返回 `Connection refused`
**解决**:
```bash
# 检查服务是否运行
curl http://127.0.0.1:9811/health

# 如果没运行，启动它
python3 ~/.openclaw/workspace/.lib/semantic-webhook-server.py --port 9811 &
```

### 端口冲突

**症状**: `Address already in use`
**解决**:
```bash
# 查找占用端口的进程
lsof -i :9811

# 杀掉旧进程或更换端口
python3 ~/.openclaw/workspace/.lib/semantic-webhook-server.py --port 9812
```

### 日志查看

```bash
# Webhook 服务日志
tail -f ~/.openclaw/logs/semantic-webhook.log

# 语义检查详细日志
tail -f ~/.openclaw/workspace/.lib/semantic_check.log
```
