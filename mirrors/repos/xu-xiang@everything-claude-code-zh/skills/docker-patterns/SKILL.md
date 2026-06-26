---
name: docker-patterns
description: 用于本地开发、容器安全、网络、卷策略和多服务编排的 Docker 与 Docker Compose 模式。
origin: ECC
---

# Docker 模式 (Docker Patterns)

容器化开发的 Docker 和 Docker Compose 最佳实践。

## 激活时机

- 为本地开发设置 Docker Compose
- 设计多容器架构
- 排查容器网络或卷（Volume）问题
- 审查 Dockerfile 的安全性与镜像大小
- 从本地开发迁移到容器化工作流（Workflow）

## 用于本地开发的 Docker Compose

### 标准 Web 应用技术栈

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev                     # 使用多阶段构建 Dockerfile 的 dev 阶段
    ports:
      - "3000:3000"
    volumes:
      - .:/app                        # 绑定挂载用于热重载
      - /app/node_modules             # 匿名卷 -- 保留容器内的依赖
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  mailpit:                            # 本地邮件测试
    image: axllent/mailpit
    ports:
      - "8025:8025"                   # Web UI 界面
      - "1025:1025"                   # SMTP 端口

volumes:
  pgdata:
  redisdata:
```

### 开发与生产环境的 Dockerfile

```dockerfile
# 阶段：依赖安装 (dependencies)
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 阶段：开发环境 (dev - 支持热重载、调试工具)
FROM node:22-alpine AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# 阶段：构建 (build)
FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

# 阶段：生产环境 (production - 最小化镜像)
FROM node:22-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

### 覆盖文件（Override Files）

```yaml
# docker-compose.override.yml (自动加载，仅限开发环境设置)
services:
  app:
    environment:
      - DEBUG=app:*
      - LOG_LEVEL=debug
    ports:
      - "9229:9229"                   # Node.js 调试器端口

# docker-compose.prod.yml (生产环境显式指定)
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```

```bash
# 开发环境 (自动加载 override)
docker compose up

# 生产环境
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 网络（Networking）

### 服务发现（Service Discovery）

在同一个 Compose 网络中的服务可以通过服务名解析：
```
# 在 "app" 容器中：
postgres://postgres:postgres@db:5432/app_dev    # "db" 解析为 db 容器
redis://redis:6379/0                             # "redis" 解析为 redis 容器
```

### 自定义网络（Custom Networks）

```yaml
services:
  frontend:
    networks:
      - frontend-net

  api:
    networks:
      - frontend-net
      - backend-net

  db:
    networks:
      - backend-net              # 仅 api 可达，frontend 不可达

networks:
  frontend-net:
  backend-net:
```

### 仅暴露必要的端口

```yaml
services:
  db:
    ports:
      - "127.0.0.1:5432:5432"   # 仅宿主机可访问，外部网络不可见
    # 在生产环境中完全省略 ports -- 仅在 Docker 网络内部可访问
```

## 卷策略（Volume Strategies）

```yaml
volumes:
  # 命名卷 (Named volume): 在容器重启间持久化，由 Docker 管理
  pgdata:

  # 绑定挂载 (Bind mount): 将宿主机目录映射到容器（用于开发）
  # - ./src:/app/src

  # 匿名卷 (Anonymous volume): 防止绑定挂载覆盖容器生成的特定内容
  # - /app/node_modules
```

### 常用模式

```yaml
services:
  app:
    volumes:
      - .:/app                   # 源代码 (绑定挂载用于热重载)
      - /app/node_modules        # 保护容器的 node_modules 不被宿主机覆盖
      - /app/.next               # 保护构建缓存

  db:
    volumes:
      - pgdata:/var/lib/postgresql/data          # 持久化数据
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql  # 初始化脚本
```

## 容器安全（Container Security）

### Dockerfile 硬化

```dockerfile
# 1. 使用特定的标签 (绝不使用 :latest)
FROM node:22.12-alpine3.20

# 2. 以非 root 用户运行
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app

# 3. 移除能力 (Capabilites，在 compose 中配置)
# 4. 尽可能使用只读根文件系统
# 5. 不在镜像层中存储密钥
```

### Compose 安全

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE          # 仅当需要绑定 < 1024 端口时
```

### 密钥管理（Secret Management）

```yaml
# 推荐：使用环境变量（在运行时注入）
services:
  app:
    env_file:
      - .env                     # 严禁将 .env 提交到 git
    environment:
      - API_KEY                  # 从宿主机环境继承

# 推荐：Docker Secrets (Swarm 模式)
secrets:
  db_password:
    file: ./secrets/db_password.txt

services:
  db:
    secrets:
      - db_password

# 不良实践：硬编码在镜像中
# ENV API_KEY=sk-proj-xxxxx      # 严禁这样做
```

## .dockerignore

```
node_modules
.git
.env
.env.*
dist
coverage
*.log
.next
.cache
docker-compose*.yml
Dockerfile*
README.md
tests/
```

## 调试（Debugging）

### 常用命令

```bash
# 查看日志
docker compose logs -f app           # 持续追踪 app 日志
docker compose logs --tail=50 db     # 查看 db 最后 50 行日志

# 在运行中的容器内执行命令
docker compose exec app sh           # 进入 app 终端
docker compose exec db psql -U postgres  # 连接到 postgres

# 查看状态
docker compose ps                     # 查看运行中的服务
docker compose top                    # 查看每个容器内的进程
docker stats                          # 查看资源使用情况

# 重新构建
docker compose up --build             # 重新构建镜像并启动
docker compose build --no-cache app   # 强制完整重新构建

# 清理
docker compose down                   # 停止并移除容器
docker compose down -v                # 同时移除卷（破坏性操作）
docker system prune                   # 移除未使用的镜像/容器
```

### 调试网络问题

```bash
# 在容器内检查 DNS 解析
docker compose exec app nslookup db

# 检查连通性
docker compose exec app wget -qO- http://api:3000/health

# 检查网络
docker network ls
docker network inspect <project>_default
```

## 反模式（Anti-Patterns）

```
# 不良实践：在没有编排工具的情况下在生产环境使用 docker compose
# 生产环境的多容器负载应使用 Kubernetes, ECS, 或 Docker Swarm

# 不良实践：在没有卷的情况下在容器中存储数据
# 容器是瞬态的 -- 重新启动且没有卷时所有数据都会丢失

# 不良实践：以 root 用户运行
# 务必创建并使用非 root 用户

# 不良实践：使用 :latest 标签
# 锁定到特定版本以确保构建可复现

# 不良实践：一个巨大的容器包含所有服务
# 关注点分离：每个容器一个进程

# 不良实践：将密钥放入 docker-compose.yml
# 使用 .env 文件（加入 gitignore）或 Docker secrets
```
