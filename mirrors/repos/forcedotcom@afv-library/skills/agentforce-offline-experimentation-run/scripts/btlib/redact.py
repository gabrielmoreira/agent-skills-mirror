"""Scrub credentials from text before it is written to disk or printed.

Every artifact writer and log line in btlib goes through redact(). Besides the patterns
below, the SFAP client registers the token it read, so an opaque (non-JWT) token is
scrubbed too.
"""

import re

_BEARER = re.compile(r"(?i)\b(bearer\s+)[^\s\"'<>\\]{16,}")  # any long run: session ids contain "!"
_JWT = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]+")
_SECRETS = set()
REDACTED = "<REDACTED>"


def register_secret(value):
    """Scrub this exact string from every later redact() call (ignored if short)."""
    if isinstance(value, str) and len(value) >= 16:
        _SECRETS.add(value)


def redact(text):
    if not isinstance(text, str):
        text = str(text)
    for secret in _SECRETS:
        if secret in text:
            text = text.replace(secret, REDACTED)
    text = _BEARER.sub(lambda m: m.group(1) + REDACTED, text)
    return _JWT.sub(REDACTED, text)


def redact_obj(obj):
    """redact() applied to every string inside a JSON-like value."""
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [redact_obj(v) for v in obj]
    return obj
