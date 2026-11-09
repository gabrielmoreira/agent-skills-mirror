#!/usr/bin/env bash
# VPS 入站防火墙（nftables，Ubuntu）。参考 VM 的 install-flclash-killswitch.sh 的结构：
# 原子替换规则 + 应用后 180 秒保险丝（没 confirm 就自动回滚）+ 开机自启。
#
# 适用：VPS 自己的 IP 就是出口（出站不限制）。入站默认丢弃，只放行：
#   回环、已建立连接、来自 ADMIN_NET 的 SSH 和 ping、云厂商 DHCP、IPv6 邻居发现。
#   远程桌面的 5900 / 6080 因此不会暴露到公网，只能经 SSH 隧道访问。
# 不适用：VPS 上还跑 FlClash TUN 套家宽出口。那种情况直接用 VM 的 install-flclash-killswitch.sh，
#   把 LAN_NET 设成你的管理来源网段（ADMIN_NET）、NIC 设成 VPS 的网卡。
#
# 由用户在服务器上自己运行；先在云厂商控制台确认有独立的救援/VNC 入口，再操作，不要只靠 SSH。
# 用法（sudo 运行）:
#   ADMIN_NET=<你的管理来源> vps-guard.sh render    只打印规则，先审阅，不改系统
#   ADMIN_NET=<你的管理来源> vps-guard.sh install   安装并应用（带保险丝）
#   vps-guard.sh confirm                            180 秒内确认，取消自动回滚
#   vps-guard.sh status | uninstall
# ADMIN_NET 必填：你的固定公网 IP/32，或 Tailscale 网段 100.64.0.0/10。SSH_PORT 默认 22。
# MOSH=1 可选（默认 0 不放行）：只对 ADMIN_NET 放行 mosh 的 UDP 端口，MOSH_PORTS 默认 60000-61000。
#   mosh 握手走 SSH，会话走这段 UDP；不开这个开关，启用 vps-guard 后 mosh 连不上。
set -euo pipefail

ADMIN_NET="${ADMIN_NET:-}"
SSH_PORT="${SSH_PORT:-22}"
MOSH="${MOSH:-0}"
MOSH_PORTS="${MOSH_PORTS:-60000-61000}"
TABLE="vps_guard"
NFT_FILE="/etc/vps-guard.nft"
UNIT="/etc/systemd/system/vps-guard.service"
CONFIRM_FLAG="/tmp/vps-guard-confirm"
ARM_LOG="/tmp/vps-guard-armed.log"

die() { echo "ERROR: $*" >&2; exit 1; }

build_nft() {
  [ -n "$ADMIN_NET" ] || die "请先设置 ADMIN_NET（你的管理来源，如 203.0.113.7/32 或 100.64.0.0/10），例如: sudo ADMIN_NET=203.0.113.7/32 $0 install"
  [[ "$SSH_PORT" =~ ^[0-9]+$ ]] || die "SSH_PORT 必须是数字"
  local mosh_rule=""
  case "$MOSH" in
    0) ;;
    1)
      [[ "$MOSH_PORTS" =~ ^([0-9]{1,5})-([0-9]{1,5})$ ]] || die "MOSH_PORTS 必须是 起-止 端口段，如 60000-61000"
      local lo=$((10#${BASH_REMATCH[1]})) hi=$((10#${BASH_REMATCH[2]}))
      { [ "$lo" -ge 1024 ] && [ "$hi" -le 65535 ] && [ "$lo" -le "$hi" ]; } || die "MOSH_PORTS 须在 1024-65535 之间且起点不大于终点"
      mosh_rule="        ip saddr $ADMIN_NET udp dport $lo-$hi counter accept"
      ;;
    *) die "MOSH 只能是 0 或 1" ;;
  esac
  cat <<NFT
add table inet $TABLE
delete table inet $TABLE
table inet $TABLE {
    chain input {
        type filter hook input priority 10; policy drop;
        iifname "lo" counter accept
        ct state established,related counter accept
        ip saddr $ADMIN_NET tcp dport $SSH_PORT counter accept
        ip saddr $ADMIN_NET icmp type echo-request counter accept
${mosh_rule:+$mosh_rule
}        udp sport 67 udp dport 68 counter accept
        ip6 nexthdr icmpv6 icmpv6 type { nd-neighbor-solicit, nd-neighbor-advert, nd-router-advert } counter accept
        counter
    }
}
NFT
}

apply_armed() {
  build_nft | install -Dm600 /dev/stdin "$NFT_FILE"
  nft -c -f "$NFT_FILE" || die "规则检查失败，未应用"
  # 保险丝：后台应用，180 秒内没有 confirm 标志就自动回滚（脱离 SSH 会话运行）
  nohup bash -c "
    nft -f $NFT_FILE
    rm -f $CONFIRM_FLAG
    echo APPLIED \$(date +%T) > $ARM_LOG
    for i in \$(seq 1 18); do
      sleep 10
      [ -f $CONFIRM_FLAG ] && { echo CONFIRMED \$(date +%T) >> $ARM_LOG; exit 0; }
    done
    nft delete table inet $TABLE 2>/dev/null
    echo ROLLED_BACK \$(date +%T) >> $ARM_LOG
  " >/dev/null 2>&1 &
  echo "armed: 规则已应用，180 秒内请在另一个 SSH 会话执行 '$0 confirm'，否则自动回滚"
}

do_install() {
  cat > "$UNIT" <<'UNITEOF'
[Unit]
Description=VPS inbound firewall (vps-guard)
DefaultDependencies=no
After=local-fs.target systemd-modules-load.service
Before=network-pre.target nftables.service ufw.service
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/nft -f /etc/vps-guard.nft
ExecStopPost=-/usr/sbin/nft delete table inet vps_guard
RemainAfterExit=yes

[Install]
WantedBy=network-pre.target
UNITEOF
  systemctl daemon-reload
  systemctl enable vps-guard.service >/dev/null 2>&1
  apply_armed
}

do_confirm() { touch "$CONFIRM_FLAG"; sleep 1; cat "$ARM_LOG" 2>/dev/null || true; }

do_status() {
  systemctl is-enabled vps-guard.service 2>&1 || true
  nft list table inet "$TABLE" 2>/dev/null || echo "(table 不存在，当前没有入站防火墙)"
}

do_uninstall() {
  systemctl disable --now vps-guard.service 2>/dev/null || true
  rm -f "$UNIT" "$NFT_FILE"
  nft delete table inet "$TABLE" 2>/dev/null || true
  systemctl daemon-reload
  echo "uninstalled"
}

case "${1:-}" in
  render)    build_nft ;;
  install)   do_install ;;
  confirm)   do_confirm ;;
  status)    do_status ;;
  uninstall) do_uninstall ;;
  *) die "用法: ADMIN_NET=<管理来源> [MOSH=1] $0 [render|install|confirm|status|uninstall]" ;;
esac
