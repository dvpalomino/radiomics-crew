"""Shared HTTP layer: caching + retries + polite rate limiting.

A good tool is versatile in what it accepts, strict in what it returns, caches so
it does not burn rate limits, and hands errors back to the agent as text it can
reason about instead of raising and killing the run.
"""

from __future__ import annotations

import time
from functools import lru_cache

import requests

_LAST_CALL: dict[str, float] = {}
_MIN_INTERVAL = 0.35  # seconds between calls to the same host (NCBI: 3 req/s unauthenticated)


def _throttle(host: str) -> None:
    now = time.monotonic()
    delta = now - _LAST_CALL.get(host, 0.0)
    if delta < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - delta)
    _LAST_CALL[host] = time.monotonic()


@lru_cache(maxsize=512)
def cached_get(url: str, params_frozen: tuple[tuple[str, str], ...], timeout: int = 30) -> str:
    """GET with an LRU cache keyed on (url, params). Params must be hashable."""
    host = url.split("/")[2]
    params = dict(params_frozen)
    last_error = ""
    for attempt in range(3):
        _throttle(host)
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={"User-Agent": "RadiomicsCrew/0.1 (research use; contact via repo)"},
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:  # network, 4xx, 5xx
            last_error = str(exc)
            time.sleep(1.5 * (attempt + 1))
    return f"TOOL_ERROR: request to {url} failed after 3 attempts: {last_error}"


def freeze(params: dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((k, str(v)) for k, v in params.items() if v is not None))
