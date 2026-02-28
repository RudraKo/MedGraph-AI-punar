from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.domain.models.adherence import Base as AdherenceBase, AdherenceStatusStr, GuardianAlert
from app.repositories.adherence_repo import AdherenceRepository
from app.services.adherence.adherence_monitor import AdherenceMonitorService

def test_adherence_monitoring_service():
    # 1. Setup In-Memory SQLite DB for testing purity
    engine = create_engine("sqlite:///:memory:")
    AdherenceBase.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    # 2. Dependency Injection
    repo = AdherenceRepository(db)
    service = AdherenceMonitorService(repo)
    
    patient = "uuid-123"
    
    print("Test Scenario: Simulating sequential adherence events...")
    
    # Event 1: TAKEN
    result1 = service.process_medication_event(patient, "Vitamin C", datetime.now(), AdherenceStatusStr.TAKEN)
    assert result1["consecutive_misses"] == 0
    assert result1["guardian_alert_triggered"] is False
    
    # Event 2: MISSED (1)
    result2 = service.process_medication_event(patient, "Aspirin", datetime.now(), AdherenceStatusStr.MISSED)
    assert result2["consecutive_misses"] == 1
    
    # Event 3: MISSED (2)
    result3 = service.process_medication_event(patient, "Warfarin", datetime.now(), AdherenceStatusStr.MISSED)
    assert result3["consecutive_misses"] == 2
    
    # Event 4: MISSED (3) -> Hits threshold! Should fire alert.
    print(f"\nTriggering 3rd Consecutive Miss...")
    result4 = service.process_medication_event(patient, "Aspirin", datetime.now(), AdherenceStatusStr.MISSED)
    import json
    print(json.dumps(result4, indent=2))
    assert result4["consecutive_misses"] == 3
    assert result4["guardian_alert_triggered"] is True
    
    # Event 5: MISSED (4) -> Still missing. Should NOT fire redundant alert (Debounced)
    print(f"\nTriggering 4th Consecutive Miss (Checking Duplicate Alert Prevention)...")
    result5 = service.process_medication_event(patient, "Vitamin C", datetime.now(), AdherenceStatusStr.MISSED)
    print(json.dumps(result5, indent=2))
    assert result5["consecutive_misses"] == 4
    assert result5["guardian_alert_triggered"] is False
    
    # Event 6: TAKEN -> Should reset the counter to 0!
    print(f"\nTriggering TAKEN state (Should break the miss chain)...")
    result6 = service.process_medication_event(patient, "Aspirin", datetime.now(), AdherenceStatusStr.TAKEN)
    print(json.dumps(result6, indent=2))
    assert result6["consecutive_misses"] == 0
    assert result6["guardian_alert_triggered"] is False
    
    print("\n✅ Service Business Logic tests passed!")
    print("✅ In-Memory SQLite execution proved Repository isolation.")

if __name__ == "__main__":
    test_adherence_monitoring_service()
