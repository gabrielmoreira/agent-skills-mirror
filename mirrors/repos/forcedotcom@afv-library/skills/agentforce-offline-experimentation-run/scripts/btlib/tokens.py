"""SFAP token refresh (--token-org): mint a new token when the run's token expires.

An SFAP token lasts about two hours, so a long replay outlives it. On an HTTP 401 the client
calls the refresher with the token that was refused. The refresher runs

    bash scripts/resolve-token.sh --org <alias>

which writes a new token to a new 0600 temp file and prints that file's path. The new token
replaces the old one in the run's token file (atomically, mode 0600), the script's file is
deleted, and the client sends the request again, once.

- One mint per expiry: requests refused with the same token wait for the first refresh, then
  retry with its token. A lock file next to the token file (<token file>.lock, empty) extends
  this to other processes reading the same file.
- No loops: a token minted here and refused within FRESH_SECONDS is not an expired token (wrong
  org, missing scope), and a mint that failed is not repeated for the same token. Those requests
  stay http_401 infra errors.
- The new token must be for the run's SFAP endpoint and core tenant: another org's is not used.
- The token never enters argv or output: the script gets the org alias only, and its stdout (a
  file path and IDs) is parsed, never printed.
"""

import contextlib
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import tempfile
import threading
import time

from .redact import redact, register_secret

RESOLVE_TOKEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resolve-token.sh")
FRESH_SECONDS = 300
SCRIPT_FILE_PREFIX = "offexp-jwt."  # resolve-token.sh's temp files: the only files deleted here


def read_token(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return ""


def _digest(token):
    return hashlib.sha256((token or "").encode("utf-8")).hexdigest()


def _last_json(out):
    """The script's JSON line, {} if there is none."""
    for line in reversed((out or "").strip().splitlines()):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        return obj if isinstance(obj, dict) else {}
    return {}


def _print(msg):
    print(msg, flush=True)


class TokenRefresher:
    """SfapClient's on_unauthorized(token_used): True when the token file now holds a token worth a retry."""

    def __init__(self, token_file, org, base_url, core_tenant_id, script=None, timeout=180, log=_print,
                 clock=time.monotonic):
        self.token_file = os.path.abspath(token_file)
        self.org = org
        self.base_url = (base_url or "").rstrip("/")
        self.core_tenant_id = core_tenant_id
        self.script = script or RESOLVE_TOKEN
        self.timeout = timeout
        self.log = log
        self._clock = clock
        self.refreshes = self.failures = 0
        self._lock = threading.Lock()
        self._minted = {}  # digest of a token minted here -> when
        self._given_up = set()  # digests of tokens not to refresh again

    def __call__(self, token_used):
        used = _digest(token_used)
        with self._lock:
            try:
                with self._file_lock():
                    if read_token(self.token_file) not in ("", token_used):
                        return True  # refreshed meanwhile, by another thread or process
                    if used in self._given_up:
                        return False
                    minted = self._minted.get(used)
                    if minted is not None and self._clock() - minted < FRESH_SECONDS:
                        why = "a token minted moments ago was refused too, so expiry is not the problem"
                    else:
                        why = self._mint()
            except OSError as e:
                why = f"cannot update the token file ({type(e).__name__})"
            if why is None:
                self.refreshes += 1
                self.log(f"SFAP token refreshed (resolve-token.sh --org {self.org})")
                return True
            self._given_up.add(used)
            self.failures += 1
            self.log(f"WARNING: SFAP token not refreshed: {redact(why)}. The calls refused with HTTP 401 are "
                     "infra errors; with --cache-dir a rerun sends only those")
            return False

    def _mint(self):
        """Run the script and install its token: None on success, else why not."""
        try:
            proc = subprocess.Popen(["bash", self.script, "--org", self.org], stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    universal_newlines=True, start_new_session=True)
        except OSError as e:
            return f"cannot run resolve-token.sh ({type(e).__name__})"
        try:
            out, _ = proc.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(OSError):
                os.killpg(proc.pid, signal.SIGKILL)  # the script's sf and curl children too
            proc.communicate()
            return f"resolve-token.sh --org {self.org} took more than {self.timeout:g}s"
        info = _last_json(out)
        new_file = info.get("tokenFile")
        try:
            if info.get("error"):
                return f"resolve-token.sh --org {self.org}: {info['error']} ({info.get('hint') or 'no hint'})"
            if proc.returncode or not new_file:
                return f"resolve-token.sh --org {self.org} exited {proc.returncode} without a token file"
            tenant = info.get("coreTenantId")
            if (info.get("baseUrl") or "").rstrip("/") != self.base_url or (tenant and tenant != self.core_tenant_id):
                return (f"resolve-token.sh --org {self.org} gives a token for another SFAP endpoint or core tenant "
                        "than the run's (is --token-org the org --token-info was made for?)")
            token = read_token(new_file)
            if not token:
                return "resolve-token.sh wrote an empty token file"
            register_secret(token)
            self._install(token)
            self._minted[_digest(token)] = self._clock()
            return None
        finally:
            if (new_file and os.path.abspath(new_file) != self.token_file
                    and os.path.basename(new_file).startswith(SCRIPT_FILE_PREFIX) and os.path.isfile(new_file)):
                os.unlink(new_file)

    def _install(self, token):
        """Replace the token file atomically: a reader sees the old token or the new one, never a partial file."""
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(self.token_file), prefix=".bt-token-")  # mode 0600
        try:
            with os.fdopen(fd, "w") as f:
                f.write(token)
            os.replace(tmp, self.token_file)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise

    @contextlib.contextmanager
    def _file_lock(self):
        fd = os.open(self.token_file + ".lock", os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            yield
        finally:
            os.close(fd)  # releases the lock

    def stats(self):
        with self._lock:
            return {"refreshes": self.refreshes, "failures": self.failures}
