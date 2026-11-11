"""Unprivileged, short-lived local UI and native desktop launchers for killswitch.py."""
import argparse
import base64
import json
import os
from pathlib import Path
import platform
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

ASSETS = Path(__file__).resolve().parent.parent / 'assets/killswitch'
CLI = Path(__file__).with_name('killswitch.py')
ACTIONS = {'status', 'on', 'off', 'uninstall'}


def ps_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def launch_terminal(action, config, receipt, directory):
    argv = [sys.executable, str(CLI), action, '--config', str(config), '--receipt', str(receipt)]
    system = platform.system()
    if system == 'Windows':
        command = '& ' + ' '.join(ps_quote(a) for a in argv) + '; Read-Host "Press Enter to close"'
        encoded = base64.b64encode(command.encode('utf-16le')).decode()
        outer = "Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoProfile -NoExit -EncodedCommand " + encoded + "'"
        return subprocess.Popen(['powershell.exe', '-NoProfile', '-Command', outer])
    script = directory / ('action-' + secrets.token_hex(6) + '.command')
    script.write_text('#!/bin/sh\nsudo ' + shlex.join(argv) + '\nprintf "\\n按回车关闭窗口。"\nread answer\n', encoding='utf-8')
    script.chmod(0o700)
    if system == 'Darwin':
        return subprocess.Popen(['open', '-a', 'Terminal', str(script)])
    terminal = next((shutil.which(t) for t in ('x-terminal-emulator', 'gnome-terminal', 'konsole', 'xterm') if shutil.which(t)), None)
    if not terminal:
        raise RuntimeError('未找到终端，请从命令行运行开关。')
    separator = '--' if Path(terminal).name == 'gnome-terminal' else '-e'
    return subprocess.Popen([terminal, separator, '/bin/sh', str(script)])


def desktop(config, output):
    output.mkdir(parents=True, exist_ok=False)
    system = platform.system()
    argv = [sys.executable, str(CLI), 'gui', '--config', str(config)]
    if system == 'Darwin':
        import plistlib
        contents = output / 'Guardian Switch.app/Contents'
        (contents / 'MacOS').mkdir(parents=True)
        (contents / 'Resources').mkdir()
        launcher = contents / 'MacOS/guardian-switch'
        launcher.write_text('#!/bin/sh\nexec ' + shlex.join(argv) + '\n', encoding='utf-8')
        launcher.chmod(0o755)
        shutil.copyfile(ASSETS / 'icon.icns', contents / 'Resources/guardian.icns')
        with (contents / 'Info.plist').open('wb') as out:
            plistlib.dump({'CFBundleName': 'Guardian Switch', 'CFBundleDisplayName': 'Guardian Switch',
                          'CFBundleIdentifier': 'org.claude-guardian.switch', 'CFBundlePackageType': 'APPL',
                          'CFBundleExecutable': 'guardian-switch', 'CFBundleIconFile': 'guardian.icns'}, out)
    elif system == 'Windows':
        icon = output / 'guardian.ico'
        shutil.copyfile(ASSETS / 'icon.ico', icon)
        # A normal-user launcher; elevation is requested only for an explicit action.
        pythonw = Path(sys.executable).with_name('pythonw.exe')
        target = pythonw if pythonw.is_file() else Path(sys.executable)
        args = subprocess.list2cmdline(argv[1:])
        command = ('$s=(New-Object -ComObject WScript.Shell).CreateShortcut(' + ps_quote(output / 'Guardian Switch.lnk') + ');'
                   '$s.TargetPath=' + ps_quote(target) + ';$s.Arguments=' + ps_quote(args) + ';$s.IconLocation=' + ps_quote(icon) + ';$s.Save()')
        subprocess.run(['powershell.exe', '-NoProfile', '-Command', command], check=True, timeout=30)
    else:
        icon = output / 'guardian.png'
        shutil.copyfile(ASSETS / 'icon.png', icon)
        def quote(value):
            return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'
        launcher = output / 'guardian-switch.desktop'
        launcher.write_text('[Desktop Entry]\nType=Application\nName=Guardian Switch\nComment=本机防直连开关\nExec=' +
                            ' '.join(quote(a) for a in argv) + '\nIcon=' + str(icon) + '\nTerminal=false\nCategories=Network;\n', encoding='utf-8')
        launcher.chmod(0o755)


