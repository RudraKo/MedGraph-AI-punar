from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.domain.models.adherence import Base as AdherenceBase


settings = get_settings()

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """
    Creates known ORM tables on startup.
    In production, prefer Alembic migrations for all schema changes.
    """
    AdherenceBase.metadata.create_all(bind=engine)


def check_database_health() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
