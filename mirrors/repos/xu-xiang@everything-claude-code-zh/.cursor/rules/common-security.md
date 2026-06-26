---
description: "安全：强制检查、密钥管理、响应协议"
alwaysApply: true
---
# 安全指南 (Security Guidelines)

## 强制安全检查 (Mandatory Security Checks)

在进行任何提交 (commit) 之前：
- [ ] 严禁硬编码密钥（API 密钥 (API keys)、密码、令牌 (tokens)）
- [ ] 所有用户输入均已验证
- [ ] 预防 SQL 注入 (SQL injection)（使用参数化查询 (parameterized queries)）
- [ ] 预防跨站脚本攻击 (XSS prevention)（对 HTML 进行清理/转义 (sanitized HTML)）
- [ ] 已启用跨站请求伪造 (CSRF) 保护
- [ ] 身份验证 (Authentication) / 授权 (Authorization) 已验证
- [ ] 所有端点 (endpoints) 均已启用速率限制 (Rate limiting)
- [ ] 错误信息不会泄露敏感数据

## 密钥管理 (Secret Management)

- 严禁在源码中硬编码密钥 (secrets)
- 始终使用环境变量 (environment variables) 或密钥管理器 (secret manager)
- 在启动时验证必要的密钥是否存在
- 轮换 (Rotate) 任何可能已泄露的密钥

## 安全响应协议 (Security Response Protocol)

如果发现安全问题：
1. 立即停止 (STOP)
2. 使用 **security-reviewer** 智能体 (Agent)
3. 在继续前修复关键 (CRITICAL) 问题
4. 轮换 (Rotate) 任何泄露的密钥
5. 审查整个代码库以确认是否存在类似问题
