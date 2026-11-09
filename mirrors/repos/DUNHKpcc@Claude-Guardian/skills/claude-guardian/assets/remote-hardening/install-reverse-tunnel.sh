#!/usr/bin/env bash
# 进阶路线：在目标 Linux 机器上安装 systemd 常驻的反向 SSH 隧道（目标机:22 → 中转 VPS 的回环端口）。
# 脱敏版（2026-10-24）：由所有者的脚本整理。所有者的原脚本把私钥内嵌在脚本里，这里改为：
# 密钥由用户自己生成并把路径传入，脚本不生成、不内嵌、不输出任何密钥。
# 在目标机上由用户或经分级授权的 Agent 运行；先于 killswitch 安装（killswitch 会读取本 unit 的 user@IP 和 -p 端口放行隧道）。
#
# 用法:
#   sudo VPS_HOST=<中转VPS的IPv4> VPS_SSH_PORT=<VPS的sshd端口> KEY_PATH=<已有私钥路径> bash install-reverse-tunnel.sh install
#   bash install-reverse-tunnel.sh status | uninstall
# 可选: VPS_USER(默认 root)、REMOTE_BIND_PORT(VPS 回环上的落点端口，默认 2222)、LOCAL_SSH_PORT(默认 22)、TARGET_USER(默认 sudo 用户)
set -euo pipefail

UNIT_NAME="guardian-reverse-tunnel.service"
UNIT="/etc/systemd/system/$UNIT_NAME"
die() { echo "ERROR: $*" >&2; exit 1; }

VPS_HOST="${VPS_HOST:-}"
VPS_SSH_PORT="${VPS_SSH_PORT:-}"
VPS_USER="${VPS_USER:-root}"
KEY_PATH="${KEY_PATH:-}"
REMOTE_BIND_PORT="${REMOTE_BIND_PORT:-2222}"
LOCAL_SSH_PORT="${LOCAL_SSH_PORT:-22}"
TARGET_USER="${TARGET_USER:-${SUDO_USER:-}}"

do_install() {
  [ "$(id -u)" -eq 0 ] || die "需要 root（sudo）"
  [ -n "$TARGET_USER" ] || die "请设置 TARGET_USER（运行隧道的普通用户）"
  [[ "$VPS_HOST" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] \
    || die "VPS_HOST 必须是 IPv4 地址（killswitch 要按 IP 放行隧道，不接受域名）"
  [[ "$VPS_SSH_PORT" =~ ^[0-9]+$ ]] || die "请设置 VPS_SSH_PORT（VPS 上 sshd 的端口）"
  [ -f "$KEY_PATH" ] || die "KEY_PATH 指向的私钥不存在: $KEY_PATH（密钥由用户自己生成，脚本不内嵌）"
  local home; home=$(getent passwd "$TARGET_USER" | cut -d: -f6)
  [ -n "$home" ] || die "找不到用户 $TARGET_USER"

  # sudo 下复制出的文件属主是 root，sshd 客户端会拒读；必须 chown 和 chmod 600
  install -d -m 700 -o "$TARGET_USER" -g "$TARGET_USER" "$home/.ssh"
  install -m 600 -o "$TARGET_USER" -g "$TARGET_USER" "$KEY_PATH" "$home/.ssh/guardian_tunnel_key"

  cat > "$UNIT.tmp" <<UNIT_EOF
[Unit]
Description=Reverse SSH tunnel to relay VPS (127.0.0.1:$REMOTE_BIND_PORT -> this machine:$LOCAL_SSH_PORT)
After=network-online.target
Wants=network-online.target

[Service]
User=$TARGET_USER
Environment=HOME=$home
ExecStart=/usr/bin/ssh -NT -p $VPS_SSH_PORT \\
  -o ExitOnForwardFailure=yes \\
  -o ServerAliveInterval=15 \\
  -o ServerAliveCountMax=3 \\
  -o StrictHostKeyChecking=accept-new \\
  -o BatchMode=yes \\
  -i $home/.ssh/guardian_tunnel_key \\
  -R 127.0.0.1:$REMOTE_BIND_PORT:127.0.0.1:$LOCAL_SSH_PORT \\
  $VPS_USER@$VPS_HOST
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT_EOF
  install -Dm644 "$UNIT.tmp" "$UNIT" && rm -f "$UNIT.tmp"
  systemctl daemon-reload
  systemctl enable --now "$UNIT_NAME"
  sleep 5
  echo "隧道服务状态: $(systemctl is-active "$UNIT_NAME" || true)"
  echo "管理端连接: 先 ssh -p $VPS_SSH_PORT -N -L $REMOTE_BIND_PORT:127.0.0.1:$REMOTE_BIND_PORT $VPS_USER@$VPS_HOST，再 ssh -p $REMOTE_BIND_PORT $TARGET_USER@127.0.0.1"
  echo "若状态不是 active: VPS 上 journalctl -u ssh 看连接记录；客户端加 -vvv；authorized_keys 带 options 的行先换成无 options 的同公钥对照，再用 sshd -ddd 二分（见 advanced-route.md）"
}

do_status() { systemctl status "$UNIT_NAME" --no-pager || true; }

do_uninstall() {
  systemctl disable --now "$UNIT_NAME" 2>/dev/null || true
  rm -f "$UNIT"
  systemctl daemon-reload
  echo "uninstalled（私钥文件 ~/.ssh/guardian_tunnel_key 未删除，请自行处理）"
}

case "${1:-}" in
  install)   do_install ;;
  status)    do_status ;;
  uninstall) do_uninstall ;;
  *) die "用法: sudo VPS_HOST=... VPS_SSH_PORT=... KEY_PATH=... $0 install | status | uninstall" ;;
esac
