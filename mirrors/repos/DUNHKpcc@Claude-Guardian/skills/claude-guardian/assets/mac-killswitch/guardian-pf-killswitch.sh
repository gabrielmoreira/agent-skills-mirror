#!/bin/bash
# Claude-Guardian：macOS 本机路线的 PF killswitch（ADR-054，2026-11-01 采用 PF；Issue #25 已报告现场修正版真机通过，随包版本与覆盖范围见 local-firewall-prompts.md）。
# 起因：Issue #17 实测 LuLu 按进程过滤，早于路由，分不出“走 TUN”和“直连”，只放行核心会把正常 TUN 流量一起拦掉。
# 思路：按网卡拦，不按进程拦。物理网卡只放行发往节点真实 IP:端口 的连接（加 DHCP，可选 DNS、局域网例外），
#       其余出站一律丢弃；TUN（utun）和回环不受影响。核心或 TUN 停掉后，应用流量落到物理网卡，被拦，不会直连。
# 规则放在 com.apple/claude-guardian 子 anchor 里，不改 /etc/pf.conf；用 pfctl -E/-X 的引用计数开关 PF。
# 兼容 macOS 自带的 bash 3.2（不用 mapfile、关联数组）。
# 用法（除 render 外都要 sudo）：
#   render                只打印将要加载的规则，不改系统
#   apply                 加载规则并布置保险丝（默认 180 秒），不 confirm 就自动撤销；节点或网卡变了也用它重载
#   confirm               确认本次规则：取消保险丝，并作为开机加载的版本
#   status                PF 状态、本 anchor 规则与命中计数、网卡覆盖检查、DNS 路径、最近事件
#   dns                   各网络服务的 DNS 设置、当前 DNS 走哪张网卡（不需要 sudo，不改系统）
#   blocked [秒数]         抓一段时间被拦的包，按目的地类别和端口汇总，不输出 IP（默认 60 秒）
#   rollback              立即撤销运行中的规则（不删开机项）
#   persist | unpersist   安装／移除开机自动加载（LaunchDaemon）
#   uninstall             rollback + unpersist + 删除本脚本生成的文件
# 可选环境变量：
#   CONFIG          Clash Verge Rev 运行配置，默认 ~/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml
#   NODE_IPS        逗号分隔的节点 IPv4；设置后不读配置，须同时设 NODE_PORTS
#   NODE_PORTS      逗号分隔的节点端口
#   NICS            逗号分隔的物理网卡，默认 networksetup 列出的全部硬件端口加当前默认路由网卡
#   BOOTSTRAP_DNS   逗号分隔的 DNS 服务器 IPv4；节点是域名、核心重启后要解析节点时才填
#   LAN_NET         逗号分隔的局域网网段（如 192.168.1.0/24）；要直连 NAS、打印机时才填
#   FUSE_SECONDS    保险丝秒数，默认 180
set -euo pipefail

ANCHOR="com.apple/claude-guardian"
STATE_DIR="/Library/Application Support/ClaudeGuardian/pf-killswitch"
RULES_CONFIRMED="$STATE_DIR/rules.conf"
RULES_PENDING="$STATE_DIR/rules.pending.conf"
CONFIRM_FLAG="$STATE_DIR/confirm"
FUSE_PID="$STATE_DIR/fuse.pid"
LOG="$STATE_DIR/events.log"
INSTALLED_SCRIPT="$STATE_DIR/guardian-pf-killswitch.sh"
# 令牌放 /var/run：重启后清空，开机加载时据此判断本次是否已开过 PF
TOKEN_FILE="/var/run/claude-guardian-pf.token"
LABEL="com.claude-guardian.pf-killswitch"
PLIST="/Library/LaunchDaemons/$LABEL.plist"
FUSE_SECONDS="${FUSE_SECONDS:-180}"
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

die() { echo "ERROR: $*" >&2; exit 1; }
warn() { echo "WARN: $*" >&2; }
log_event() { echo "$1 $(date '+%F %T')" >> "$LOG"; }
need_root() { [ "$(id -u)" -eq 0 ] || die "这一步要 sudo：sudo $0 ${1:-}"; }
need_mac() { [ "$(uname -s)" = "Darwin" ] || die "只用于 macOS"; }

