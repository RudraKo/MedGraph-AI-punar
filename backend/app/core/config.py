from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    debug: bool
    log_level: str

    database_url: str
    sqlalchemy_echo: bool

    redis_url: str
    redis_enabled: bool
    cache_ttl_seconds: int
    cache_key_prefix: str

    rate_limit_enabled: bool
    rate_limit_per_minute: int

    celery_enabled: bool
    celery_broker_url: str
    celery_result_backend: str

    allowed_origins: tuple[str, ...]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
    allowed_origins = tuple(
        origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()
    )

    return Settings(
        app_name=os.getenv("APP_NAME", "MediGraph API"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=_to_bool(os.getenv("DEBUG"), False),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./medgraph.db"),
        sqlalchemy_echo=_to_bool(os.getenv("DB_ECHO"), False),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        redis_enabled=_to_bool(os.getenv("REDIS_ENABLED"), True),
        cache_ttl_seconds=_to_int(os.getenv("CACHE_TTL_SECONDS"), 300),
        cache_key_prefix=os.getenv("CACHE_KEY_PREFIX", "medigraph"),
        rate_limit_enabled=_to_bool(os.getenv("RATE_LIMIT_ENABLED"), True),
        rate_limit_per_minute=_to_int(os.getenv("RATE_LIMIT_PER_MINUTE"), 120),
        celery_enabled=_to_bool(os.getenv("CELERY_ENABLED"), False),
        celery_broker_url=os.getenv(
            "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/1")
        ),
        celery_result_backend=os.getenv(
            "CELERY_RESULT_BACKEND",
            os.getenv("REDIS_URL", "redis://localhost:6379/2"),
        ),
        allowed_origins=allowed_origins if allowed_origins else ("*",),
    )
