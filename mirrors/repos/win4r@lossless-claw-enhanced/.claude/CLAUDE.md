# lossless-claw-enhanced 运维规则

## 第一步永远是读手册

任何运维操作开始前，必须先读：
1. `~/Documents/运维手册/操作指南.md`
2. RecallNest `bot-ops` 记忆

## 仓库权限

用户对此仓库有全权管理（maintainer），approved + CI 全绿后**直接 merge**，不需要给自己提 PR。

## 验证方式

配置变更后：`docker exec <容器名> openclaw doctor` 验证
