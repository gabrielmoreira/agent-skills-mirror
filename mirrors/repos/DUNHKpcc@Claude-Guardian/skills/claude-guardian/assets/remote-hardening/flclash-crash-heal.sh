#!/usr/bin/env bash
# FlClash 崩溃自愈：路由黑洞清理 + core 看门狗。killswitch 场景特有，适用于任何 Linux 上的 FlClash TUN + fail-closed 防火墙。
# 脱敏版（2026-10-24）：由所有者的脚本整理，逻辑不变；用户名、UID、GUI 环境改为参数，并加 install/uninstall 生成 systemd 单元。
# 背景: FlClashCore 死后 TUN 消失，但 FlClash 写入的 ip rule 和策略路由表(如 2022)残留，公网被黑洞，
#       反向隧道/任何重连都出不去。本脚本只在 TUN 不存在时清残留；TUN 在或 core 活着时绝不碰路由。
# 子命令:
#   routes      清残留策略路由（TUN 不存在时）
#   watchdog    core 和 TUN 都没了且持续 DEAD_AFTER 秒，拉起 FlClash GUI（GUI 会重建 TUN 和路由）
#   install     写入看门狗 service+timer；若存在反向隧道 unit，给它加 ExecStartPre 清路由的 drop-in
#   uninstall   移除上述单元
# 环境变量: GUI_USER(默认 sudo 用户)、TUN_DEV(默认 FlClash)、FLCLASH_BIN(默认 /opt/FlClash/FlClash)、
#           TUNNEL_UNIT_NAME(默认 guardian-reverse-tunnel.service)、DEAD_AFTER(默认 90)、
#           WAYLAND_DISPLAY_NAME(默认 wayland-1)、X_DISPLAY(默认 :0)
set -u
TUN_DEV="${TUN_DEV:-FlClash}"
GUI_USER="${GUI_USER:-${SUDO_USER:-}}"
FLCLASH_BIN="${FLCLASH_BIN:-/opt/FlClash/FlClash}"
TUNNEL_UNIT_NAME="${TUNNEL_UNIT_NAME:-guardian-reverse-tunnel.service}"
DEAD_AFTER="${DEAD_AFTER:-90}"
X_DISPLAY="${X_DISPLAY:-:0}"
WAYLAND_DISPLAY_NAME="${WAYLAND_DISPLAY_NAME:-wayland-1}"
LOG="/var/log/flclash-route-cleanup.log"
DEAD_SINCE="/run/flclash-core-dead.since"
SELF="$(readlink -f "$0")"
INSTALLED="/usr/local/sbin/flclash-crash-heal.sh"
log() { echo "$(date '+%F %T') $*" >> "$LOG" 2>/dev/null; }
die() { echo "ERROR: $*" >&2; exit 1; }

tun_exists() { ip link show "$TUN_DEV" >/dev/null 2>&1; }

clean_routes() {
  tun_exists && return 0
  local t
  for t in $(ip rule show | grep -oE 'lookup [0-9]+' | awk '{print $2}' | sort -u); do
    if ip route show table "$t" 2>/dev/null | grep -q "dev $TUN_DEV"; then
      while ip rule del table "$t" 2>/dev/null; do :; done
      ip route flush table "$t" 2>/dev/null
      log "cleaned stale table $t (TUN absent)"
    fi
  done
  return 0
}

watchdog() {
  [ -n "$GUI_USER" ] || { log "GUI_USER 未设置，看门狗不动作"; return 0; }
  if tun_exists || pgrep -x FlClashCore >/dev/null; then
    rm -f "$DEAD_SINCE"
    return 0
  fi
  if [ ! -f "$DEAD_SINCE" ]; then
    date +%s > "$DEAD_SINCE"
    log "core/TUN down, watch started"
    return 0
  fi
  local dead_for=$(( $(date +%s) - $(cat "$DEAD_SINCE") ))
  [ "$dead_for" -lt "$DEAD_AFTER" ] && return 0

  rm -f "$DEAD_SINCE"
  if pgrep -x FlClash >/dev/null; then
    log "core dead ${dead_for}s, restarting GUI"
    pkill -x FlClash
    sleep 2
  else
    log "GUI+core both dead ${dead_for}s, launching GUI"
  fi
  local uid; uid=$(id -u "$GUI_USER")
  runuser -u "$GUI_USER" -- env DISPLAY="$X_DISPLAY" WAYLAND_DISPLAY="$WAYLAND_DISPLAY_NAME" \
    XDG_RUNTIME_DIR="/run/user/$uid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    nohup "$FLCLASH_BIN" >/dev/null 2>&1 &
  log "GUI relaunched"
}

