# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Astron Agent 是一个企业级 Agentic Workflow 开发平台,采用微服务架构,整合了 AI 工作流编排、模型管理、AI 工具、RPA 自动化和团队协作功能。

### 技术栈概览

- **前端**: TypeScript + React 18 + Vite + Ant Design (位于 `console/frontend/`)
- **控制台后端**: Java 21 + Spring Boot 3.5.4 (位于 `console/backend/`)
- **核心微服务**: Python 3.11+ + FastAPI (位于 `core/` 目录)
- **租户服务**: Go 1.23 + Gin (位于 `core/tenant/`)
- **基础设施**: MySQL, Redis, Kafka, MinIO

## 项目架构

### 目录结构

```
astron-agent/
├── console/                    # 控制台模块
│   ├── frontend/              # React 前端 (TypeScript)
│   └── backend/               # Spring Boot 后端 (Java)
│       ├── hub/               # 主 API 服务
│       ├── toolkit/           # 工具模块
│       └── commons/           # 公共模块
├── core/                      # 核心微服务
│   ├── agent/                 # Agent 服务 (Python FastAPI)
│   ├── workflow/              # 工作流服务 (Python FastAPI)
│   ├── knowledge/             # 知识库服务 (Python FastAPI)
│   ├── memory/                # 内存数据库服务 (Python)
│   ├── tenant/                # 租户服务 (Go Gin)
│   ├── common/                # 公共模块 (Python)
│   └── plugin/                # 插件系统
│       ├── aitools/           # AI 工具插件
│       ├── rpa/               # RPA 插件
│       └── link/              # 链接插件
├── docker/                    # Docker 配置
├── docs/                      # 文档
├── helm/                      # Kubernetes Helm Charts
└── makefiles/                 # Makefile 工具链
```

### 核心架构模式

#### 1. 微服务通信

- **Frontend → Backend**: HTTP/REST + SSE (服务端推送)
- **Backend → Core Services**: HTTP/REST API
- **Core Services ↔ Core Services**: Kafka 事件驱动 (异步)
- **数据持久化**: MySQL (关系数据) + Redis (缓存/会话)
- **文件存储**: MinIO (对象存储)

#### 2. Kafka 事件主题

- `workflow-events`: 工作流事件
- `knowledge-events`: 知识库事件
- `agent-events`: Agent 事件

#### 3. Python 服务架构 (DDD)

所有 Python 微服务遵循领域驱动设计 (DDD):

```
service/
├── api/                       # API 层 (FastAPI 路由)
├── service/                   # 服务层 (业务逻辑)
├── domain/                    # 领域层 (领域模型)
├── repository/                # 仓储层 (数据访问)
└── main.py                    # 服务入口
```

#### 4. 公共模块 (core/common)

为所有 Python 服务提供统一的基础设施:

- 认证和审计系统 (MetrologyAuth)
- 可观测性支持 (OpenTelemetry)
- 数据库、缓存、消息队列连接管理
- 统一日志系统
- OSS 对象存储集成

## 部署

### Docker Compose 部署 (推荐快速开始)

```bash
cd docker/astronAgent
cp .env.example .env
vim .env                        # 配置环境变量

# 启动所有服务 (包括 Casdoor 认证)
docker compose -f docker-compose-with-auth.yaml up -d

# 访问地址
# - 前端: http://localhost/
# - Casdoor 管理: http://localhost:8000 (admin/123)
```

## 重要注意事项

### 开发约定

1. **禁止直接推送到 main/develop 分支** - 必须通过分支开发 + PR 流程

### 模块间依赖

- **Common Module** 被所有 Python 服务依赖,修改时需谨慎
- **Agent Service** 被 Workflow 服务调用
- **Knowledge Service** 为 Agent 和 Workflow 提供 RAG 能力
- **Tenant Service** 为所有服务提供租户上下文

## 相关文档

- [项目模块说明](docs/PROJECT_MODULES_zh.md) - 详细架构说明
- [部署指南](docs/DEPLOYMENT_GUIDE_WITH_AUTH_zh.md) - 完整部署步骤
- [前端开发指南](console/frontend/CLAUDE.md) - 前端特定指南
