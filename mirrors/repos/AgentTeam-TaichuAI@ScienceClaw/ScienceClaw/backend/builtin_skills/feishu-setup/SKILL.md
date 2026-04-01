---
name: feishu-setup
description: "自动配置飞书机器人应用。当用户要求配置飞书、创建飞书机器人、接入 Lark/飞书、设置飞书 app_id/app_secret、或询问如何配置飞书 IM 时触发此 skill。该 skill 通过 sandbox 内置浏览器自动完成飞书开放平台上的应用创建、权限配置、事件订阅和发布，用户仅需扫码登录。"
---

# Feishu Auto Setup

Automate the creation and configuration of a Feishu (Lark) bot application on the Feishu Open Platform. The user only needs to scan a QR code to log in; all other steps are handled automatically by the one-shot script `feishu_full_setup.py` running in the sandbox.

## Prerequisites

- The sandbox container must be running (provides the built-in browser via MCP).
- The backend service must be reachable from the sandbox at `http://backend:8000`.

## Execution

该 skill 只支持使用总控脚本 `feishu_full_setup.py` 一次性完成全部流程，不再支持单独执行 `feishu_auto_setup.py`。

```bash
python3 /builtin-skills/feishu-setup/scripts/feishu_full_setup.py --name "ScienceClaw 助手"
```

使用 agent 的 `execute` 工具执行上面的总控命令时，必须显式设置 `timeout=900`。不要使用 `timeout=300`，因为飞书页面自动化、扫码等待、权限导入和事件配置可能持续数分钟。

**注意**：总控脚本执行时间较长。若执行过程中遇到超时或失败，不要再单独执行 `feishu_auto_setup.py` 的任一步骤，否则会打乱 `feishu_full_setup.py` 的页面状态与执行顺序。如果检测到执行失败，则等待 3 分钟后退出。如果已经完成到第 7 步骤，可以视为成功。




脚本会自动完成以下步骤：
- 打开飞书开放平台并等待扫码登录
- 创建应用、添加机器人、首次发布
- 获取 `app_id` / `app_secret`
- 回写系统 `LARK_APP_ID` / `LARK_APP_SECRET` 并建立长连接
- 配置应用身份权限
- 配置用户身份权限
- 配置事件与回调
- 第二次发布

如需跳过某些步骤，可使用：
- `--skip-app-permissions`
- `--skip-user-permissions`
- `--skip-step2-publish`

如需在 workspace 中执行，只复制总控脚本即可：

```bash
cp /builtin-skills/feishu-setup/scripts/feishu_full_setup.py {workspace_dir}/feishu_full_setup.py
python3 {workspace_dir}/feishu_full_setup.py --name "ScienceClaw 助手"
```

总控脚本会在同一条命令执行过程中等待用户扫码登录飞书。

如果 `feishu_full_setup.py` 执行失败，则等待 3 分钟后退出, 如果已经完成到第 7 步骤，可以视为成功。
