from app.services.interactions.interaction_engine import InteractionEngine, InteractionRecord, SeverityLevel

def test_interaction_engine():
    # 1. Mock DB Records (Usually fetched by SQLAlchemy)
    # These represent the "edges" in our graph
    db_records = [
        InteractionRecord(
            drug_a="ASPIRIN", 
            drug_b="WARFARIN", 
            severity=SeverityLevel.SEVERE, 
            explanation="Increased risk of severe gastrointestinal bleeding."
        ),
        InteractionRecord(
            drug_a="OMEPRAZOLE", 
            drug_b="CITALOPRAM", 
            severity=SeverityLevel.MODERATE, 
            explanation="Omeprazole can increase blood levels of citalopram."
        ),
        InteractionRecord(
            drug_a="SILDENAFIL", 
            drug_b="NITROGLYCERIN", 
            severity=SeverityLevel.CONTRAINDICATED, 
            explanation="Fatal drop in blood pressure."
        )
    ]
    
    # 2. Incoming request representing the current polypharmacy profile
    # The engine will build a subset O(D^2) permutation check across this list
    current_prescriptions = ["Aspirin", "Warfarin", "Omeprazole", "Citalopram"]
    
    # 3. Execution
    print(f"Scanning the following polypharmacy profile: {current_prescriptions} ...\n")
    
    engine = InteractionEngine()
    result = engine.analyze_prescription(
        prescribed_drugs=current_prescriptions,
        db_records=db_records
    )

    import json
    print("API Response Envelope:")
    print(json.dumps(result, indent=2))
    
    # Assertions mapped strictly to math rules
    # Aspirin + Warfarin = Severe (4)
    # Omeprazole + Citalopram = Moderate (2)
    # Total Risk = 6
    assert result["risk_score"] == 6
    assert result["severity_summary"] == "Danger: Critical Polypharmacy Risk"
    assert len(result["interactions"]) == 2
    
    print("\n✅ Deterministic Graph Edge-Traversal completed successfully.")
    print("✅ Strict mathematical scoring mapped perfectly without arbitrary ML.")

if __name__ == "__main__":
    test_interaction_engine()
