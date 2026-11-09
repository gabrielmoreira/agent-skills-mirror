#!/usr/bin/env bash
# 脱敏版（2026-10-21）：由所有者的脚本整理，逻辑不变。只把个人信息改成参数：
#   LAN_NET 必须由用户设置（客机所在局域网网段，如 192.168.1.0/24）；
#   EXPECTED_EXIT_IP 可选，用于 test 比对固定出口；服务用户改为当前 sudo 用户。
# 在 Linux 客机（如 Omarchy）里由用户自己运行；先打快照，并在虚拟机控制台操作，不要只靠 SSH。
# FlClash fail-closed killswitch v3
# 目标：整机一切流量只能 1) 走 FlClash TUN 出去，或 2) 发往 profile 中各 VLESS 节点真实服务端 IP:port。
# v3 变更：
#   - hook 改到 priority 10（conntrack 之后、ufw 之后），修复 v2 在 raw(-300) 上 ct state 不可靠导致的 SSH 锁死
#   - 解析节点时过滤 fake-ip(198.18.0.0/15)，域名解析失败时经隧道 DoH 取真实 IP
#   - nft 文件采用 add->delete->重建 单事务原子替换，不再有半套状态
#   - apply-armed: 死亡保险丝，应用后 180s 内未确认自动回滚
#   - refresh 定时刷新节点 IP（systemd timer），节点切换/服务器变更后自动跟进
# 用法:
#   install-flclash-killswitch.sh install        安装（含 armed 首次应用+保险丝）
#   install-flclash-killswitch.sh refresh        重新解析节点并原子替换规则
#   install-flclash-killswitch.sh confirm        确认本次应用（取消保险丝）
#   install-flclash-killswitch.sh status|test|uninstall
set -euo pipefail

NIC="${NIC:-enp0s1}"
TUN="${TUN:-FlClash}"
LAN_NET="${LAN_NET:-}"            # 必填：客机局域网网段，例如 192.168.1.0/24
EXPECTED_EXIT_IP="${EXPECTED_EXIT_IP:-}"   # 可选：固定出口的 IP，test 时比对
SSH_PORT="${SSH_PORT:-22}"
TABLE="flclash_killswitch"
NFT_FILE="/etc/flclash-killswitch.nft"
UNIT="/etc/systemd/system/flclash-killswitch.service"
RUNIT="/etc/systemd/system/flclash-killswitch-refresh.service"
RTIMER="/etc/systemd/system/flclash-killswitch-refresh.timer"
# 反向隧道 systemd unit（进阶路线用；文件存在才生效）：解析其 ExecStart 里的 user@IP 和 -p 端口，
# 加入独立白名单，保证隧道断线后能重连。不用反向隧道就保持默认，文件不存在则忽略。
TUNNEL_UNIT="${TUNNEL_UNIT:-/etc/systemd/system/guardian-reverse-tunnel.service}"
CONFIRM_FLAG="/tmp/ks-confirm"
ARM_LOG="/tmp/ks-armed.log"

# sudo 会重置 HOME，还原真实用户家目录
REAL_HOME="${SUDO_HOME:-$(getent passwd "${SUDO_UID:-$(id -u)}" | cut -d: -f6)}"
CFG_DIR="$REAL_HOME/.local/share/com.follow.clash"

s() { sudo "$@"; }
die() { echo "ERROR: $*" >&2; exit 1; }

is_fakeip() { [[ "$1" =~ ^198\.1[89]\. ]] ; }

