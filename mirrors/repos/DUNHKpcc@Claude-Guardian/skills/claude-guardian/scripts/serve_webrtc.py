"""Finite loopback-only server for one fixed, opt-in WebRTC asset.

Starting this helper does not open a browser or initiate STUN. The served page
still requires explicit per-run consent and a user click in the intended browser
profile. Expiry initiates listener cleanup; failures leave closure unconfirmed.
Closing the listener cannot revoke a previously loaded page.
No results, credentials, raw request logs, or user data are collected by this
server. Optional rejection diagnostics emit one fixed classification to stderr.
"""
import argparse
import errno
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import math
from pathlib import Path
import socket
import sys
import threading
import time

ROUTE = '/webrtc-probe.html'
DEFAULT_DURATION = 300
MAX_DURATION = 900
MAX_CONNECTIONS = 8
ASSET = Path(__file__).resolve().parent.parent / 'assets' / 'webrtc-probe.html'
_STAGES = frozenset({'startup', 'asset', 'bind', 'publish_url', 'serve', 'cleanup'})
_REJECTION_STAGES = frozenset({'request', 'host', 'origin', 'fetch_site', 'body', 'route'})
_FETCH_CLASSES = (
    ('Sec-Fetch-Site', 'fetch_site', frozenset({'none', 'same-origin', 'same-site', 'cross-site'})),
    ('Sec-Fetch-Mode', 'fetch_mode', frozenset({'cors', 'navigate', 'no-cors', 'same-origin', 'websocket'})),
    ('Sec-Fetch-Dest', 'fetch_dest', frozenset({
        'audio', 'audioworklet', 'document', 'embed', 'empty', 'font', 'frame',
        'iframe', 'image', 'manifest', 'object', 'paintworklet', 'report', 'script',
        'serviceworker', 'sharedworker', 'style', 'track', 'video', 'worker', 'xslt'})),
    ('Sec-Fetch-User', 'fetch_user', frozenset({'?1'})),
)


def _at_stage(stage, function, *args):
    """Attach only a fixed phase; preserve the caller's original exception type."""
    try:
        return function(*args)
    except (Exception, KeyboardInterrupt) as error:
        error._helper_stage = stage
        raise


def _failure_diagnostic(error, stage):
    observed = getattr(error, '_helper_stage', stage)
    stage = observed if type(observed) is str and observed in _STAGES else stage
    stage = stage if type(stage) is str and stage in _STAGES else 'startup'
    if isinstance(error, KeyboardInterrupt):
        code = 'INTERRUPTED'
    elif isinstance(error, PermissionError):
        code = 'PERMISSION_DENIED'
    elif isinstance(error, OSError):
        number = error.errno
        code = ({errno.EADDRINUSE: 'ADDRESS_IN_USE',
                 errno.EADDRNOTAVAIL: 'ADDRESS_UNAVAILABLE'}.get(number, 'IO_ERROR')
                if type(number) is int else 'IO_ERROR')
    elif isinstance(error, (RuntimeError, ValueError)):
        code = 'INVALID_STATE'
    else:
        code = 'UNEXPECTED_ERROR'
    return stage, code