is_ipv4() {
  [[ "$1" =~ ^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$ ]] || return 1
  local i
  for i in 1 2 3 4; do [ "${BASH_REMATCH[$i]}" -le 255 ] || return 1; done
}
is_fakeip() { [[ "$1" =~ ^198\.1[89]\. ]]; }
is_cidr4() { [[ "$1" =~ ^([0-9.]+)/([0-9]{1,2})$ ]] && is_ipv4 "${1%/*}" && [ "${1#*/}" -le 32 ]; }
is_port() { [[ "$1" =~ ^[0-9]{1,5}$ ]] && [ "$1" -ge 1 ] && [ "$1" -le 65535 ]; }
is_nic() { [[ "$1" =~ ^[a-z]+[0-9]+$ ]]; }
csv_words() { echo "$1" | tr ',' ' '; }
uniq_words() { printf '%s\n' "$@" | awk 'NF' | sort -u | tr '\n' ' ' | sed 's/ *$//'; }

user_home() {
  if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ] && command -v dscl >/dev/null 2>&1; then
    dscl . -read "/Users/$SUDO_USER" NFSHomeDirectory 2>/dev/null | awk '{print $2}'
  else
    echo "$HOME"
  fi
}

# 只读 proxies: 段，兼容块写法和 {name: a, server: b, port: 443} 行内写法
extract_endpoints() {
  awk -v sq="'" '
    BEGIN {
      srv_re = "(^|[[:space:]{,])server:[[:space:]]*[\"" sq "]?[^\"" sq ", }]+"
      port_re = "(^|[[:space:]{,])port:[[:space:]]*[\"" sq "]?[0-9]+"
    }
    /^[A-Za-z][^:]*:/ { inp = ($0 ~ /^proxies:/); next }
    inp {
      line = $0
      while (match(line, srv_re)) {
        tok = substr(line, RSTART, RLENGTH); sub(/.*server:[[:space:]]*/, "", tok); gsub("[\"" sq "]", "", tok)
        print "S " tok; line = substr(line, RSTART + RLENGTH)
      }
      line = $0
      while (match(line, port_re)) {
        tok = substr(line, RSTART, RLENGTH); sub(/.*port:[[:space:]]*/, "", tok); gsub("[\"" sq "]", "", tok)
        print "P " tok; line = substr(line, RSTART + RLENGTH)
      }
    }' "$1"
}

resolve_domain() {
  local d="$1" ip got=""
  [[ "$d" =~ ^[A-Za-z0-9.-]+$ ]] || { warn "跳过无法识别的 server: $d"; return 0; }
  if command -v dscacheutil >/dev/null 2>&1; then
    for ip in $(dscacheutil -q host -a name "$d" 2>/dev/null | awk '/^ip_address:/{print $2}'); do
      if is_ipv4 "$ip" && ! is_fakeip "$ip"; then echo "$ip"; got=1; fi
    done
  fi
  # 系统解析被 fake-ip 接管时，经 TUN 用 DoH 取真实 A 记录（apply 前 TUN 还通）
  if [ -z "$got" ]; then
    for ip in $(curl -4 -s --max-time 10 -H 'accept: application/dns-json' \
                "https://1.1.1.1/dns-query?name=${d}&type=A" 2>/dev/null \
                | grep -oE '"data": ?"[0-9.]+"' | grep -oE '[0-9]+(\.[0-9]+){3}'); do
      is_ipv4 "$ip" && echo "$ip"
    done
  fi
  return 0
}

