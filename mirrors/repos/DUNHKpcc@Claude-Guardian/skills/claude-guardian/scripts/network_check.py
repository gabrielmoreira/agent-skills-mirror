"""Basic network check: route, IPv4 exit, IPv6, DNS leak, UDP, optional failure drill.

Fills the gap left by ``guardian.py check`` (metadata only): this one actually tests the
network of the machine it runs on (macOS, Windows, Linux). Run it after the user approved
the check plan (B tier); it contacts only the fixed neutral endpoints in ``ENDPOINTS`` and
never Claude or Anthropic. Exit IPs stay in memory: the report shows country, ASN and
whether exits match. ``--evidence-output`` writes a private new file for
``egress_verifier.py``, which does contain the exit IP.

DNS leak: under a fake-ip TUN a lookup returns a synthetic address and no real resolver is
asked, so the check also opens a connection to each test name; that makes the proxy core
resolve it, and the test service sees which resolvers asked. A resolver in the user's home
country (``--home-country``, default CN) is a leak. bash.ws's own "may be leaking" text only
means the resolver ASN differs from the exit ASN, which is normal through a proxy, so it is
not used.
"""
import argparse
import http.client
import ipaddress
import json
import os
import platform as _platform
import re
import socket
import ssl
import subprocess
import sys
import time

import stun_probe

SCHEMA = 'guardian-network-check/0.1'
EVIDENCE_SCHEMA = 'guardian-egress-evidence/0.1'
REF = re.compile(r'[A-Za-z0-9._-]{1,64}\Z')
EXIT_HOST, EXIT_PATH = 'ipinfo.io', '/json'
V6_HOST, V6_PATH = 'api6.ipify.org', '/?format=json'
LEAK_HOST = 'bash.ws'
STUN_HOST, STUN_PORT = 'stun.cloudflare.com', 3478
ENDPOINTS = ('https://%s%s' % (EXIT_HOST, EXIT_PATH), 'https://%s%s' % (V6_HOST, V6_PATH),
             'https://%s/id , <n>.<id>.%s , https://%s/dnsleak/test/<id>' % (LEAK_HOST, LEAK_HOST, LEAK_HOST),
             'stun:%s:%d (UDP)' % (STUN_HOST, STUN_PORT))
FORBIDDEN = ('claude', 'anthropic')
MAX_BODY = 64 * 1024
LEAK_NAMES = 6
TUN_NAME = re.compile(r'(utun|tun|meta|mihomo|clash|flclash|sing|wintun|wireguard)', re.I)
STATUS_TEXT = {'pass': '通过', 'fail': '有问题', 'warn': '注意', 'not_run': '还没查', 'error': '没测成'}

assert not any(word in item.lower() for item in ENDPOINTS for word in FORBIDDEN)


class CheckError(Exception):
    pass


# -- transport ------------------------------------------------------------------
class _FamilyConnection(http.client.HTTPSConnection):
    """HTTPS over one address family, resolved by the OS (so a TUN/fake-ip path is used)."""

    def __init__(self, host, family, timeout):
        super().__init__(host, 443, timeout=timeout, context=ssl.create_default_context())
        self._family = family

    def connect(self):
        info = socket.getaddrinfo(self.host, self.port, self._family, socket.SOCK_STREAM)[0]
        sock = socket.socket(info[0], info[1], info[2])
        sock.settimeout(self.timeout)
        try:
            sock.connect(info[4])
            self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        except Exception:
            sock.close()
            raise


def https_get(host, path, family=socket.AF_INET, timeout=10, proxy=None):
    """GET over a forced family, or through an explicit local HTTP proxy; returns the body text."""
    if proxy:
        conn = http.client.HTTPSConnection(proxy[0], proxy[1], timeout=timeout, context=ssl.create_default_context())
        conn.set_tunnel(host, 443)
    else:
        conn = _FamilyConnection(host, family, timeout)
    try:
        conn.request('GET', path, headers={'User-Agent': 'curl/8', 'Accept': 'application/json'})
        response = conn.getresponse()
        body = response.read(MAX_BODY + 1)
        if response.status != 200 or len(body) > MAX_BODY:
            raise CheckError('http_%d' % response.status)
        return body.decode('utf-8', 'replace')
    finally:
        conn.close()