class Session:
    def __init__(self, config, directory, preview=False):
        self.config, self.directory, self.preview = config, directory, preview
        self.token = secrets.token_urlsafe(24)
        self.pending = None
        self.worker = None
        self.started = 0
        self.last = {'protection': 'unknown', 'startup': None, 'message': '点击“刷新状态”，在本机授权读取防火墙。'}

    def state(self):
        if self.pending:
            if self.pending.is_file():
                try:
                    data = json.loads(self.pending.read_text(encoding='utf-8'))
                    self.last = {k: data[k] for k in ('protection', 'startup', 'coverage', 'message', 'checked_at') if k in data}
                    self.last['failed'] = data.get('exit_code', 1) != 0
                except (OSError, ValueError):
                    self.last = {'protection': 'unknown', 'startup': None, 'message': '结果无法读取，请刷新状态。'}
                self.pending = None
            elif self.worker and self.worker.poll() not in (None, 0):
                self.last = {'protection': 'unknown', 'startup': None, 'message': '授权已取消或终端启动失败，请重试。'}
                self.pending = None
            elif time.monotonic() - self.started > 240:
                self.last = {'protection': 'unknown', 'startup': None, 'message': '操作尚未确认，请查看操作终端；不要重复开启。'}
                self.pending = None
        stale = time.time() - self.last.get('checked_at', 0) > 90
        return dict(self.last, pending=bool(self.pending), stale=stale, preview=self.preview)

    def action(self, action):
        if action not in ACTIONS:
            raise ValueError('未知操作。')
        if self.pending:
            raise ValueError('请先完成操作终端中的步骤。')
        if self.preview:
            on = action in {'on', 'status'}
            self.last = {'protection': 'on' if on else 'off', 'startup': on,
                         'message': '演示状态，不读取或修改系统。', 'checked_at': int(time.time())}
            return
        self.pending = self.directory / ('result-' + secrets.token_hex(12) + '.json')
        self.started = time.monotonic()
        try:
            self.worker = launch_terminal(action, self.config, self.pending, self.directory)
        except (OSError, RuntimeError):
            self.pending = None
            raise ValueError('无法打开操作终端，请检查终端安装或从命令行运行。') from None


def handler_for(session):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def trusted(self):
            host = '127.0.0.1:%s' % self.server.server_port
            return (self.headers.get('Host') == host and self.headers.get('Origin', 'http://' + host) == 'http://' + host
                    and self.headers.get('Sec-Fetch-Site', 'same-origin') in {'same-origin', 'none'})

        def send(self, status, body, content_type='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; frame-ancestors 'none'")
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self.trusted() or not self.path.startswith('/' + session.token + '/'):
                return self.send(403, b'{}')
            route = self.path[len(session.token) + 2:]
            if route == 'state':
                return self.send(200, json.dumps(session.state(), ensure_ascii=False).encode())
            assets = {'': ('switch.html', 'text/html; charset=utf-8'), 'switch.css': ('switch.css', 'text/css; charset=utf-8'),
                      'switch.js': ('switch.js', 'text/javascript; charset=utf-8'), 'icon.png': ('icon.png', 'image/png')}
            if route not in assets:
                return self.send(404, b'{}')
            name, mime = assets[route]
            self.send(200, (ASSETS / name).read_bytes(), mime)

        def do_POST(self):
            if not self.trusted() or self.path not in {'/' + session.token + '/action', '/' + session.token + '/close'}:
                return self.send(403, b'{}')
            if self.path.endswith('/close'):
                if session.pending:
                    return self.send(409, json.dumps({'error': '请先完成或取消操作终端中的步骤。'}, ensure_ascii=False).encode())
                self.send(200, b'{}')
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 100 or self.headers.get_content_type() != 'application/json':
                    raise ValueError('请求格式错误。')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict) or set(data) != {'action'} or not isinstance(data['action'], str):
                    raise ValueError('请求格式错误。')
                session.action(data['action'])
                self.send(200, json.dumps(session.state(), ensure_ascii=False).encode())
            except (ValueError, TypeError) as error:
                self.send(400, json.dumps({'error': str(error)}, ensure_ascii=False).encode())
    return Handler


def serve(config, cfg, preview=False, open_browser=True):
    if not preview:
        if os.name == 'nt':
            import ctypes
            elevated = ctypes.windll.shell32.IsUserAnAdmin()
        else:
            elevated = os.geteuid() == 0
        if elevated:
            raise ValueError('请以普通用户启动界面，操作时再提权。')
    with tempfile.TemporaryDirectory(prefix='guardian-switch-') as tmp:
        session = Session(config, Path(tmp), preview)
        server = HTTPServer(('127.0.0.1', 0), handler_for(session))
        server.timeout = 5
        url = 'http://127.0.0.1:%s/%s/' % (server.server_port, session.token)
        print(url, flush=True)
        timer = threading.Timer(900, server.shutdown)
        timer.daemon = True
        timer.start()
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        finally:
            timer.cancel()
            server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Guardian Switch UI preview (no system operations)')
    parser.add_argument('--preview', action='store_true', required=True)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    serve(None, {}, preview=True, open_browser=not args.no_browser)