collect_nodes() {
  local ips="" ports="" w
  if [ -n "${NODE_IPS:-}" ]; then
    [ -n "${NODE_PORTS:-}" ] || die "设了 NODE_IPS 也要设 NODE_PORTS"
    ips=$(csv_words "$NODE_IPS"); ports=$(csv_words "$NODE_PORTS")
  else
    local cfg="${CONFIG:-$(user_home)/Library/Application Support/io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml}"
    [ -f "$cfg" ] || die "找不到 Clash Verge 运行配置：${cfg}（可用 CONFIG= 指定，或直接给 NODE_IPS/NODE_PORTS）"
    local kind val
    while read -r kind val; do
      case "$kind" in
        S) if is_ipv4 "$val"; then ips="$ips $val"
           elif [[ "$val" == *:* ]]; then warn "跳过 IPv6 节点 ${val}（本路线只走 IPv4）"
           else ips="$ips $(resolve_domain "$val" | tr '\n' ' ')"; fi ;;
        P) ports="$ports $val" ;;
      esac
    done < <(extract_endpoints "$cfg")
  fi
  for w in $ips; do is_ipv4 "$w" || die "节点地址不是 IPv4：$w"; is_fakeip "$w" && die "节点地址是 fake-ip：$w"; done
  for w in $ports; do is_port "$w" || die "节点端口无效：$w"; done
  NODE_IP_LIST=$(uniq_words $ips)
  NODE_PORT_LIST=$(uniq_words $ports)
  [ -n "$NODE_IP_LIST" ] || die "没解析出任何节点 IPv4（节点在 proxy-providers 里时用 NODE_IPS/NODE_PORTS 指定）"
  [ -n "$NODE_PORT_LIST" ] || die "没找到节点端口"
}

collect_nics() {
  local nics="" n
  if [ -n "${NICS:-}" ]; then
    nics=$(csv_words "$NICS")
  else
    nics=$(networksetup -listallhardwareports 2>/dev/null | awk '/^Device:/{print $2}' || true)
    n=$(route -n get default 2>/dev/null | awk '/interface:/{print $2}' || true)
    case "$n" in utun*|lo*|"") ;; *) nics="$nics $n" ;; esac
  fi
  for n in $nics; do is_nic "$n" || die "网卡名无效：$n"; done
  NIC_LIST=$(uniq_words $nics)
  [ -n "$NIC_LIST" ] || die "没找到物理网卡（可用 NICS=en0 指定）"
}

collect_extras() {
  local w
  DNS_LIST=""; LAN_LIST=""
  for w in $(csv_words "${BOOTSTRAP_DNS:-}"); do is_ipv4 "$w" || die "BOOTSTRAP_DNS 不是 IPv4：$w"; done
  for w in $(csv_words "${LAN_NET:-}"); do is_cidr4 "$w" || die "LAN_NET 不是 IPv4 网段：$w"; done
  DNS_LIST=$(uniq_words $(csv_words "${BOOTSTRAP_DNS:-}"))
  LAN_LIST=$(uniq_words $(csv_words "${LAN_NET:-}"))
}

render_rules() {
  collect_nodes; collect_nics; collect_extras
  echo "# Claude-Guardian PF killswitch，生成于 $(date -u '+%FT%TZ')"
  echo "cg_nics = \"{ $NIC_LIST }\""
  echo "cg_node_ports = \"{ $NODE_PORT_LIST }\""
  echo "table <cg_nodes> const { $NODE_IP_LIST }"
  [ -n "$DNS_LIST" ] && echo "table <cg_dns> const { $DNS_LIST }"
  [ -n "$LAN_LIST" ] && echo "table <cg_lan> const { $LAN_LIST }"
  echo 'pass out quick on $cg_nics inet proto udp from any port 68 to any port 67 keep state'
  echo 'pass out quick on $cg_nics inet proto { tcp udp } to <cg_nodes> port $cg_node_ports keep state'
  [ -n "$DNS_LIST" ] && echo 'pass out quick on $cg_nics inet proto { tcp udp } to <cg_dns> port 53 keep state'
  [ -n "$LAN_LIST" ] && echo 'pass out quick on $cg_nics inet to <cg_lan> keep state'
  echo 'block drop out log quick on $cg_nics all'
}

