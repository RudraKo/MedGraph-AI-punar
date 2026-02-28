from __future__ import annotations

from app.core.config import get_settings

try:
    from celery import Celery
except ImportError:  # pragma: no cover - optional dependency fallback
    Celery = None


settings = get_settings()

celery_app = None
if Celery is not None and settings.celery_enabled:
    celery_app = Celery(
        "medigraph",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_default_retry_delay=5,
        task_track_started=True,
        task_routes={
            "app.workers.tasks.extract_drug_task": {"queue": "ocr_cpu"},
            "app.workers.tasks.analyze_interactions_task": {"queue": "graph_compute"},
            "app.workers.tasks.generate_schedule_task": {"queue": "graph_compute"},
        },
    )