def _json(text):
    try:
        return json.loads(text)
    except ValueError:
        raise CheckError('bad_json') from None


def _run(command, timeout=10):
    done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, shell=False)
    return done.stdout if done.returncode == 0 else ''


# -- checks ---------------------------------------------------------------------
def parse_route(system, text):
    """Interface name of the route to an outside address from the platform's route command output."""
    if system == 'macos':
        match = re.search(r'interface:\s*(\S+)', text)
    elif system == 'linux':
        match = re.search(r'\bdev\s+(\S+)', text)
    else:
        match = re.search(r'^\s*(\S.*?)\s*$', text, re.M)
    return match.group(1) if match else None


def check_route(system):
    # Ask for the route to a real outside address on every platform: TUN usually adds more specific
    # routes and leaves the default route on the physical NIC (macOS 2026-11-02 acceptance).
    try:
        if system == 'macos':
            name = parse_route(system, _run(['/sbin/route', '-n', 'get', '1.1.1.1']))
        elif system == 'linux':
            name = parse_route(system, _run(['ip', 'route', 'get', '1.1.1.1']))
        else:
            script = ('$r = Find-NetRoute -RemoteIPAddress 1.1.1.1 | Select-Object -First 1; '
                      '$a = Get-NetAdapter -InterfaceIndex $r.InterfaceIndex; $a.InterfaceDescription')
            name = parse_route(system, _run(['powershell', '-NoProfile', '-Command', script], timeout=20))
    except (OSError, subprocess.SubprocessError):
        name = None
    if not name:
        return {'status': 'not_run', 'via_tun': 'unknown', 'interface': None}
    via = 'yes' if TUN_NAME.search(name) else 'no'
    return {'status': 'pass' if via == 'yes' else 'fail', 'via_tun': via, 'interface': name}


def check_exit_v4(home_country, proxy=None, timeout=10):
    try:
        data = _json(https_get(EXIT_HOST, EXIT_PATH, socket.AF_INET, timeout, proxy))
        address = ipaddress.ip_address(data.get('ip', ''))
    except (OSError, CheckError, ValueError, http.client.HTTPException):
        return {'status': 'error'}, None
    country = str(data.get('country', '')).lower() or None
    asn = str(data.get('org', ''))[:80] or None
    status = 'fail' if (address.version != 4 or (country and country == home_country)) else 'pass'
    return {'status': status, 'country': country, 'asn': asn, 'family': 'ipv%d' % address.version}, str(address)


def check_ipv6(timeout=8):
    """'unreachable' when there is no IPv6 path, or when the answer is an IPv4 address (proxied)."""
    try:
        data = _json(https_get(V6_HOST, V6_PATH, socket.AF_INET6, timeout))
        address = ipaddress.ip_address(data.get('ip', ''))
    except (OSError, CheckError, ValueError, http.client.HTTPException):
        return {'status': 'pass', 'probe': 'unreachable'}
    if address.version == 6:
        return {'status': 'fail', 'probe': 'reachable'}
    return {'status': 'pass', 'probe': 'unreachable'}


def judge_dns(rows, exit_country, home_country):
    """Pure judgement over the test service's rows (type ip / dns / conclusion)."""
    if not isinstance(rows, list):
        return {'status': 'not_run', 'servers': []}
    servers = []
    for row in rows:
        if isinstance(row, dict) and row.get('type') == 'dns':
            servers.append({'country': str(row.get('country', '')).lower() or None,
                            'asn': str(row.get('asn', ''))[:80] or None})
    if not servers:
        return {'status': 'not_run', 'servers': []}
    if any(item['country'] == home_country for item in servers):
        status = 'fail'
    elif exit_country and any(item['country'] != exit_country for item in servers):
        status = 'warn'
    else:
        status = 'pass'
    unique = []
    for item in servers:
        if item not in unique:
            unique.append(item)
    return {'status': status, 'servers': unique, 'count': len(servers)}


FAKE_IP = ipaddress.ip_network('198.18.0.0/15')