ip_class() {
  local ip="$1" a b
  is_ipv4 "$ip" || { echo "IPv6 地址"; return 0; }
  a=${ip%%.*}; b=${ip#*.}; b=${b%%.*}
  if [ "$a" -eq 10 ] || { [ "$a" -eq 172 ] && [ "$b" -ge 16 ] && [ "$b" -le 31 ]; } \
     || { [ "$a" -eq 192 ] && [ "$b" -eq 168 ]; }; then echo "局域网地址"
  elif [ "$a" -eq 100 ] && [ "$b" -ge 64 ] && [ "$b" -le 127 ]; then echo "运营商内网地址"
  elif [ "$a" -eq 198 ] && { [ "$b" -eq 18 ] || [ "$b" -eq 19 ]; }; then echo "fake-ip 地址"
  elif [ "$a" -eq 127 ]; then echo "本机回环"
  else echo "公网地址"; fi
}

# 2026-11-02 真机验收 R3：换网后域名解析失败，IP 和显式代理正常。macOS 不会把发往局域网的 DNS
# 劫持进 TUN（Mihomo 文档），DHCP 下发的路由器 DNS 走物理网卡，被本规则丢弃。这里只读检查，不改设置。
do_dns() {
  need_mac
  local svc out ns ifc cls warned=0 allowed=""
  [ -f "$RULES_PENDING" ] && allowed=$(sed -n 's/^table <cg_dns> const { \(.*\) }$/\1/p' "$RULES_PENDING")
  [ -z "$allowed" ] && [ -f "$RULES_CONFIRMED" ] && allowed=$(sed -n 's/^table <cg_dns> const { \(.*\) }$/\1/p' "$RULES_CONFIRMED")
  allowed="$allowed $(csv_words "${BOOTSTRAP_DNS:-}")"
  echo "== 各网络服务的 DNS 设置 =="
  while IFS= read -r svc; do
    svc="${svc#\*}"
    [ -n "$svc" ] || continue
    out=$(networksetup -getdnsservers "$svc" 2>/dev/null || true)
    if echo "$out" | grep -qi "aren't any"; then
      echo "WARN: ${svc}：自动（DHCP 下发）。换网后会用新网络下发的 DNS，常见是路由器地址，会被拦"
      warned=1
    else
      cls=""
      for ns in $out; do
        { is_ipv4 "$ns" || [[ "$ns" == *:* ]]; } && cls="$cls $(ip_class "$ns")"
      done
      echo "  ${svc}：手动（$(uniq_words $cls)）"
    fi
  done < <(networksetup -listallnetworkservices 2>/dev/null | tail -n +2)
  echo "== 当前生效的 DNS 走哪张网卡 =="
  for ns in $(scutil --dns 2>/dev/null | awk '/nameserver\[[0-9]+\]/{print $3}' | sort -u); do
    cls=$(ip_class "$ns")
    if ! is_ipv4 "$ns"; then
      echo "WARN: 有一个 IPv6 DNS：走物理网卡会被拦（本路线只走 IPv4），关掉网卡 IPv6 后会消失"; warned=1; continue
    fi
    ifc=$(route -n get "$ns" 2>/dev/null | awk '/interface:/{print $2}' || true)
    case "$ifc" in
      utun*|lo*) echo "  一个$cls 走 ${ifc}：会进 TUN，正常" ;;
      *) echo "WARN: 一个$cls 走 ${ifc:-未知网卡}：不进 TUN。加了 PF 会解析失败；放进 LAN_NET 能解析，但查询绕过代理（DNS 泄漏）"; warned=1 ;;
    esac
    case " $allowed " in *" $ns "*)
      echo "WARN: 这个$cls 也在 BOOTSTRAP_DNS 里：核心停掉后系统 DNS 查询能直接发出去（DNS 泄漏），系统 DNS 换一个不在 BOOTSTRAP_DNS 里的公网地址"; warned=1 ;;
    esac
  done
  if [ "$warned" -eq 1 ]; then
    echo "改法（B 档）：每个网络服务都把 DNS 设成手动的公网 IPv4，查询会进 TUN 被核心接管："
    echo "  sudo networksetup -setdnsservers \"<服务名>\" 1.1.1.1"
    echo "  恢复自动：sudo networksetup -setdnsservers \"<服务名>\" empty"
  fi
  return 0
}

