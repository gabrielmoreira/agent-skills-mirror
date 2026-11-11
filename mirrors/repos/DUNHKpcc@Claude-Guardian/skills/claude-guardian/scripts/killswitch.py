"""Portable Kill Switch controller; only operates an explicitly configured local deployment."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
PF = ASSETS / 'mac-killswitch/guardian-pf-killswitch.sh'
LINUX = ASSETS / 'vm-killswitch/install-flclash-killswitch.sh'
WINDOWS = ASSETS / 'killswitch/windows-switch.ps1'
UNITS = ['flclash-killswitch.service', 'flclash-killswitch-refresh.timer']
FUSE = 'guardian-switch-fuse'
BACKENDS = {'Darwin': 'mac_pf', 'Linux': 'linux_flclash', 'Windows': 'windows_firewall'}


class SwitchError(Exception):
    pass


def load_config(path):
    cfg = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    required = {'version', 'target', 'backend', 'protected_processes', 'mac', 'windows'}
    if not isinstance(cfg, dict) or set(cfg) != required or cfg['version'] != 1:
        raise SwitchError('配置格式不正确，请从随包模板重新填写。')
    if cfg['backend'] != BACKENDS.get(platform.system()) or cfg['target'] != platform.node():
        raise SwitchError('配置与当前设备或系统不匹配，请让 Agent 核对目标设备。')
    names = cfg['protected_processes']
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or not n.strip() or '\n' in n for n in names):
        raise SwitchError('请填写需要退出的应用与后台进程名称。')
    if not isinstance(cfg['mac'], dict) or set(cfg['mac']) - {'CONFIG', 'NODE_IPS', 'NODE_PORTS', 'NICS', 'BOOTSTRAP_DNS', 'LAN_NET'}:
        raise SwitchError('Mac 配置包含不支持的参数。')
    if any(not isinstance(v, str) or '\n' in v or '\x00' in v for v in cfg['mac'].values()):
        raise SwitchError('Mac 参数必须是单行文本。')
    if cfg['backend'] == 'mac_pf' and not (cfg['mac'].get('CONFIG') or (cfg['mac'].get('NODE_IPS') and cfg['mac'].get('NODE_PORTS'))):
        raise SwitchError('请填写代理配置绝对路径或节点 IPv4 与端口。')
    if cfg['mac'].get('CONFIG') and not Path(cfg['mac']['CONFIG']).is_absolute():
        raise SwitchError('代理配置路径必须是绝对路径。')
    win = cfg['windows']
    if not isinstance(win, dict) or set(win) - {'enable_rules', 'disable_rules', 'state_path', 'mode'} or not {'enable_rules', 'disable_rules', 'state_path'} <= set(win):
        raise SwitchError('Windows 配置格式不正确。')
    if win.get('mode', 'application_paths') not in ('application_paths', 'whole_machine'):
        raise SwitchError('Windows 模式须为 application_paths 或 whole_machine。')
    for key in ('enable_rules', 'disable_rules'):
        if not isinstance(win[key], list) or any(not isinstance(n, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+', n) for n in win[key]):
            raise SwitchError('Windows 规则须使用精确 Name，不使用显示名称或通配符。')
    all_names = win['enable_rules'] + win['disable_rules']
    if len(set(all_names)) != len(all_names) or not isinstance(win['state_path'], str):
        raise SwitchError('Windows 规则名称重复或状态路径无效。')
    if cfg['backend'] == 'windows_firewall' and (not win['enable_rules'] or not Path(win['state_path']).is_absolute()):
        raise SwitchError('请填写已部署的规则 Name 和备份绝对路径。')
    return cfg


def run(argv, *, env=None, allowed=(0,), timeout=30):
    try:
        proc = subprocess.run([str(x) for x in argv], capture_output=True, text=True, encoding='utf-8', errors='replace',
                              env=env, timeout=timeout)
    except FileNotFoundError:
        raise SwitchError('缺少系统命令，请让 Agent 检查依赖。') from None
    except subprocess.TimeoutExpired:
        raise SwitchError('系统操作超时，状态尚未确认；开启保险丝会按原计划恢复。') from None
    if proc.returncode not in allowed:
        raise SwitchError('系统操作未完成（退出码 %s），请检查权限或部署状态。' % proc.returncode)
    return proc


def pf(cfg, action):
    env = dict(os.environ, **cfg['mac'], FUSE_SECONDS='180')
    return run(['/bin/bash', PF, action], env=env, timeout=90)


def windows(path, action):
    result = run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', WINDOWS,
                  '-Action', action, '-Config', Path(path).resolve()], timeout=60)
    data = json.loads(result.stdout.strip().lstrip('\ufeff'))
    data['message'] = ('请先保存 Windows 关闭保护时的恢复基线。' if 'Create a baseline' in data.get('message', '')
                       else '已读回三档生效策略及指定规则；出口与防泄漏结果请以场景验收为准。')
    return data


def status(cfg, path):
    backend = cfg['backend']
    if backend == 'windows_firewall':
        return windows(path, 'Status')
    if backend == 'mac_pf':
        info = run(['pfctl', '-s', 'info']).stdout
        rules = run(['pfctl', '-a', 'com.apple/claude-guardian', '-sr']).stdout
        main = run(['pfctl', '-sr']).stdout
        protected = 'Status: Enabled' in info and 'com.apple/*' in main and 'block drop out log' in rules
        installed = Path('/Library/LaunchDaemons/com.claude-guardian.pf-killswitch.plist').is_file()
        loaded = run(['launchctl', 'print', 'system/com.claude-guardian.pf-killswitch'], allowed=(0, 113)).returncode == 0
        startup = True if installed and loaded else (None if installed or loaded else False)
        partial = (bool(rules) and not protected) or '不在规则里' in pf(cfg, 'status').stdout
    else:
        tables = json.loads(run(['nft', '-j', 'list', 'tables']).stdout)['nftables']
        exists = any(t.get('table', {}).get('name') == 'flclash_killswitch' and t['table']['family'] == 'inet' for t in tables)
        protected = False
        if exists:
            table = json.loads(run(['nft', '-j', 'list', 'table', 'inet', 'flclash_killswitch']).stdout)['nftables']
            protected = any(x.get('chain', {}).get('hook') == 'output' and x['chain'].get('policy') == 'drop' for x in table)
        enabled = [run(['systemctl', 'is-enabled', u], allowed=(0, 1)).stdout.strip() == 'enabled' for u in UNITS]
        startup = all(enabled)
        partial = (exists and not protected) or any(enabled) != all(enabled)
    return {'protection': 'unknown' if partial else ('on' if protected else 'off'),
            'startup': startup, 'checked_at': int(time.time()),
            'message': '已读回系统规则；出口与防泄漏结果请以场景验收为准。'}


def require_admin():
    if os.name == 'nt':
        import ctypes
        admin = ctypes.windll.shell32.IsUserAnAdmin()
    else:
        admin = os.geteuid() == 0
    if not admin:
        raise SwitchError('需要管理员权限。请从桌面界面打开操作终端，或使用 sudo／管理员终端。')


def confirm(action, cfg):
    if not sys.stdin.isatty():
        raise SwitchError('请在本机终端亲自确认；不接受管道或自动确认参数。')
    effects = {'on': '开启防直连。代理不可用时外网会被阻断；180 秒未确认将恢复。',
               'off': '停用当前保护及开机加载，可能恢复直连。请先退出相关应用及后台进程。',
               'uninstall': '恢复未保护状态并移除已部署的防护组件；配置模板与桌面入口保留。',
               'snapshot': '保存当前 Windows 策略及指定规则状态，作为关闭时的恢复基线。'}
    if cfg['backend'] == 'windows_firewall' and cfg['windows'].get('mode') == 'whole_machine':
        print('整机出口模式：影响所有软件。代理停用时其他软件也可能断网；国内直连、局域网、虚拟机和远程连接须先审核例外。关闭保护会恢复原有出站策略。', flush=True)
    phrase = action.upper() + ' ' + cfg['target']
    print(effects[action] + '\n目标设备：' + cfg['target'] + '\n输入 ' + phrase + ' 继续，其他输入取消。', flush=True)
    if input('> ').strip() != phrase:
        raise SwitchError('已取消，未执行该操作。')


def require_apps_closed(cfg):
    if os.name == 'nt':
        text = run(['powershell.exe', '-NoProfile', '-Command',
                    '[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Process | Select-Object -ExpandProperty ProcessName']).stdout
        running = {n.casefold().removesuffix('.exe') for n in text.splitlines()}
        configured = {n.casefold().removesuffix('.exe') for n in cfg['protected_processes']}
    else:
        text = run(['ps', '-axo', 'comm=']).stdout
        running = {Path(n.strip()).name.casefold() for n in text.splitlines()}
        configured = {n.casefold() for n in cfg['protected_processes']}
    if running & configured:
        raise SwitchError('仍有配置中需要保护的应用或后台进程运行，请退出后重试。')


def linux_off():
    run(['systemctl', 'stop', FUSE + '.timer', FUSE + '.service'], allowed=(0, 5))
    run(['systemctl', 'disable', '--now', *UNITS])
    run(['systemctl', 'stop', 'flclash-killswitch-refresh.service'])
    tables = json.loads(run(['nft', '-j', 'list', 'tables']).stdout)['nftables']
    if any(t.get('table', {}).get('name') == 'flclash_killswitch' for t in tables):
        run(['nft', 'delete', 'table', 'inet', 'flclash_killswitch'])


def off(cfg, path):
    if cfg['backend'] == 'mac_pf':
        pf(cfg, 'unpersist')
        pf(cfg, 'rollback')
    elif cfg['backend'] == 'linux_flclash':
        linux_off()
    else:
        windows(path, 'Off')


def on(cfg, path):
    before = status(cfg, path)
    require_coverage(cfg, before)
    if before['protection'] == 'on' and before['startup']:
        return before
    if before['protection'] != 'off' or before['startup'] is not False:
        raise SwitchError('当前状态不完整，请先让 Agent 核对，或按恢复方案关闭后重新开启。')
    started = time.monotonic()
    try:
        if cfg['backend'] == 'mac_pf':
            pf(cfg, 'apply')
        elif cfg['backend'] == 'linux_flclash':
            if not Path('/etc/flclash-killswitch.nft').is_file():
                raise SwitchError('尚未部署 Linux 防护规则，请先按 Skill 完成首次部署。')
            # The existing service removes its table on stop; the fuse also disables boot loading.
            run(['systemd-run', '--collect', '--unit=' + FUSE, '--on-active=180s', '/usr/bin/systemctl',
                 'disable', '--now', *UNITS])
            run(['systemctl', 'start', UNITS[0]])
        else:
            windows(path, 'On')
        print('开关配置已临时开启。请核对当前应用覆盖、网络正常及出口符合预期；180 秒内输入 KEEP 保留，否则恢复。', flush=True)
        if input('> ').strip() != 'KEEP' or time.monotonic() - started >= 160:
            raise SwitchError('未在确认时间内保留，正在恢复未保护状态。')
        current = status(cfg, path)
        require_coverage(cfg, current)
        if current['protection'] != 'on' or current.get('coverage', {}).get('status') == 'fail':
            raise SwitchError('未读回有效保护，可能已触发保险丝。')
        if cfg['backend'] == 'mac_pf':
            pf(cfg, 'confirm')
            pf(cfg, 'persist')
        elif cfg['backend'] == 'linux_flclash':
            run(['systemctl', 'enable', '--now', *UNITS])
            run(['systemctl', 'stop', FUSE + '.timer'])
        else:
            windows(path, 'Confirm')
    except (Exception, KeyboardInterrupt):
        off(cfg, path)
        raise
    result = status(cfg, path)
    require_coverage(cfg, result)
    if result['protection'] != 'on' or not result['startup']:
        raise SwitchError('开启后的状态验证未通过，请按恢复入口检查。')
    return result


def require_coverage(cfg, state):
    coverage = state.get('coverage', {}).get('status')
    whole_machine = cfg['backend'] == 'windows_firewall' and cfg['windows'].get('mode') == 'whole_machine'
    if coverage == 'fail' or (whole_machine and coverage != 'pass'):
        raise SwitchError('防护配置未核实，请检查出站放行规则、代理路径和接口；不要据此恢复受保护业务。')


def execute(action, cfg, path):
    require_admin()
    if action == 'status':
        return status(cfg, path)
    confirm(action, cfg)
    if action == 'snapshot':
        if cfg['backend'] != 'windows_firewall':
            raise SwitchError('只有 Windows 使用策略快照；Mac/Linux 使用独立规则。')
        windows(path, 'Snapshot')
        return {'protection': 'unknown', 'startup': None, 'checked_at': int(time.time()), 'message': '恢复基线已保存。'}
    if action == 'on':
        return on(cfg, path)
    require_apps_closed(cfg)
    off(cfg, path)
    result = status(cfg, path)
    if result['protection'] != 'off' or result['startup'] is not False:
        raise SwitchError('仍有保护或开机加载残留，请让 Agent 核对。')
    if action == 'uninstall':
        if cfg['backend'] == 'mac_pf':
            pf(cfg, 'uninstall')
        elif cfg['backend'] == 'linux_flclash':
            run(['/bin/bash', LINUX, 'uninstall'])
        else:
            windows(path, 'Uninstall')
    return result


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Guardian Switch — 本机防直连开关')
    parser.add_argument('action', choices=['status', 'on', 'off', 'uninstall', 'snapshot', 'gui', 'desktop'])
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output', type=Path, help='桌面入口生成目录；必须不存在')
    parser.add_argument('--receipt', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    result, code = {}, 0
    try:
        cfg = load_config(args.config)
        if args.action in {'gui', 'desktop'}:
            from killswitch_ui import serve, desktop
            if args.action == 'gui':
                serve(args.config.resolve(), cfg)
            else:
                if args.output is None:
                    raise SwitchError('请用 --output 指定新的桌面入口目录。')
                desktop(args.config.resolve(), args.output.resolve())
                print('桌面入口已生成。请保持程序目录与配置文件位置不变。')
            return 0
        result = execute(args.action, cfg, args.config)
    except (SwitchError, OSError, ValueError, EOFError, KeyboardInterrupt) as error:
        code = 1
        result = {'protection': 'unknown', 'startup': None, 'checked_at': int(time.time()),
                  'message': str(error) if isinstance(error, SwitchError) else '操作中断或配置不可读，请检查后重试。'}
    print(json.dumps(result, ensure_ascii=False))
    if args.receipt:
        with args.receipt.open('x', encoding='utf-8') as out:
            json.dump(dict(result, exit_code=code), out, ensure_ascii=False)
    return code


if __name__ == '__main__':
    sys.exit(main())
