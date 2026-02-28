import pytest
from app.services.interactions.interaction_engine import InteractionEngine, InteractionRecord, SeverityLevel

@pytest.fixture
def mock_db_records():
    return [
        InteractionRecord(drug_a="ASPIRIN", drug_b="WARFARIN", severity=SeverityLevel.SEVERE, explanation="Increased bleeding risk."),
        InteractionRecord(drug_a="OMEPRAZOLE", drug_b="WARFARIN", severity=SeverityLevel.MODERATE, explanation="Altered metabolism."),
        InteractionRecord(drug_a="LISINOPRIL", drug_b="POTASSIUM", severity=SeverityLevel.CONTRAINDICATED, explanation="Fatal hyperkalemia risk.")
    ]

@pytest.fixture
def engine():
    return InteractionEngine()

def test_no_interactions(engine, mock_db_records):
    prescription = ["PARACETAMOL", "AMOXICILLIN"]
    result = engine.analyze_prescription(prescription, mock_db_records)
    
    assert result["risk_score"] == 0
    assert result["severity_summary"] == "Low"
    assert len(result["interactions"]) == 0

def test_severe_interactions(engine, mock_db_records):
    prescription = ["ASPIRIN", "WARFARIN", "LISINOPRIL", "PARACETAMOL"]
    result = engine.analyze_prescription(prescription, mock_db_records)
    
    # Only Aspirin + Warfarin is severely interacting in the list (Weight = 4)
    # 100 * (1 - e^(-0.322 * 4)) = 72
    assert result["risk_score"] == 72
    assert result["severity_summary"] == "High"
    assert len(result["interactions"]) == 1
    assert result["interactions"][0]["severity"] == "severe"

def test_empty_medication_list(engine, mock_db_records):
    result = engine.analyze_prescription([], mock_db_records)
    
    assert result["risk_score"] == 0
    assert result["severity_summary"] == "Low"
    assert len(result["interactions"]) == 0

def test_duplicate_drugs(engine, mock_db_records):
    # Edgecase Fix: Passing duplicate drugs shouldn't duplicate interaction alerts
    # ["ASPIRIN", "ASPIRIN", "WARFARIN"] -> Should be stripped internally to ["ASPIRIN", "WARFARIN"]
    prescription = ["ASPIRIN", "ASPIRIN", "WARFARIN"]
    result = engine.analyze_prescription(prescription, mock_db_records)
    
    # Still calculates to Weight=4 (Score=72) instead of counting it twice.
    assert result["risk_score"] == 72  
    assert len(result["interactions"]) == 1

def test_whitespace_sanitization(engine, mock_db_records):
    prescription = ["   Aspirin  ", "  WaRfArIn\t"]
    result = engine.analyze_prescription(prescription, mock_db_records)
    
    assert result["risk_score"] == 72
    assert len(result["interactions"]) == 1

def test_case_insensitive_matching(engine, mock_db_records):
    prescription = ["aspirin", "WaRfArIn"]
    result = engine.analyze_prescription(prescription, mock_db_records)
    
    assert result["risk_score"] == 72
    assert len(result["interactions"]) == 1
