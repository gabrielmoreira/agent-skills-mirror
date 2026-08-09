# reverse-skill — 平台无关项目入口

本仓库是一个**安全任务技能路由包**（逆向工程 / 渗透测试 / 安全分析）。`RULES.md` 是行为链唯一真相源。

## 路由

用户任务命中安全/逆向关键词时：

1. `skills/MASTER-ROUTING.md` 或 `powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/master-route.ps1 -Hint "<任务>"` → PRIMARY
2. 歧义时读 `skills/routing.md` 全矩阵（三轴：目标类型 / 用户意图 / 工具链）
3. 路由规则唯一事实源：`skills/config/routing.json`（改路由只改这里）

## 授权门禁（硬性）

- 对任何目标动手前：`powershell -File skills/scripts/case-init.ps1 -Hint "<任务>"` 生成 `work/<case>/scope.md`
- `auth.status=granted` + `network_profile` 就绪前**禁止 ACT**
- 证据链：`skills/ops/evidence-finding-path.md`；角色：`skills/ops/role-map.md`

## 首次运行

`skills/tool-index.md` 是 gitignored 的生成文件，首次使用前运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/refresh-tool-index.ps1
```

缺工具 → `skills/scripts/bootstrap-reverse.ps1`（清单能力，禁止猜路径）。

## 测试（改动后必跑）

```powershell
# 路由回归（162 用例，修改 routing.json 后必跑）
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/test-routing.ps1

# 结构一致性 + 供应链 pin gate
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/verify-routing-coherence.ps1

# 冒烟（verify + 脚本解析 + 快速路由）
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/smoke.ps1
```

## 客户端边界

- 路由核心、测试和工具清单必须与具体 AI 客户端解耦。
- Claude Code、Codex、Cursor、OpenCode 等客户端只能通过各自适配层接入，不得成为仓库默认身份或核心配置依赖。
- `skills/INDEX.md` 由 `extract-summaries.ps1` 从全部 `SKILL.md` 动态生成，不硬编码客户端或模块数量。
