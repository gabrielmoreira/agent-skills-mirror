# 多用户运行

QuantDinger v5 默认使用 PostgreSQL 多用户体系。`SINGLE_USER_MODE` 仅用于兼容旧环境，
正常部署应保持为 `false`。

[English](MULTI_USER_SETUP.md)

## 初始配置

推荐的一键安装程序会要求设置首个管理员并写入必要环境文件。源码部署至少需要配置：

```text
# .env
POSTGRES_PASSWORD=<高强度独立密码>

# .env
ADMIN_USER=<管理员用户名>
ADMIN_PASSWORD=<高强度独立密码>
SECRET_KEY=<独立随机密钥>
CREDENTIAL_ENCRYPTION_KEY=<稳定且独立的加密密钥>
SINGLE_USER_MODE=false
```

使用 `docker compose up -d --build` 启动。全新 PostgreSQL 数据库会通过
`backend_api_python/migrations/init.sql` 初始化；后续结构升级由一次性的 `migration`
服务负责。不要对已有数据库手工重复执行 `init.sql`。

## 管理员初始化

数据库没有用户时，后端会根据 `ADMIN_USER`、`ADMIN_PASSWORD` 和可选的 `ADMIN_EMAIL`
创建首个管理员。示例密码 `123456` 不能用于部署，一键安装程序会拒绝该密码。

已有数据库仍保留未修改的初始管理员时，后端可以同步配置中的非默认凭据。手工修改
数据库前，请先阅读[管理员凭据排错指南](ADMIN_AND_SETTINGS_TROUBLESHOOTING_CN.md)。

## 角色

| 角色 | 预期权限 |
| --- | --- |
| `viewer` | 仪表盘与只读页面 |
| `user` | 个人指标、回测、策略和组合 |
| `manager` | 用户能力加运营设置 |
| `admin` | 用户管理、设置、凭据等完整管理能力 |

后端权限校验始终是最终边界；前端隐藏菜单不等于完成鉴权。

## 当前 API 路径

- 登录态：`/api/auth/login`、`/api/auth/logout`、`/api/auth/info`
- 注册与恢复：`/api/auth/register`、`/api/auth/reset-password`
- 管理员用户管理：`/api/users/list`、`/api/users/create`、
  `/api/users/update`、`/api/users/delete`、`/api/users/reset-password`
- 用户自助：`/api/users/profile`、`/api/users/profile/update`、
  `/api/users/change-password`，以及 `/api/users/mfa/*` 下的 MFA 接口

请求与响应结构以 [Human OpenAPI](../api/README_CN.md) 为准。

## 生产检查清单

1. PostgreSQL 与 Redis 只放在私有网络或 loopback。
2. 持久保存 `SECRET_KEY`；更换它会使现有会话失效。
3. 持久保存 `CREDENTIAL_ENCRYPTION_KEY`；更换它可能导致已有凭据无法解密。
4. 允许远程登录前启用 HTTPS。
5. 备份 PostgreSQL，并实际验证恢复流程。
6. 定期检查管理员登录日志、MFA、用户状态与角色分配。

当前仓库没有受维护的 SQLite 自动迁移命令。旧 SQLite 安装应先保留可验证备份，再设计
受控的数据迁移流程，不要运行已经不存在的旧脚本。