def check_fake_ip(host=EXIT_HOST):
    """'yes' when the system resolver answers from the fake-ip range: the proxy core took over DNS."""
    try:
        address = socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM)[0][4][0]
    except OSError:
        return 'unknown'
    return 'yes' if ipaddress.ip_address(address) in FAKE_IP else 'unknown'


def check_dns_leak(exit_country, home_country, timeout=10):
    try:
        test_id = https_get(LEAK_HOST, '/id', socket.AF_INET, timeout).strip()
        if not re.fullmatch(r'[a-z0-9]{8,40}', test_id):
            raise CheckError('bad_id')
        for index in range(1, LEAK_NAMES + 1):
            name = '%d.%s.%s' % (index, test_id, LEAK_HOST)
            try:
                socket.getaddrinfo(name, 80, socket.AF_INET, socket.SOCK_STREAM)
                socket.create_connection((name, 80), timeout=4).close()
            except OSError:
                pass
        time.sleep(2)
        rows = _json(https_get(LEAK_HOST, '/dnsleak/test/%s?json' % test_id, socket.AF_INET, timeout + 5))
    except (OSError, CheckError, http.client.HTTPException):
        return {'status': 'error', 'servers': []}
    return judge_dns(rows, exit_country, home_country)


def check_udp(exit_address, timeout=3.0):
    """STUN over UDP; the mapped address should be the same exit as TCP."""
    try:
        info = socket.getaddrinfo(STUN_HOST, STUN_PORT, socket.AF_INET, socket.SOCK_DGRAM)[0]
    except OSError:
        return {'status': 'error'}
    with socket.socket(info[0], socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        for _ in range(2):
            request = stun_probe.binding_request()
            try:
                sock.sendto(request, info[4])
                packet, _peer = sock.recvfrom(stun_probe.MAX_PACKET)
                mapped = stun_probe.parse_binding_response(packet, request[8:20])[0]
                break
            except socket.timeout:
                continue
            except (OSError, stun_probe.StunError):
                return {'status': 'error'}
        else:
            return {'status': 'warn', 'udp': 'blocked'}
    if exit_address is None:
        return {'status': 'not_run', 'udp': 'open'}
    same = ipaddress.ip_address(mapped) == ipaddress.ip_address(exit_address)
    return {'status': 'pass' if same else 'fail', 'udp': 'open', 'same_exit_as_tcp': same}


def failure_drill(home_country, console=None):
    """Interactive: the user stops the proxy core; nothing should get out; then restarts it."""
    stdin, stdout = console if console else (sys.stdin, sys.stdout)
    if not (stdin.isatty() and stdout.isatty()):
        return {'status': 'not_run', 'reason': 'needs_terminal'}
    stdout.write('\n故障演练：现在请退出代理客户端或停掉代理核心（TUN 会一起停），完成后按回车。')
    stdout.flush()
    stdin.readline()
    stopped, _ = check_exit_v4(home_country, timeout=6)
    stdout.write('现在请重新打开代理客户端，确认已连上后按回车。')
    stdout.flush()
    stdin.readline()
    restored, _ = check_exit_v4(home_country, timeout=10)
    if stopped['status'] == 'error' and restored['status'] != 'pass':
        result = 'inconclusive'  # also unreachable after restart: the network itself is down
    elif stopped['status'] == 'error':
        result = 'no_direct'
    elif stopped.get('country') == home_country:
        result = 'direct_observed'
    else:
        result = 'core_still_running'
    status = {'no_direct': 'pass', 'direct_observed': 'fail', 'core_still_running': 'not_run',
              'inconclusive': 'not_run'}[result]
    return {'status': status, 'result': result, 'restored': restored['status'] == 'pass'}


# -- report ---------------------------------------------------------------------
def system_name():
    name = _platform.system().lower()
    return {'darwin': 'macos', 'windows': 'windows', 'linux': 'linux'}.get(name)


def run(target_ref, home_country='cn', proxy=None, drill=False, console=None):
    system = system_name()
    if system is None:
        raise CheckError('unsupported_platform')
    results = {'route': check_route(system)}
    results['exit_ipv4'], exit_address = check_exit_v4(home_country)
    if proxy:
        proxied, proxied_address = check_exit_v4(home_country, proxy=proxy)
        if proxied['status'] != 'error' and exit_address:
            proxied['same_exit_as_direct'] = proxied_address == exit_address
            if not proxied['same_exit_as_direct']:
                proxied['status'] = 'fail'
        results['exit_via_proxy'] = proxied
    results['ipv6'] = check_ipv6()
    results['dns_leak'] = check_dns_leak(results['exit_ipv4'].get('country'), home_country)
    results['dns_leak']['fake_ip'] = check_fake_ip()
    results['udp'] = check_udp(exit_address)
    results['failure_drill'] = failure_drill(home_country, console) if drill else {'status': 'not_run'}
    results['webrtc'] = {'status': 'not_run'}
    overall = ('fail' if any(item['status'] == 'fail' for item in results.values()) else
               'pass' if all(results[k]['status'] == 'pass' for k in ('route', 'exit_ipv4', 'ipv6', 'dns_leak', 'udp'))
               else 'incomplete')
    report = {'schema_version': SCHEMA, 'platform': system, 'target_ref': target_ref,
              'home_country': home_country, 'checked_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
              'endpoints': list(ENDPOINTS), 'results': results, 'overall': overall}
    return report, (exit_address, proxied_address if proxy else None)


def evidence(report, addresses):
    """Partial evidence for egress_verifier.py; settings it cannot see stay unknown."""
    r = report['results']
    exit_address, proxied_address = addresses
    samples = [{'family': 'ipv4', 'exit': exit_address, 'process': 'terminal'}] if exit_address else []
    if proxied_address:  # programs that use the HTTP/mixed port (proxy variables), e.g. Claude Code
        samples.append({'family': 'ipv4', 'exit': proxied_address, 'process': 'other_app'})
    via = r['route']['via_tun']
    leak = {'pass': 'pass', 'fail': 'fail'}.get(r['dns_leak']['status'], 'not_run')
    drill = r['failure_drill'].get('result')
    return {'schema_version': EVIDENCE_SCHEMA, 'platform': report['platform'], 'target_ref': report['target_ref'],
            'tun': {'enabled': 'yes' if via == 'yes' else 'unknown', 'strict_route': 'unknown',
                    'default_route_via_tun': via},
            'core': {'ipv6': 'unknown'},
            'dns': {'ipv6': 'unknown', 'hijack': r['dns_leak'].get('fake_ip', 'unknown'), 'leak_test': leak},
            'rules': {'final_match': 'unknown', 'direct_exceptions': 'unknown'},
            'samples': samples,
            'ipv6_probe': r['ipv6'].get('probe', 'not_run'),
            'webrtc': 'not_run',
            'failure_drill': drill if drill in ('no_direct', 'direct_observed') else 'not_run',
            'firewall': 'unknown', 'os_ipv6': 'unknown'}


def describe(report):
    """[(key, label, status, detail)] in display order; shared by the summary and the dashboard."""
    r, rows = report['results'], []

    def add(key, label, detail):
        rows.append((key, label, r[key]['status'], detail))

    route = r['route']
    add('route', '去往外网的路由', ('走 TUN（%s）' % route['interface']) if route['via_tun'] == 'yes'
        else ('没走 TUN（%s）' % route['interface']) if route.get('interface') else '读不到')
    exit4 = r['exit_ipv4']
    add('exit_ipv4', 'IPv4 出口', '%s · %s' % ((exit4.get('country') or '?').upper(), exit4.get('asn') or '?')
        if exit4['status'] != 'error' else '连不上测试站点')
    if 'exit_via_proxy' in r:
        same = r['exit_via_proxy'].get('same_exit_as_direct')
        add('exit_via_proxy', '经本地代理端口的出口',
            '和直连出口一致' if same else '和直连出口不一致' if same is False else '没测成')
    add('ipv6', 'IPv6 是否堵住', '已堵住，只走 IPv4' if r['ipv6'].get('probe') == 'unreachable'
        else '没堵住：有 IPv6 出口，会绕过 IPv4 出口')
    dns = r['dns_leak']
    places = '、'.join(sorted({'%s %s' % ((s.get('country') or '?').upper(), s.get('asn') or '')
                               for s in dns.get('servers', [])}))
    detail = {'pass': '解析服务器：%s，没有国内解析' % places,
              'warn': '没有国内解析；解析服务器和出口不在同一地区：%s' % places,
              'fail': '有解析服务器在本国：%s' % places,
              'not_run': '测试站没收到解析请求，再跑一次', 'error': '连不上测试站点'}[dns['status']]
    if dns.get('fake_ip') == 'yes':
        detail += '；系统 DNS 已由代理核心接管（fake-ip）'
    add('dns_leak', 'DNS 泄露', detail)
    add('udp', 'UDP', {'pass': 'STUN 映射地址和 TCP 出口一致', 'fail': 'UDP 出口和 TCP 出口不一致',
                       'warn': 'UDP 不通（WebRTC、QUIC 用不了，但不会漏）', 'not_run': '没有 TCP 出口可比',
                       'error': '没测成'}[r['udp']['status']])
    drill = r['failure_drill']
    result = drill.get('result')
    add('failure_drill', '故障演练', {'pass': '停掉代理后连不出去，没有直连', 'fail': '停掉代理后直连出去了'}.get(
        drill['status'], '停掉后还能用代理出口，核心可能没停，再做一次' if result == 'core_still_running'
        else '重新打开代理后也连不上，先检查网络再做一次' if result == 'inconclusive'
        else '加 --failure-drill 在终端里按提示停一次代理核心'))
    add('webrtc', 'WebRTC', '运行 serve_webrtc.py，在浏览器里点一次')
    return rows


def summary(report):
    lines = ['网络基础检测（%s，%s）' % (report['target_ref'], report['platform'])]
    lines += ['[%s] %s：%s' % (STATUS_TEXT[status], label, detail) for _key, label, status, detail in describe(report)]
    lines.append('结论：%s' % {'pass': '这几项都通过', 'fail': '有问题，见上面标“有问题”的项',
                             'incomplete': '还有没查完的项'}[report['overall']])
    return '\n'.join(lines)


def _write_new(path, document):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(document, handle, ensure_ascii=False, indent=1)


def _proxy(value):
    match = re.fullmatch(r'(?:http://)?(127\.0\.0\.1|localhost|\[::1\]):(\d{1,5})/?', value or '')
    if not match or not 0 < int(match.group(2)) < 65536:
        raise argparse.ArgumentTypeError('只接受本机代理端口，例如 http://127.0.0.1:7897')
    return (match.group(1).strip('[]'), int(match.group(2)))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Basic network check (route, IPv4 exit, IPv6, DNS leak, UDP, '
                                                 'failure drill). Contacts only: ' + '; '.join(ENDPOINTS))
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('endpoints', help='list the endpoints a run contacts; no network')
    go = sub.add_parser('run', help='run the checks (after the user approved the plan)')
    go.add_argument('--target-ref', required=True)
    go.add_argument('--home-country', default='cn', help='two-letter code of the user\'s real country (default cn)')
    go.add_argument('--proxy', type=_proxy, help='also test through the local HTTP/mixed port, e.g. http://127.0.0.1:7897')
    go.add_argument('--failure-drill', action='store_true', help='interactive: stop the proxy core when asked')
    go.add_argument('--json', action='store_true', help='print the JSON report instead of the summary')
    go.add_argument('--output', help='save the JSON report (no IPs) to a NEW file')
    go.add_argument('--evidence-output', help='save egress_verifier evidence to a NEW private file (contains the exit IP)')
    args = parser.parse_args(argv)
    if args.command == 'endpoints':
        print('\n'.join(ENDPOINTS))
        return 0
    if not REF.match(args.target_ref) or not re.fullmatch(r'[a-z]{2}', args.home_country.lower()):
        parser.error('target-ref 用别名；home-country 用两位国家代码')
    try:
        report, addresses = run(args.target_ref, args.home_country.lower(), args.proxy, args.failure_drill)
        if args.output:
            _write_new(args.output, report)
        if args.evidence_output:
            _write_new(args.evidence_output, evidence(report, addresses))
    except (CheckError, OSError) as exc:
        print(json.dumps({'status': 'error', 'code': str(exc) or type(exc).__name__}), file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=1) if args.json else summary(report))
    return 1 if report['overall'] == 'fail' else 0


if __name__ == '__main__':
    sys.exit(main())
