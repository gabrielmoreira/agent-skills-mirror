#!/usr/bin/env bash
# 脱敏版（2026-10-21）：由所有者的脚本整理。原脚本按 QEMU 的 shared NAT 写，放行 10.0.2.2；
# VM 路线现在要求 LAN 独立网卡，所以放行来源改为必填参数 SSH_SRC（你的管理机在局域网里的地址或网段）。
# 在 Linux 客机的控制台里由用户自己运行：开启 sshd，若 ufw 已启用，只放行 SSH_SRC 到 22 端口。
# 用法: sudo SSH_SRC=<管理机地址或网段> NIC=<客机网卡名> bash enable-guest-ssh.sh
set -euo pipefail

NIC="${NIC:-enp0s1}"          # 用 ip link 确认客机网卡名
SSH_SRC="${SSH_SRC:-}"        # 必填（ufw 启用时）：例如 192.168.1.10 或 192.168.1.0/24

# 全新 Omarchy 默认没有 sshd：先装 openssh，否则 sshd -t 直接失败，反向隧道的终点 127.0.0.1:22 也无人监听
sudo pacman -S --needed --noconfirm openssh
sudo sshd -t
sudo systemctl enable --now sshd

if sudo ufw status 2>/dev/null | grep -q '^Status: active'; then
  [ -n "$SSH_SRC" ] || { echo '请先设置 SSH_SRC（管理机地址或网段）' >&2; exit 1; }
  sudo ufw allow in on "$NIC" from "$SSH_SRC" to any port 22 proto tcp
fi

printf 'sshd: '
sudo systemctl is-active sshd
printf 'listening: '
ss -lnt | awk '$4 ~ /:22$/ {print $4; found=1} END {if (!found) print "not-listening"}'