def _report_failure(error, stage, url_may_be_published):
    stage, code = _failure_diagnostic(error, stage)
    state = 'unknown' if url_may_be_published else 'not_started'
    cleanup = getattr(error, '_helper_cleanup_state', 'unknown')
    cleanup = cleanup if type(cleanup) is str and cleanup in {'complete', 'unknown'} else 'unknown'
    message = ('Local WebRTC helper failed; stage=' + stage + '; error=' + code
               + '; probe_state=' + state + '; cleanup_state=' + cleanup + '.')
    if cleanup == 'unknown':
        message += ' Listener closure is unconfirmed.'
    if url_may_be_published:
        message += (' Close any loaded probe page; stopping the local server'
                    ' cannot stop a browser probe.')
    try:
        print(message, file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass  # A failed output sink cannot justify a raw exception traceback.


def _read_asset():
    if ASSET.is_symlink() or not ASSET.is_file():
        raise RuntimeError('Fixed WebRTC asset unavailable')
    asset = ASSET.read_bytes()
    if len(asset) > 128 * 1024:
        raise RuntimeError('Fixed WebRTC asset exceeds size limit')
    return asset


class _AssetHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
    server_version = 'GuardianLocalProbe'
    sys_version = ''

    def log_message(self, *_args):
        pass

    def log_error(self, *_args):
        pass

    def send_error(self, code, message=None, explain=None):
        # Never reflect request paths, headers, methods, credentials, or exceptions.
        self._reject('request', code, b'Request rejected.\n', 'text/plain; charset=utf-8')

    def _diagnose_rejection(self, stage):
        if getattr(self.server, 'diagnose_rejection', False) is not True:
            return
        with self.server._rejection_lock:
            if self.server._rejection_reported:
                return
            # Claim before output, including a failed sink, so retries cannot log
            # additional requests. The budget belongs to this server instance.
            self.server._rejection_reported = True
        try:
            headers = getattr(self, 'headers', None)

            def values(name):
                return headers.get_all(name, []) if headers is not None else []

            def match(name, expected):
                observed = values(name)
                return 'absent' if not observed else 'match' if observed == [expected] else 'invalid'

            method = getattr(self, 'command', None)
            parts = getattr(self, 'requestline', '').split()
            exact_route = (getattr(self, 'path', None) == ROUTE
                           and len(parts) >= 2 and parts[1] == ROUTE)
            fields = [
                ('stage', stage if type(stage) is str and stage in _REJECTION_STAGES else 'request'),
                ('method', method if method in ('GET', 'HEAD') else 'other'),
                ('host', match('Host', self.server.authority)),
                ('origin', match('Origin', 'http://' + self.server.authority)),
                ('exact_route', 'yes' if exact_route else 'no'),
                ('content_length', 'present' if values('Content-Length') else 'absent'),
                ('transfer_encoding', 'present' if values('Transfer-Encoding') else 'absent'),
            ]
            for name, field, allowed in _FETCH_CLASSES:
                observed = values(name)
                value = ('missing' if not observed else 'duplicate' if len(observed) != 1
                         else observed[0] if type(observed[0]) is str and observed[0] in allowed
                         else 'invalid')
                fields.append((field, value))
            print('Local WebRTC request rejected; ' + '; '.join(
                key + '=' + value for key, value in fields), file=sys.stderr, flush=True)
        except Exception:
            pass  # Optional diagnostics, including sink errors, cannot change admission.

    def _reject(self, stage, code, body, content_type):
        self._diagnose_rejection(stage)
        return self._reply(code, body, content_type)

    def _reply(self, code, body, content_type):
        self.close_connection = True
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'close')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def _is_user_navigation(self):
        # Host and Origin have already passed their exact-match gates. This
        # exception only delivers the static page; starting ICE still needs the
        # page's separate per-run consent and click.
        request_parts = getattr(self, 'requestline', '').split()
        if (getattr(self, 'command', None) != 'GET' or getattr(self, 'path', None) != ROUTE
                or len(request_parts) < 2 or request_parts[1] != ROUTE):
            return False
        if any(self.headers.get_all(name) for name in (
                'Content-Length', 'Transfer-Encoding', 'Purpose', 'Sec-Purpose')):
            return False
        return all(self.headers.get_all(name, []) == [value] for name, value in (
            ('Sec-Fetch-Mode', 'navigate'),
            ('Sec-Fetch-Dest', 'document'),
            ('Sec-Fetch-User', '?1')))

    def _serve_asset(self):
        hosts = self.headers.get_all('Host', [])
        if hosts != [self.server.authority]:
            return self._reject('host', 421, b'Invalid local host.\n', 'text/plain')
        origins = self.headers.get_all('Origin', [])
        if origins and origins != ['http://' + self.server.authority]:
            return self._reject('origin', 403, b'Origin rejected.\n', 'text/plain')
        fetch_sites = self.headers.get_all('Sec-Fetch-Site', [])
        # Duplicated, combined, or unknown Site values cannot fall through as
        # non-cross-site requests, regardless of their order.
        if (fetch_sites and (len(fetch_sites) != 1 or fetch_sites[0] not in {
                'none', 'same-origin', 'same-site', 'cross-site'})) or (
                fetch_sites == ['cross-site'] and not self._is_user_navigation()):
            return self._reject('fetch_site', 403, b'Cross-site request rejected.\n', 'text/plain')
        if self.headers.get_all('Transfer-Encoding') or self.headers.get_all('Content-Length'):
            return self._reject('body', 400, b'Request body not supported.\n', 'text/plain')
        # BaseHTTPRequestHandler normalizes a leading '//'; inspect the original
        # target as well so this endpoint accepts only one exact origin-form path.
        request_parts = self.requestline.split()
        if self.path != ROUTE or len(request_parts) < 2 or request_parts[1] != ROUTE:
            return self._reject('route', 404, b'Not found.\n', 'text/plain')
        self._reply(200, self.server.asset, 'text/html; charset=utf-8')

    do_GET = _serve_asset
    do_HEAD = _serve_asset