resolve_endpoints() {
  local profile
  profile=$(find "$CFG_DIR/profiles" -maxdepth 1 -type f -name '*.yaml' -printf '%T@ %p\n' 2>/dev/null \
            | sort -n | tail -1 | cut -d' ' -f2-)
  [ -n "${profile:-}" ] || die "未找到 FlClash profile"
  echo "profile: $(basename "$profile")" >&2

  mapfile -t servers < <(awk '/^[[:space:]]+server:[[:space:]]*/ {gsub(/["'"'"' ]/, "", $2); print $2}' "$profile" | sort -u)
  mapfile -t ports   < <(awk '/^[[:space:]]+port:[[:space:]]*/ {gsub(/["'"'"' ]/, "", $2); if ($2 ~ /^[0-9]+$/) print $2}' "$profile" | sort -nu)
  [ "${#ports[@]}" -gt 0 ] || die "profile 中未找到端口"

  local raw=() srv ip
  for srv in "${servers[@]}"; do
    if [[ "$srv" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
      raw+=("$srv")
      continue
    fi
    local got=0
    while read -r ip _; do
      if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] && ! is_fakeip "$ip"; then
        raw+=("$ip"); got=1
      fi
    done < <(getent ahostsv4 "$srv" 2>/dev/null || true)
    # 系统解析被 fake-ip 劫持时，经隧道 DoH 取真实 A 记录
    if [ "$got" -eq 0 ]; then
      echo "  $srv: 系统解析疑似 fake-ip，走 DoH..." >&2
      local doh
      doh=$(curl -4 -s --max-time 15 -H 'accept: application/dns-json' \
            "https://1.1.1.1/dns-query?name=${srv}&type=A" 2>/dev/null || true)
      [ -n "$doh" ] && while read -r ip; do
        [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] && raw+=("$ip")
      done < <(python3 -c '
import json,sys
try:
    d=json.load(sys.stdin)
    for a in d.get("Answer",[]):
        if a.get("type")==1: print(a["data"])
except Exception: pass' <<<"$doh")
    fi
  done

  mapfile -t ips < <(printf '%s\n' "${raw[@]}" | sort -u)
  [ "${#ips[@]}" -gt 0 ] || die "未能解析出任何 VLESS 服务端真实 IP（隧道可用吗？）"
  IP_LIST=$(IFS=,; echo "${ips[*]}")
  PORT_LIST=$(IFS=,; echo "${ports[*]}")
  echo "endpoints: ${#ips[@]} IPs / ports: ${PORT_LIST}" >&2

  TUNNEL_IP_LIST=""; TUNNEL_PORT_LIST=""
  if [ -f "$TUNNEL_UNIT" ]; then
    local tip tport
    tip=$(grep -oE '@[0-9]{1,3}(\.[0-9]{1,3}){3}\b' "$TUNNEL_UNIT" | head -1 | tr -d '@')
    tport=$(grep -oE '\-p [0-9]+' "$TUNNEL_UNIT" | head -1 | awk '{print $2}')
    if [ -n "$tip" ] && [ -n "$tport" ]; then
      TUNNEL_IP_LIST="$tip"; TUNNEL_PORT_LIST="$tport"
      echo "tunnel: $tip:$tport（加入白名单，保证反向隧道可重连）" >&2
    else
      echo "WARN: $TUNNEL_UNIT 存在但没解析出 user@IP 和 -p 端口；隧道不会进白名单，启用后可能失联" >&2
    fi
  fi
}

build_nft() {
  [ -n "$LAN_NET" ] || die "请先设置 LAN_NET（客机局域网网段，如 192.168.1.0/24），例如: sudo LAN_NET=192.168.1.0/24 $0 install"
  local ip_elems port_elems
  ip_elems=$(echo "$IP_LIST" | sed 's/,/, /g')
  port_elems=$(echo "$PORT_LIST" | sed 's/,/, /g')
  local tunnel_sets=""
  [ -n "$TUNNEL_IP_LIST" ] && tunnel_sets="
    set tunnel4 {
        type ipv4_addr
        elements = { $(echo "$TUNNEL_IP_LIST" | sed 's/,/, /g') }
    }
    set tunnel_ports {
        type inet_service
        elements = { $(echo "$TUNNEL_PORT_LIST" | sed 's/,/, /g') }
    }"
  local tunnel_rules=""
  [ -n "$TUNNEL_IP_LIST" ] && tunnel_rules="
        oifname \"$NIC\" ip daddr @tunnel4 tcp dport @tunnel_ports ct state new counter accept"
  cat <<EOF
add table inet $TABLE
delete table inet $TABLE
table inet $TABLE {
    set proxy4 {
        type ipv4_addr
        elements = { $ip_elems }
    }
    set proxy_ports {
        type inet_service
        elements = { $port_elems }
    }$tunnel_sets
    chain output {
        type filter hook output priority 10; policy drop;
        oifname "lo" counter accept
        oifname "$TUN" counter accept
        ct state established,related counter accept
        oifname "$NIC" udp sport 68 udp dport 67 counter accept
        oifname "$NIC" udp sport 546 udp dport 547 counter accept
        oifname "$NIC" ip daddr @proxy4 tcp dport @proxy_ports counter accept
        oifname "$NIC" ip daddr @proxy4 udp dport @proxy_ports counter accept$tunnel_rules
        counter
    }
    chain input {
        type filter hook input priority 10; policy drop;
        iifname "lo" counter accept
        iifname "$TUN" counter accept
        ct state established,related counter accept
        iifname "$NIC" ip saddr $LAN_NET tcp dport $SSH_PORT counter accept
        iifname "$NIC" ip saddr $LAN_NET icmp type echo-request counter accept
        iifname "$NIC" udp sport 67 udp dport 68 counter accept
        counter
    }
}
EOF
}

write_rules_file() {
  build_nft > "$NFT_FILE.tmp"
  s install -Dm600 "$NFT_FILE.tmp" "$NFT_FILE"
  rm -f "$NFT_FILE.tmp"
}

apply_armed() {
  write_rules_file
  # 保险丝：后台应用，180 秒内没有 confirm 标志就自动回滚（脱离 SSH 会话运行）
  s bash -c "nohup bash -c '
    nft -f $NFT_FILE
    rm -f $CONFIRM_FLAG
    echo APPLIED \$(date +%T) > $ARM_LOG
    for i in \$(seq 1 18); do
      sleep 10
      [ -f $CONFIRM_FLAG ] && { echo CONFIRMED \$(date +%T) >> $ARM_LOG; exit 0; }
    done
    nft delete table inet $TABLE 2>/dev/null
    echo ROLLED_BACK \$(date +%T) >> $ARM_LOG
  ' >/dev/null 2>&1 &"
  echo "armed: 规则已应用，180 秒内请执行 'install-flclash-killswitch.sh confirm'，否则自动回滚"
}

do_install() {
  resolve_endpoints
  ip link show "$TUN" >/dev/null 2>&1 \
    || echo "WARN: TUN $TUN 当前不存在，装完后外网完全不可用（fail-closed 语义，SSH 不受影响）" >&2

  cat > "$UNIT.tmp" <<'EOF'
[Unit]
Description=FlClash fail-closed outbound firewall (killswitch v3)
DefaultDependencies=no
After=local-fs.target systemd-modules-load.service
Before=network-pre.target nftables.service ufw.service
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/usr/bin/nft -f /etc/flclash-killswitch.nft
ExecStopPost=-/usr/bin/nft delete table inet flclash_killswitch
RemainAfterExit=yes

[Install]
WantedBy=network-pre.target
EOF
  s install -Dm644 "$UNIT.tmp" "$UNIT" && rm -f "$UNIT.tmp"

  # 开机后定期刷新节点 IP（服务器换 IP / 换节点不用手动处理）
  cat > "$RUNIT.tmp" <<EOF
[Unit]
Description=Refresh FlClash killswitch endpoint sets
After=network-online.target flclash-killswitch.service
Wants=network-online.target

[Service]
Type=oneshot
User=${SUDO_USER:-$(id -un)}
Environment=SUDO_HOME=$REAL_HOME
ExecStart=$REAL_HOME/install-flclash-killswitch.sh refresh
EOF
  s install -Dm644 "$RUNIT.tmp" "$RUNIT" && rm -f "$RUNIT.tmp"

  cat > "$RTIMER.tmp" <<'EOF'
[Unit]
Description=Hourly refresh of FlClash killswitch endpoints

[Timer]
OnBootSec=3min
OnUnitActiveSec=1h
Persistent=true

[Install]
WantedBy=timers.target
EOF
  s install -Dm644 "$RTIMER.tmp" "$RTIMER" && rm -f "$RTIMER.tmp"

  s systemctl daemon-reload
  s systemctl enable flclash-killswitch.service >/dev/null 2>&1
  # timer 只 enable 不 start 时处于 enabled-but-inactive，要到下次开机才生效；这里一并 start，并打印下次触发时间
  s systemctl enable --now flclash-killswitch-refresh.timer >/dev/null 2>&1
  systemctl list-timers flclash-killswitch-refresh.timer --no-pager 2>/dev/null || true
  apply_armed
}

do_confirm() { touch "$CONFIRM_FLAG"; sleep 1; cat "$ARM_LOG" 2>/dev/null || true; }

do_refresh() {
  resolve_endpoints
  local old new
  old=$(s nft list set inet "$TABLE" proxy4 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort -u | tr '\n' ' ' || true)
  write_rules_file
  s nft -f "$NFT_FILE"
  new=$(echo "$IP_LIST" | tr ',' ' ')
  echo "refreshed: old=[$old] new=[$new]"
}

do_status() {
  echo "== service/timer =="
  systemctl is-enabled flclash-killswitch.service 2>&1 || true
  systemctl is-active  flclash-killswitch.service 2>&1 || true
  systemctl is-active  flclash-killswitch-refresh.timer 2>&1 || true
  echo "== table =="
  s nft list table inet "$TABLE" 2>/dev/null || echo "(table 不存在 — 当前无 killswitch)"
}

do_test() {
  echo "[1] 经隧道出口（应为 ${EXPECTED_EXIT_IP:-你固定的出口 IP}）:"
  EXPECTED_EXIT_IP="$EXPECTED_EXIT_IP" curl -4 -s --max-time 12 https://ipinfo.io/json | python3 -c '
import json,os,sys
try:
    d=json.load(sys.stdin); ip=d.get("ip","?"); want=os.environ.get("EXPECTED_EXIT_IP","")
    ok=("YES" if ip==want else "NO") if want else "(未设置 EXPECTED_EXIT_IP)"
    print(f"    exit={ip} country={d.get(chr(99)+chr(111)+chr(117)+chr(110)+chr(116)+chr(114)+chr(121))} pinned={ok}")
except Exception as e: print("    FAIL:",e)'
  echo "[2] DNS（应可用，走隧道）:"
  getent hosts archlinux.org >/dev/null 2>&1 && echo "    OK" || echo "    FAIL"
  echo "[3] OUTPUT 链 drop 计数（浏览几分钟后应为 0 或极小）:"
  s nft list chain inet "$TABLE" output 2>/dev/null | grep -E "^\s+counter" | tail -1 || true
  echo "[4] 手动项: 浏览器开 browserleaks.com/webrtc 与 dnsleaktest.com，确认无真实 IP/真实 DNS"
  echo "[5] 手动项: pkill FlClashCore 后确认 curl/DNS 全死，重启 FlClash 恢复"
}

do_uninstall() {
  s systemctl disable --now flclash-killswitch.service flclash-killswitch-refresh.timer 2>/dev/null || true
  s rm -f "$UNIT" "$RUNIT" "$RTIMER"
  s nft delete table inet "$TABLE" 2>/dev/null || true
  s systemctl daemon-reload
  echo "uninstalled"
}

case "${1:-install}" in
  install)   do_install ;;
  refresh)   do_refresh ;;
  confirm)   do_confirm ;;
  status)    do_status ;;
  test)      do_test ;;
  uninstall) do_uninstall ;;
  *) die "用法: $0 [install|refresh|confirm|status|test|uninstall]" ;;
esac
