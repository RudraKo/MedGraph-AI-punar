import pytest
from fastapi.testclient import TestClient
from main import app
from typing import Dict, Any, List

# Import dependencies to override
from app.api.v1.ocr import get_ocr_service
from app.api.v1.interactions import get_interaction_engine
from app.api.v1.scheduling import get_schedule_optimizer

from app.services.ocr.ocr_service import OCRService
from app.services.interactions.interaction_engine import InteractionEngine
from app.services.scheduling.schedule_optimizer import ScheduleOptimizer

client = TestClient(app)

# --- MOCK SERVICES ---
class MockOCRService(OCRService):
    async def extract_drug_from_image(self, image_bytes: bytes, known_drugs: list[str]) -> Dict[str, Any]:
        if b"CORRUPT" in image_bytes:
             raise ValueError("Format not recognized")
        if b"FATAL" in image_bytes:
             raise RuntimeError("Mock fatal Tesseract crash")
        return {
            "extracted_text": "MOCK TEXT",
            "matched_drug": "ASPIRIN",
            "confidence_score": 0.99
        }

class MockInteractionEngine(InteractionEngine):
    def analyze_prescription(self, prescribed_drugs: list[str], db_records: list) -> Dict[str, Any]:
        if "CRASH" in prescribed_drugs:
            raise ValueError("Invalid drug formatted")
        return {
            "interactions": [],
            "risk_score": 0,
            "severity_summary": "Safe"
        }

class MockScheduleOptimizer(ScheduleOptimizer):
    def generate_schedule(self, dosages: list, interactions: list) -> Dict[str, Any]:
        if dosages[0].drug_name == "CRASH":
            raise ValueError("Incompatible frequency constraint")
        return {
            "schedule": [
                {"time": "08:00", "medications": [dosages[0].drug_name]}
            ],
            "notes": "Mock scheduled successfully"
        }

@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_ocr_service] = MockOCRService
    app.dependency_overrides[get_interaction_engine] = MockInteractionEngine
    app.dependency_overrides[get_schedule_optimizer] = MockScheduleOptimizer
    yield
    app.dependency_overrides.clear()

# --- TEST OCR ENDPOINT ---
def test_ocr_success():
    response = client.post(
        "/api/v1/ocr/extract-drug",
        files={"image": ("test.png", b"VALID_BYTES", "image/png")}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["matched_drug"] == "ASPIRIN"

def test_ocr_validation_failure():
    # Unsupported file type
    response = client.post(
        "/api/v1/ocr/extract-drug",
        files={"image": ("test.pdf", b"VALID_BYTES", "application/pdf")}
    )
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["detail"]

def test_ocr_domain_exception():
    response = client.post(
        "/api/v1/ocr/extract-drug",
        files={"image": ("test.png", b"CORRUPT_BYTES", "image/png")}
    )
    # The OCRRouter traps ValueErrors as 400 Bad Requests
    assert response.status_code == 400
    assert "Format not recognized" in response.json()["detail"]
    
def test_ocr_fatal_exception():
    response = client.post(
        "/api/v1/ocr/extract-drug",
        files={"image": ("test.png", b"FATAL_BYTES", "image/png")}
    )
    assert response.status_code == 500
    assert "OCR pipeline failure" in response.json()["detail"]


# --- TEST INTERACTIONS ENDPOINT ---
def test_interactions_success():
    response = client.post(
        "/api/v1/check-interactions",
        json={"prescribed_drugs": ["ASPIRIN", "WARFARIN"]}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["severity_summary"] == "Safe"

def test_interactions_validation_failure():
    # Empty list should block
    response = client.post(
        "/api/v1/check-interactions",
        json={"prescribed_drugs": []}
    )
    assert response.status_code == 400
    assert "Medication list cannot be empty" in response.json()["detail"]

def test_interactions_domain_exception():
    response = client.post(
        "/api/v1/check-interactions",
        json={"prescribed_drugs": ["CRASH"]}
    )
    assert response.status_code == 500
    assert "Interaction engine failure" in response.json()["detail"]


# --- TEST SCHEDULING ENDPOINT ---
def test_schedule_success():
    response = client.post(
        "/api/v1/schedule",
        json={"dosages": [{"drug_name": "ASPIRIN", "frequency": 2}]}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["schedule"][0]["medications"][0] == "ASPIRIN"

def test_schedule_validation_failure():
    # Empty dosages array
    response = client.post(
        "/api/v1/schedule",
        json={"dosages": []}
    )
    assert response.status_code == 400
    assert "Dosage list cannot be empty" in response.json()["detail"]

def test_schedule_domain_exception():
    response = client.post(
        "/api/v1/schedule",
        json={"dosages": [{"drug_name": "CRASH", "frequency": 1}]}
    )
    assert response.status_code == 500
    assert "Schedule optimization failure" in response.json()["detail"]
