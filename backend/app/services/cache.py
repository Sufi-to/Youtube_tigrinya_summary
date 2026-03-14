from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class InMemoryCache:
    def __init__(self) -> None:
        self._data: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._data.get(key)
        if not entry:
            return None
        if entry.expires_at < time.time():
            self._data.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._data[key] = CacheEntry(value=value, expires_at=time.time() + ttl_seconds)