# 汇总 tcpdump -n -q -e -i pflog0 的输出：只留网卡、目的地类别、协议、端口，不留 IP
summarize_blocked() {
  awk '
    function cls(ip,  a) {
      split(ip, a, ".")
      if (a[1] == 10 || (a[1] == 172 && a[2] >= 16 && a[2] <= 31) || (a[1] == 192 && a[2] == 168)) return "局域网"
      if (a[1] == 100 && a[2] >= 64 && a[2] <= 127) return "运营商内网"
      if (a[1] == 169 && a[2] == 254) return "链路本地"
      if (a[1] >= 224 || ip == "255.255.255.255") return "组播/广播"
      if (a[1] == 198 && (a[2] == 18 || a[2] == 19)) return "fake-ip段"
      return "公网"
    }
    {
      nic = "?"
      if (match($0, / on [a-z]+[0-9]+:/)) nic = substr($0, RSTART + 4, RLENGTH - 5)
      if ($0 ~ /IP6 /) { n[nic " IPv6"]++; total++; next }
      if (!match($0, /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)? > [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?:/)) next
      pair = substr($0, RSTART, RLENGTH - 1); rest = substr($0, RSTART + RLENGTH)
      split(pair, ends, " > "); m = split(ends[2], o, ".")
      ip = o[1] "." o[2] "." o[3] "." o[4]; port = (m == 5) ? o[5] : "-"
      proto = (rest ~ /tcp/) ? "TCP" : (rest ~ /UDP|udp/) ? "UDP" : (rest ~ /ICMP/) ? "ICMP" : "其他"
      n[nic " " cls(ip) " " proto "/" port]++; total++
    }
    END {
      printf "共 %d 个被拦的包\n", total
      for (k in n) printf "%6d  %s\n", n[k], k
    }' | { IFS= read -r head; echo "$head"; sort -rn; }
  cat <<'EOF'
怎么读：
  局域网 UDP/53、TCP/53      系统 DNS 指向局域网，见 dns 命令
  公网 UDP/53、TCP/53        多半是核心自己的上游 DNS（nameserver 等），或有程序绕过系统 DNS 直连
  组播/广播、链路本地、IPv6    mDNS、AirDrop、局域网发现等，被拦一般无害
  公网 UDP/3478、19302 等     STUN 直连：有程序的 UDP 没进 TUN
  公网 TCP/443 等             有连接没进 TUN（看是哪个程序：TUN 是否开着、程序是否绑了物理网卡）
  运营商内网、局域网其他端口    局域网设备访问；需要时用 LAN_NET 放行
EOF
}

do_blocked() {
  need_root blocked; need_mac
  local secs="${1:-60}" raw pid
  { [[ "$secs" =~ ^[0-9]+$ ]] && [ "$secs" -ge 5 ] && [ "$secs" -le 600 ]; } || die "秒数要在 5 到 600 之间"
  pfctl -a "$ANCHOR" -sr 2>/dev/null | grep -q 'block drop out log' \
    || die "当前规则不带日志（没加载，或是旧版脚本加载的），先用本脚本重新 apply"
  ifconfig pflog0 >/dev/null 2>&1 || ifconfig pflog0 create || die "建不了 pflog0"
  raw=$(mktemp)
  tcpdump -n -q -l -e -i pflog0 > "$raw" 2>/dev/null &
  pid=$!
  echo "抓 ${secs} 秒被拦的包；这段时间请正常使用，或者复现问题（比如换网、访问打不开的网站）……"
  sleep "$secs"
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  summarize_blocked < "$raw"
  rm -f "$raw"
}

main_ruleset_ready() { pfctl -sr 2>/dev/null | grep -q 'anchor "com.apple/\*"'; }

