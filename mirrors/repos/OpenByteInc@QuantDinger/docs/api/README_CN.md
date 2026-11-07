# QuantDinger Web API（OpenAPI）

本目录提供面向人类用户会话的 REST API 契约。它与 `/api/agent/v1` 的 Agent Gateway 分开维护，请勿混用人类 JWT 和 Agent Token。

| 文件 | 用途 |
|---|---|
| [openapi.yaml](openapi.yaml) | 已提交的权威接口契约，由后端导出脚本更新 |
| [index.html](index.html) | 静态 ReDoc 查看器，需要通过 HTTP 打开 |

## 本地查看

浏览器从 `file://` 打开 `index.html` 时不能加载同目录 YAML。请启动静态服务器：

```bash
cd docs/api
python -m http.server 8080
# 打开 http://localhost:8080/index.html
```

QuantDinger 后端启用调试模式或设置 `OPENAPI_ENABLED=true` 后，也可访问：

- Swagger UI：`http://localhost:5000/api/docs/swagger`
- ReDoc：`http://localhost:5000/api/docs/redoc`

## 更新契约

修改接口实现后，在仓库中重新导出并提交差异：

```bash
cd backend_api_python
pip install -r requirements.txt
python scripts/export_openapi.py
```

公共响应封装、认证和 Public/Internal 分层见 [API 约定](../architecture/API_CONVENTIONS.md)（英文）。Agent 接口见 [Agent 文档入口](../agent/README_CN.md) 与 [Agent OpenAPI](../agent/agent-openapi.json)。
