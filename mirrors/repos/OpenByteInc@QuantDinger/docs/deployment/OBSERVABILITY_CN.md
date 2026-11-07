# 可观测性

[English](OBSERVABILITY.md)

后端通过 `GET /metrics` 暴露 Prometheus 指标，并在 HTTP 响应中传递经过校验的
`X-Request-ID`。Docker 默认使用 JSON 日志，包含进程角色与请求 ID。

## 启动监控栈

```bash
python backend_api_python/scripts/check_production_config.py --env-file .env --require-grafana
docker compose \
  -f docker-compose.yml \
  -f docker-compose.observability.yml \
  up -d --build
```

本机默认地址：

| 服务 | 地址 | 用途 |
| --- | --- | --- |
| Grafana | `http://127.0.0.1:3000` | 仪表盘与趋势分析 |
| Prometheus | `http://127.0.0.1:9090` | 指标采集、存储与查询 |
| Alertmanager | `http://127.0.0.1:9093` | 告警分组、静默与发送 |

Grafana 会自动配置 Prometheus 数据源和 `QuantDinger Runtime Overview` 仪表盘。
将 Grafana 放到反向代理后之前，必须修改 `GRAFANA_ADMIN_PASSWORD`。

## 默认监控范围

内置规则覆盖 API 错误率与延迟、Worker 心跳过期、PostgreSQL/Redis 可用性，以及
任务 Redis 内存压力。生产使用前，需要在 `ops/alertmanager/alertmanager.yml` 中配置
真实的通知接收器并测试告警链路。

不要把 `/metrics`、Prometheus、Alertmanager 或 Grafana 直接暴露到公网。保留默认
loopback 绑定，或放入私有网络并使用带认证的反向代理。
