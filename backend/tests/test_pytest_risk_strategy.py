import pytest
from app.services.interactions.interaction_engine import InteractionEngine, InteractionRecord, SeverityLevel
from app.services.interactions.scoring_strategies import ExponentialRiskStrategy

def test_large_interaction_list_bounds():
    """
    Verifies that a large list of interactions (15) remains bounded 
    but accurately represents extreme clinical risk.
    """
    engine = InteractionEngine(scoring_strategy=ExponentialRiskStrategy())
    
    # 15 moderate interactions (W=2 each) = Raw Weight 30
    # Formula: 100 * (1 - e^(-0.322 * 30))
    # 0.322 * 30 = 9.66
    # e^(-9.66) is very small (~0.000063)
    # Score should be ~99.9... masked to 100 or close to 99.
    
    # Create 15 drugs that all interact with DRUG_MAIN
    drugs = [f"DRUG_{i}" for i in range(16)] # 16 drugs -> 15 pairs involving DRUG_MAIN
    
    mock_db = []
    for i in range(1, 16):
        mock_db.append(InteractionRecord(
            drug_a="DRUG_0",
            drug_b=f"DRUG_{i}",
            severity=SeverityLevel.MODERATE,
            explanation=f"Interaction {i}"
        ))
        
    result = engine.analyze_prescription(drugs, mock_db)
    
    assert result["raw_weight"] == 30
    assert result["risk_score"] <= 100
    assert result["risk_score"] > 95
    assert result["clinical_band"] == "Critical"
    assert result["severity_counts"]["moderate"] == 15

def test_contraindicated_floor():
    """
    Ensures that any contraindicated interaction forces a minimum score of 80.
    Formula alone for W=5 is ~80, but if we had a rule that was lower, the floor would catch it.
    We'll test it by using a mock strategy if needed, but the requirement is in the scoring engine.
    """
    engine = InteractionEngine()
    
    # One contraindicated interaction
    records = [
        InteractionRecord(drug_a="A", drug_b="B", severity=SeverityLevel.CONTRAINDICATED, explanation="Fatal")
    ]
    
    result = engine.analyze_prescription(["A", "B"], records)
    
    assert result["risk_score"] >= 80
    assert result["clinical_band"] == "Critical"
    assert "TERMINAL RISK" in result["explanation"].upper()

def test_metadata_fields():
    engine = InteractionEngine()
    records = [
        InteractionRecord(drug_a="A", drug_b="B", severity=SeverityLevel.SEVERE, explanation="X"),
        InteractionRecord(drug_a="B", drug_b="C", severity=SeverityLevel.MODERATE, explanation="Y")
    ]
    
    result = engine.analyze_prescription(["A", "B", "C"], records)
    
    assert "raw_weight" in result
    assert "severity_counts" in result
    assert "dominant_severity_driver" in result
    assert "explanation" in result
    assert result["dominant_severity_driver"] == "severe"
    assert result["severity_counts"]["severe"] == 1
    assert result["severity_counts"]["moderate"] == 1