class _BoundedServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False
    allow_reuse_address = False

    def __init__(self, asset, diagnose_rejection=False):
        if type(diagnose_rejection) is not bool:
            raise ValueError('Rejection diagnostics require a boolean')
        self.diagnose_rejection = diagnose_rejection
        self._rejection_lock = threading.Lock()
        self._rejection_reported = False
        self.asset = asset
        self.connections = set()
        self._pending_closes = set()
        self.connection_lock = threading.Lock()
        self.closing = False
        super().__init__(('127.0.0.1', 0), _AssetHandler)
        self.authority = '127.0.0.1:' + str(self.server_port)
        self.timeout = 0.05

    def process_request(self, request, client_address):
        with self.connection_lock:
            if self.closing or len(self.connections) >= MAX_CONNECTIONS:
                self.shutdown_request(request)
                return
            self.connections.add(request)
        request.settimeout(1.0)
        try:
            super().process_request(request, client_address)
        except Exception:
            with self.connection_lock:
                self.connections.discard(request)
            self.shutdown_request(request)
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            with self.connection_lock:
                self.connections.discard(request)

    def handle_error(self, request, client_address):
        pass  # No tracebacks with request/user data.

    def server_close(self):
        with self.connection_lock:
            self.closing = True
            connections = tuple(self.connections | self._pending_closes)
        first_error = None
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass  # A closed/disconnected socket may reject shutdown.
            except BaseException as error:
                if first_error is None:
                    first_error = error
            try:
                connection.close()
            except BaseException as error:
                if first_error is None:
                    first_error = error
                with self.connection_lock:
                    self._pending_closes.add(connection)
            else:
                with self.connection_lock:
                    self.connections.discard(connection)
                    self._pending_closes.discard(connection)
        # Attempt every owned resource even if an earlier close failed or was
        # interrupted. Failed connections remain tracked for a later retry.
        try:
            super().server_close()
        except BaseException as error:
            if first_error is None:
                first_error = error
        if first_error is not None:
            raise first_error


class LocalProbeServer:
    """Explicit construction binds 127.0.0.1 on an OS-selected ephemeral port.

    Use as a context manager. serve() blocks until a finite deadline or cancellation
    and always attempts to close listener and active requests. Failed closure is
    unconfirmed and close() can retry it. Serving remains single-use.
    There is intentionally no host, port, directory, or asset-path option.
    """
    def __init__(self, diagnose_rejection=False):
        asset = _at_stage('asset', _read_asset)
        self._server = _at_stage('bind', _BoundedServer, asset, diagnose_rejection)
        self._cancel = threading.Event()
        self._started = False
        self._closed = False
        self._cleanup_state = 'unknown'
        self.url = 'http://' + self._server.authority + ROUTE

    def __enter__(self):
        return self

    def __exit__(self, _kind, error, _traceback):
        self._close_preserving(error)

    def _close_preserving(self, primary_error):
        try:
            self.close()
        except BaseException:
            if primary_error is None:
                raise
            primary_error._helper_cleanup_state = 'unknown'
        else:
            if primary_error is not None:
                primary_error._helper_cleanup_state = self._cleanup_state

    def close(self):
        self._cancel.set()
        if not self._closed:
            self._cleanup_state = 'unknown'
            try:
                _at_stage('cleanup', self._server.server_close)
            except BaseException as error:
                error._helper_cleanup_state = 'unknown'
                raise
            self._closed = True
            self._cleanup_state = 'complete'

    def serve(self, duration_seconds=DEFAULT_DURATION, cancel_event=None):
        if (isinstance(duration_seconds, bool) or not isinstance(duration_seconds, (int, float))
                or not 0 < duration_seconds <= MAX_DURATION or not math.isfinite(duration_seconds)):
            raise ValueError('Duration must be greater than zero and at most 900 seconds')
        if self._started or self._closed:
            raise RuntimeError('Server is single-use')
        self._started = True
        deadline = time.monotonic() + duration_seconds
        primary_error = None
        try:
            while not self._cancel.is_set() and not (cancel_event and cancel_event.is_set()):
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._server.timeout = min(0.05, remaining)
                try:
                    self._server.handle_request()
                except (OSError, ValueError):
                    if not self._cancel.is_set():
                        raise
        except BaseException as error:
            primary_error = error
            raise
        finally:
            self._close_preserving(primary_error)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--duration', type=float, default=DEFAULT_DURATION,
                        help='HTTP listener lifetime in seconds, greater than 0 and at most 900 (default 300)')
    parser.add_argument('--diagnose-rejection', action='store_true',
                        help='Emit one fixed, redacted rejection classification to local stderr')
    args = parser.parse_args(argv)
    if not math.isfinite(args.duration) or not 0 < args.duration <= MAX_DURATION:
        parser.error('duration must be greater than 0 and at most 900 seconds')
    stage = 'startup'
    url_may_be_published = False
    try:
        with LocalProbeServer(diagnose_rejection=args.diagnose_rejection) as server:
            stage = 'publish_url'
            # Even a partially failed output write may have disclosed the URL.
            url_may_be_published = True
            print(server.url, flush=True)
            print('Open manually in the intended browser profile. No probe runs until consent and click. Ctrl+C requests local server shutdown.', flush=True)
            stage = 'serve'
            server.serve(args.duration)
    except KeyboardInterrupt as error:
        _report_failure(error, stage, url_may_be_published)
        return 130
    except Exception as error:
        _report_failure(error, stage, url_may_be_published)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