ensure_main_ruleset() {
  main_ruleset_ready && return 0
  # 系统默认规则集没加载时只加载系统自己的 /etc/pf.conf，不修改它
  pfctl -f /etc/pf.conf 2>/dev/null || true
  main_ruleset_ready || die "主规则集里没有 anchor \"com.apple/*\"，/etc/pf.conf 可能被改过，停下来人工检查"
}

enable_pf() {
  [ -f "$TOKEN_FILE" ] && return 0
  local token
  token=$(pfctl -E 2>&1 | awk '/Token/{print $NF}')
  [ -n "$token" ] || die "pfctl -E 没返回令牌"
  echo "$token" > "$TOKEN_FILE"
}

runtime_rollback() {
  pfctl -a "$ANCHOR" -F rules 2>/dev/null || true
  pfctl -a "$ANCHOR" -F Tables 2>/dev/null || true
  if [ -f "$TOKEN_FILE" ]; then
    pfctl -X "$(cat "$TOKEN_FILE")" 2>/dev/null || true
    rm -f "$TOKEN_FILE"
  fi
  rm -f "$RULES_PENDING"
}

stop_fuse() {
  if [ -f "$FUSE_PID" ]; then
    kill "$(cat "$FUSE_PID")" 2>/dev/null || true
    rm -f "$FUSE_PID"
  fi
}

do_apply() {
  need_root apply; need_mac
  local tmp
  tmp=$(mktemp)
  render_rules > "$tmp"
  pfctl -n -a "$ANCHOR" -f "$tmp" || { rm -f "$tmp"; die "规则语法检查没过，未加载"; }
  do_dns
  mkdir -p "$STATE_DIR"; chmod 700 "$STATE_DIR"
  mv "$tmp" "$RULES_PENDING"; chmod 600 "$RULES_PENDING"
  ensure_main_ruleset
  stop_fuse
  rm -f "$CONFIRM_FLAG"
  pfctl -a "$ANCHOR" -f "$RULES_PENDING"
  enable_pf
  log_event APPLIED
  nohup /bin/bash "$SELF" _fuse >/dev/null 2>&1 &
  echo $! > "$FUSE_PID"
  echo "已加载：网卡 { $NIC_LIST }，节点 $(echo "$NODE_IP_LIST" | wc -w | tr -d ' ') 个，端口 { $NODE_PORT_LIST }"
  echo "${FUSE_SECONDS} 秒内验证正常后执行：sudo $0 confirm；否则自动撤销"
}

do_fuse() {
  local end=$((SECONDS + FUSE_SECONDS))
  while [ "$SECONDS" -lt "$end" ]; do
    sleep 5
    if [ -f "$CONFIRM_FLAG" ]; then log_event CONFIRMED; rm -f "$FUSE_PID"; exit 0; fi
  done
  [ -f "$CONFIRM_FLAG" ] && { log_event CONFIRMED; rm -f "$FUSE_PID"; exit 0; }
  runtime_rollback
  rm -f "$FUSE_PID"
  log_event ROLLED_BACK_BY_FUSE
}

do_confirm() {
  need_root confirm
  [ -f "$RULES_PENDING" ] || die "没有待确认的规则（保险丝可能已撤销，重新 apply）"
  touch "$CONFIRM_FLAG"
  sleep 6
  if tail -1 "$LOG" 2>/dev/null | grep -q '^CONFIRMED'; then
    mv "$RULES_PENDING" "$RULES_CONFIRMED"
    rm -f "$CONFIRM_FLAG"
    echo "已确认，保险丝已取消。$( [ -f "$PLIST" ] && echo '开机会加载这一版。' || echo '要开机自动加载再执行 persist。')"
  else
    rm -f "$CONFIRM_FLAG"
    die "保险丝没有响应确认（可能已撤销），看 status 后重新 apply"
  fi
}

do_rollback() {
  need_root rollback; need_mac
  stop_fuse
  runtime_rollback
  rm -f "$CONFIRM_FLAG"
  [ -d "$STATE_DIR" ] && log_event ROLLED_BACK_MANUAL
  echo "已撤销运行中的规则。$( [ -f "$PLIST" ] && echo '开机项还在，下次开机会重新加载已确认规则；彻底停用用 uninstall。')"
}

