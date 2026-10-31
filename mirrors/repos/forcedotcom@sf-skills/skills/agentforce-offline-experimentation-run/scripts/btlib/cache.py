"""Result cache (--cache-dir): a request already answered is not sent again.

An entry is keyed by the SFAP endpoint, the core tenant and the payload exactly as sent, so the
model alias, the generation settings and the seed (that is, the repeat) are all in the key: a
patched request, another model or another repeat is another entry. Judge calls go through the
same cache. Only answers are stored: an infra error, or a 200 without a generation, is sent
again by the next run.

    <cache dir>/<key[:2]>/<key>.json   {"schema": "bt.cache/1", "http_status", "latency_ms", "body"}

The response body is stored, not the scores, so a change to the scoring re-scores cached answers.
Entries are written through the redactor, atomically, with mode 0600. They hold the model's
answers to user conversations: keep the cache dir out of git, like run dirs.
"""

import hashlib
import json
import os
import tempfile
import threading

from . import SCHEMA_CACHE
from .redact import redact_obj
from .sfap import parse_generation


class CachingClient:
    """generate(payload) as SfapClient's, answered from cache_dir when the payload was answered before."""

    def __init__(self, client, cache_dir):
        self.client = client
        self.cache_dir = cache_dir
        self.hits = self.calls = self.write_errors = 0
        self._lock = threading.Lock()
        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)
            os.chmod(cache_dir, 0o700)

    def key(self, payload):
        blob = json.dumps({"url": self.client.url, "tenant": self.client.core_tenant_id, "payload": payload},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _path(self, key):
        return os.path.join(self.cache_dir, key[:2], key + ".json")

    @staticmethod
    def _load(path):
        try:
            with open(path, encoding="utf-8") as f:
                entry = json.load(f)
        except (OSError, ValueError):
            return None
        return entry if isinstance(entry, dict) and entry.get("schema") == SCHEMA_CACHE else None

    def _store(self, path, entry):
        """Write the entry atomically; a failure is counted, not raised (the answer is still good)."""
        tmp = None
        try:
            d = os.path.dirname(path)
            if not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
                os.chmod(d, 0o700)
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")  # mode 0600
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(redact_obj(entry), f, ensure_ascii=False)
            os.replace(tmp, path)
        except OSError:
            with self._lock:
                self.write_errors += 1
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

    def generate(self, payload):
        path = self._path(self.key(payload))
        entry = self._load(path)
        parsed = parse_generation(entry.get("body")) if entry else None
        if parsed is not None:
            with self._lock:
                self.hits += 1
            return {"status": "ok", "http_status": entry.get("http_status"), "body": entry["body"],
                    "error": None, "error_kind": None, "attempts": 0, "latency_ms": entry.get("latency_ms"),
                    "response": parsed, "cached": True}
        res = self.client.generate(payload)
        with self._lock:
            self.calls += 1
        if res["status"] == "ok":
            self._store(path, {"schema": SCHEMA_CACHE, "http_status": res.get("http_status"),
                               "latency_ms": res.get("latency_ms"), "body": res["body"]})
        res["cached"] = False
        return res

    def stats(self):
        with self._lock:
            return {"hits": self.hits, "calls": self.calls, "write_errors": self.write_errors}
