---
title: VPS IP 质量与网络测试清单（精简版）
source: https://www.nodeseek.com/post-183694-1
updated: 2026-10-21
tags:
  - VPS
  - IP 质量
  - 网络测试
---

# VPS IP 质量与网络测试清单（精简版）

2026-10-21 由所有者将原 NodeSeek《常用 VPS 脚本》目录精简为下列 IP 质量与网络测试项。原帖中的重装系统、改网络、改防火墙等其余命令不再随包收录。

## 使用前请注意

- 下面是第三方脚本和网站，**不是本项目的代码，也未经本项目审计**。多数是 `curl | bash` 远程执行，请先打开脚本地址看过内容，再在**你自己的 VPS** 上运行。
- 在用户的 VPS 上运行：用户自己运行，或 Agent 在用户授权的 SSH 会话里运行；不在不属于授权范围的机器上运行。Agent 运行前说明目标机器、脚本地址和流量成本。
- 测试结果只描述当时、该 IP、该方向的观测，不能推出“免封概率”或“IP 纯净度门槛”，也不能代替 Claude 官方对账号或地区的判断。
- 部分脚本会产生带宽、磁盘和 CPU 消耗。

## 脚本

IP 与网络质量：

```bash
bash <(curl -Ls https://Net.Check.Place)
```

```bash
bash <(curl -Ls https://IP.Check.Place)
```

综合基础信息（融合怪，基础模式）：

```bash
curl -fsSL https://raw.githubusercontent.com/spiritLHLS/ecs/main/ecs.sh -o ecs.sh && bash ecs.sh -m 1
```

流媒体与服务解锁：

```bash
bash <(curl -Ls https://check.unlock.media)
```

```bash
curl -fsSL https://raw.githubusercontent.com/oneclickvirt/UnlockTests/main/ut_install.sh | bash
ut -f 0
```

性能与综合测试：

```bash
curl -sL https://yabs.sh | bash
```

```bash
curl -fsL https://raw.githubusercontent.com/LemonBench/LemonBench/main/LemonBench.sh | bash -s -- --fast
```

## 在线网站

- https://ping.pe/
- https://ping0.cc/
- https://ipdata.co/
- https://www.ipqualityscore.com/
