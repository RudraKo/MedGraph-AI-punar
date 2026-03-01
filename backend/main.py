from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import Any
try:
    from backend.routers import auth, drugs, interactions, prescriptions, schedules, alerts, scan
except ModuleNotFoundError as exc:
    if exc.name == "backend" or (exc.name and exc.name.startswith("backend.")):
        # Support running tests from inside the backend directory (PYTHONPATH=.)
        from routers import auth, drugs, interactions, prescriptions, schedules, alerts, scan
    else:
        raise


def get_ocr_runtime_status_safe() -> dict[str, Any]:
    try:
        try:
            from backend.app.services.ocr.ocr_service import get_ocr_runtime_status
        except ModuleNotFoundError as exc:
            if exc.name == "backend" or (exc.name and exc.name.startswith("backend.")):
                from app.services.ocr.ocr_service import get_ocr_runtime_status
            else:
                raise
        return get_ocr_runtime_status()
    except Exception as exc:  # Keep API bootable even without OCR deps
        return {
            "ready": False,
            "message": f"OCR runtime unavailable: {exc}",
        }

load_dotenv()

app = FastAPI(title="MedGraph.AI API", version="1.0.0")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(drugs.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(prescriptions.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "MedGraph.AI API Running"}


@app.get("/health")
def health_check():
    ocr_status = get_ocr_runtime_status_safe()
    return {
        "status": "healthy",
        "ocr_ready": ocr_status["ready"],
        "ocr_message": ocr_status["message"],
    }


@app.get("/health/ocr")
def ocr_health_check():
    return get_ocr_runtime_status_safe()
