# retrying-lite 0.3.1, vendored from https://github.com/pellucid-oss/retrying-lite
# Copyright (c) 2020 Pellucid OSS contributors. MIT licence, see LICENSE.
"""A tiny retry decorator with exponential backoff and jitter."""

import functools
import random
import time

__all__ = ["retry", "RetryError"]
__version__ = "0.3.1"


class RetryError(Exception):
    """Raised when every attempt failed. The last exception is the __cause__."""

    def __init__(self, attempts):
        super().__init__("gave up after %d attempts" % attempts)
        self.attempts = attempts


def _backoff(attempt, base, cap):
    # Compute the delay
    delay = min(cap, base * (2 ** attempt))
    # Add some jitter so clients don't retry in lockstep
    return delay * (0.5 + random.random() / 2)


def retry(times=3, on=(Exception,), base=0.2, cap=5.0, sleep=time.sleep):
    """Retry the wrapped function up to `times` attempts when it raises one of `on`."""
    if times < 1:
        raise ValueError("times must be >= 1")
    if isinstance(on, type):
        on = (on,)

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            # Loop until it works
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except on as exc:
                    last = exc
                    if attempt + 1 < times:
                        sleep(_backoff(attempt, base, cap))
            # print("giving up", fn.__name__)
            raise RetryError(times) from last

        return wrapper

    return decorate