do_install() {
  [ "$(id -u)" -eq 0 ] || die "需要 root（sudo）"
  [ -n "$GUI_USER" ] || die "请设置 GUI_USER（登录桌面的用户）"
  local uid; uid=$(id -u "$GUI_USER") || die "找不到用户 $GUI_USER"
  install -Dm755 "$SELF" "$INSTALLED"

  # KillMode=process: oneshot 默认 control-group 会在脚本退出时杀掉它后台拉起的 GUI
  # 服务级 Environment 要写全：systemd 环境里没有桌面会话变量
  cat > /etc/systemd/system/flclash-core-watchdog.service <<UNIT_EOF
[Unit]
Description=FlClash core watchdog

[Service]
Type=oneshot
KillMode=process
Environment=GUI_USER=$GUI_USER
Environment=TUN_DEV=$TUN_DEV
Environment=FLCLASH_BIN=$FLCLASH_BIN
Environment=DEAD_AFTER=$DEAD_AFTER
Environment=DISPLAY=$X_DISPLAY
Environment=WAYLAND_DISPLAY=$WAYLAND_DISPLAY_NAME
Environment=XDG_RUNTIME_DIR=/run/user/$uid
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$uid/bus
ExecStart=$INSTALLED watchdog
UNIT_EOF
  cat > /etc/systemd/system/flclash-core-watchdog.timer <<'UNIT_EOF'
[Unit]
Description=Check FlClash core every 30s

[Timer]
OnBootSec=2min
OnUnitActiveSec=30s

[Install]
WantedBy=timers.target
UNIT_EOF
  if [ -f "/etc/systemd/system/$TUNNEL_UNIT_NAME" ]; then
    install -d "/etc/systemd/system/$TUNNEL_UNIT_NAME.d"
    # '+' 前缀: 以 root 运行，隧道服务本身是普通用户
    cat > "/etc/systemd/system/$TUNNEL_UNIT_NAME.d/clean-routes.conf" <<UNIT_EOF
[Service]
ExecStartPre=+$INSTALLED routes
UNIT_EOF
    echo "已给 $TUNNEL_UNIT_NAME 加 ExecStartPre 清路由 drop-in"
  else
    echo "未找到 $TUNNEL_UNIT_NAME，跳过隧道 drop-in（没有反向隧道时可以忽略）"
  fi
  systemctl daemon-reload
  systemctl enable --now flclash-core-watchdog.timer
  echo "installed: $(systemctl is-active flclash-core-watchdog.timer)"
}

do_uninstall() {
  [ "$(id -u)" -eq 0 ] || die "需要 root（sudo）"
  systemctl disable --now flclash-core-watchdog.timer 2>/dev/null || true
  rm -f /etc/systemd/system/flclash-core-watchdog.service /etc/systemd/system/flclash-core-watchdog.timer \
        "/etc/systemd/system/$TUNNEL_UNIT_NAME.d/clean-routes.conf" "$INSTALLED"
  rmdir "/etc/systemd/system/$TUNNEL_UNIT_NAME.d" 2>/dev/null || true
  systemctl daemon-reload
  echo "uninstalled"
}

case "${1:-all}" in
  routes)    clean_routes ;;
  watchdog)  watchdog ;;
  all)       clean_routes; watchdog ;;
  install)   do_install ;;
  uninstall) do_uninstall ;;
  *) echo "usage: $0 routes|watchdog|all|install|uninstall" >&2; exit 1 ;;
esac