do_persist() {
  need_root persist; need_mac
  [ -f "$RULES_CONFIRMED" ] || die "还没有已确认的规则，先 apply 再 confirm"
  install -m 755 "$SELF" "$INSTALLED_SCRIPT"
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$INSTALLED_SCRIPT</string><string>boot</string></array>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>/var/log/claude-guardian-pf.log</string>
  <key>StandardErrorPath</key><string>/var/log/claude-guardian-pf.log</string>
</dict>
</plist>
EOF
  chown root:wheel "$PLIST"; chmod 644 "$PLIST"
  launchctl bootout system "$PLIST" 2>/dev/null || true
  launchctl bootstrap system "$PLIST"
  log_event PERSISTED
  echo "已安装开机项 $PLIST"
}

do_unpersist() {
  need_root unpersist
  if [ -f "$PLIST" ]; then
    launchctl bootout system "$PLIST" 2>/dev/null || true
    rm -f "$PLIST"
  fi
  rm -f "$INSTALLED_SCRIPT"
  [ -d "$STATE_DIR" ] && log_event UNPERSISTED
  echo "已移除开机项"
}

do_boot() {
  local i
  for i in $(seq 1 30); do main_ruleset_ready && break; sleep 2; done
  ensure_main_ruleset
  [ -f "$RULES_CONFIRMED" ] || exit 0
  pfctl -a "$ANCHOR" -f "$RULES_CONFIRMED"
  enable_pf
  log_event BOOT_LOADED
}

do_status() {
  need_root status; need_mac
  echo "== PF =="; pfctl -s info 2>/dev/null | head -1 || true
  echo "== 主规则集挂载 com.apple/* =="; main_ruleset_ready && echo "是" || echo "否"
  echo "== 本 anchor 规则与命中计数 =="; pfctl -a "$ANCHOR" -vsr 2>/dev/null || true
  echo "== 节点表 =="; pfctl -a "$ANCHOR" -t cg_nodes -T show 2>/dev/null || echo "(无)"
  echo "== 文件 =="
  for f in "$RULES_CONFIRMED" "$RULES_PENDING" "$TOKEN_FILE" "$PLIST"; do
    [ -e "$f" ] && echo "有   $f" || echo "没有 $f"
  done
  echo "== 网卡覆盖 =="
  local rules covered n
  rules="$RULES_PENDING"; [ -f "$rules" ] || rules="$RULES_CONFIRMED"
  covered=$( [ -f "$rules" ] && sed -n 's/^cg_nics = "{ \(.*\) }"$/\1/p' "$rules" || true)
  echo "规则覆盖：{ ${covered:-无} }"
  for n in $(ifconfig -l); do
    case "$n" in lo*|utun*) continue ;; esac
    ifconfig "$n" 2>/dev/null | grep -q 'inet ' || continue
    case " $covered " in *" $n "*) ;; *) echo "WARN: $n 有 IPv4 地址但不在规则里，经它出去的流量不受保护，重新 apply" ;; esac
  done
  do_dns
  echo "== 最近事件 =="; tail -5 "$LOG" 2>/dev/null || echo "(无)"
}

do_uninstall() {
  need_root uninstall; need_mac
  do_rollback
  do_unpersist
  rm -rf "$STATE_DIR"
  echo "已卸载"
}

case "${1:-}" in
  render)    render_rules ;;
  apply)     do_apply ;;
  confirm)   do_confirm ;;
  status)    do_status ;;
  rollback)  do_rollback ;;
  persist)   do_persist ;;
  unpersist) do_unpersist ;;
  uninstall) do_uninstall ;;
  boot)      do_boot ;;
  dns)       do_dns ;;
  blocked)   do_blocked "${2:-60}" ;;
  _fuse)     do_fuse ;;
  _summarize) summarize_blocked ;;
  _class)    ip_class "${2:-}" ;;
  *) die "用法: $0 render|apply|confirm|status|dns|blocked [秒数]|rollback|persist|unpersist|uninstall" ;;
esac
