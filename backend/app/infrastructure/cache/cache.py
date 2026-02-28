from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any

from app.core.config import get_settings

try:
    import redis as redis_lib
except ImportError:  # pragma: no cover - optional dependency fallback
    redis_lib = None


class InMemoryCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def _prune(self) -> None:
        now = time.time()
        expired = [key for key, (_, expiry) in self._store.items() if expiry <= now]
        for key in expired:
            self._store.pop(key, None)

    def get(self, key: str) -> str | None:
        with self._lock:
            self._prune()
            value = self._store.get(key)
            if not value:
                return None
            return value[0]

    def set(self, key: str, value: str, ex: int) -> None:
        with self._lock:
            expiry = time.time() + max(ex, 1)
            self._store[key] = (value, expiry)

    def incr(self, key: str, ex: int) -> int:
        with self._lock:
            self._prune()
            current_raw = self._store.get(key)
            current = int(current_raw[0]) if current_raw else 0
            current += 1
            expiry = time.time() + max(ex, 1)
            self._store[key] = (str(current), expiry)
            return current

    def ping(self) -> bool:
        return True


class CacheClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._prefix = settings.cache_key_prefix
        self._fallback = InMemoryCache()
        self._redis = None

        if settings.redis_enabled and redis_lib is not None:
            try:
                self._redis = redis_lib.Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_timeout=1,
                    socket_connect_timeout=1,
                )
                # Test once; fallback to in-memory if unavailable.
                self._redis.ping()
            except Exception:
                self._redis = None

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    def ping(self) -> bool:
        if self._redis is not None:
            try:
                return bool(self._redis.ping())
            except Exception:
                return False
        return self._fallback.ping()

    def get_json(self, key: str) -> dict[str, Any] | None:
        full_key = self._full_key(key)
        raw: str | None
        if self._redis is not None:
            try:
                raw = self._redis.get(full_key)
            except Exception:
                raw = self._fallback.get(full_key)
        else:
            raw = self._fallback.get(full_key)

        if not raw:
            return None
        try:
            value = json.loads(raw)
            if isinstance(value, dict):
                return value
            return {"value": value}
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: dict[str, Any], ttl: int) -> None:
        full_key = self._full_key(key)
        payload = json.dumps(value, separators=(",", ":"), sort_keys=True)
        ttl = max(ttl, 1)

        if self._redis is not None:
            try:
                self._redis.set(full_key, payload, ex=ttl)
                return
            except Exception:
                pass
        self._fallback.set(full_key, payload, ex=ttl)

    def increment(self, key: str, ttl: int) -> int:
        full_key = self._full_key(key)
        ttl = max(ttl, 1)

        if self._redis is not None:
            try:
                with self._redis.pipeline() as pipe:
                    pipe.incr(full_key)
                    pipe.expire(full_key, ttl)
                    value, _ = pipe.execute()
                return int(value)
            except Exception:
                pass

        return self._fallback.incr(full_key, ex=ttl)


def build_cache_key(namespace: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


_cache_client_singleton: CacheClient | None = None


def get_cache_client() -> CacheClient:
    global _cache_client_singleton
    if _cache_client_singleton is None:
        _cache_client_singleton = CacheClient()
    return _cache_client_singleton
