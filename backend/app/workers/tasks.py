from __future__ import annotations

import base64
from typing import Any

from app.services.interactions.interaction_engine import InteractionEngine
from app.services.interactions.models import InteractionRecord
from app.services.ocr.ocr_service import OCRService
from app.services.scheduling.schedule_optimizer import MedicationDosage, ScheduleOptimizer
from app.workers.celery_app import celery_app


if celery_app is None:
    # Keep import path stable even when celery is disabled/unavailable.
    def _task_stub(*_args: Any, **_kwargs: Any) -> Any:
        raise RuntimeError("Celery is disabled or not installed.")

    extract_drug_task = _task_stub
    analyze_interactions_task = _task_stub
    generate_schedule_task = _task_stub

else:

    @celery_app.task(
        bind=True,
        autoretry_for=(RuntimeError,),
        retry_backoff=True,
        retry_jitter=True,
        max_retries=3,
    )
    def extract_drug_task(self, image_b64: str, known_drugs: list[str]) -> dict[str, Any]:
        image_bytes = base64.b64decode(image_b64.encode("utf-8"))
        service = OCRService()
        return service._execute_sync_pipeline(image_bytes, known_drugs)


    @celery_app.task(
        bind=True,
        autoretry_for=(RuntimeError,),
        retry_backoff=True,
        retry_jitter=True,
        max_retries=3,
    )
    def analyze_interactions_task(
        self,
        prescribed_drugs: list[str],
        db_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        engine = InteractionEngine()
        parsed_records = [InteractionRecord(**record) for record in db_records]
        return engine.analyze_prescription(prescribed_drugs, parsed_records)


    @celery_app.task(
        bind=True,
        autoretry_for=(RuntimeError,),
        retry_backoff=True,
        retry_jitter=True,
        max_retries=3,
    )
    def generate_schedule_task(
        self,
        dosages: list[dict[str, Any]],
        db_records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        optimizer = ScheduleOptimizer()
        parsed_dosages = [MedicationDosage(**row) for row in dosages]
        parsed_records = [InteractionRecord(**record) for record in db_records]
        return optimizer.generate_schedule(parsed_dosages, parsed_records)
