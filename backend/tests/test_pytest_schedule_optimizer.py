import pytest
from app.services.scheduling.schedule_optimizer import ScheduleOptimizer, MedicationDosage
from app.services.interactions.interaction_engine import InteractionRecord, SeverityLevel

@pytest.fixture
def mock_interactions():
    return [
        InteractionRecord(drug_a="ASPIRIN", drug_b="WARFARIN", severity=SeverityLevel.SEVERE, explanation="High bleed risk"),
        InteractionRecord(drug_a="OMEPRAZOLE", drug_b="WARFARIN", severity=SeverityLevel.MODERATE, explanation="Metabolite interaction")
    ]

@pytest.fixture
def optimizer():
    return ScheduleOptimizer()

def test_no_interactions_scheduling(optimizer):
    dosages = [
        MedicationDosage(drug_name="PARACETAMOL", frequency=2),
        MedicationDosage(drug_name="AMOXICILLIN", frequency=1)
    ]
    result = optimizer.generate_schedule(dosages, [])
    
    schedule = result["schedule"]
    assert len(schedule) > 0
    # First slot should place both drugs to get them out of the way
    assert "PARACETAMOL" in schedule[0]["medications"]
    assert "AMOXICILLIN" in schedule[0]["medications"]
    
    # Verify spread - Paracetamol should be taken twice, separated by at least 4 hours
    paracetamol_times = []
    for slot in schedule:
        if "PARACETAMOL" in slot["medications"]:
            paracetamol_times.append(int(slot["time"].split(":")[0]))
            
    assert len(paracetamol_times) == 2
    assert abs(paracetamol_times[1] - paracetamol_times[0]) >= 4

def test_severe_interactions_separation(optimizer, mock_interactions):
    dosages = [
        MedicationDosage(drug_name="ASPIRIN", frequency=1),
        MedicationDosage(drug_name="WARFARIN", frequency=1)
    ]
    result = optimizer.generate_schedule(dosages, mock_interactions)
    
    schedule = result["schedule"]
    aspirin_time = None
    warfarin_time = None
    
    for slot in schedule:
        if "ASPIRIN" in slot["medications"]:
            aspirin_time = int(slot["time"].split(":")[0])
        if "WARFARIN" in slot["medications"]:
            warfarin_time = int(slot["time"].split(":")[0])
            
    assert aspirin_time is not None
    assert warfarin_time is not None
    assert abs(aspirin_time - warfarin_time) >= 4  # Severe interaction requires >= 4 hours

def test_empty_medications(optimizer, mock_interactions):
    result = optimizer.generate_schedule([], mock_interactions)
    
    assert len(result["schedule"]) == 0
    assert "WARNING" not in result["notes"]

def test_impossible_constraints_fail_gracefully(optimizer):
    # Try to schedule 5 overlapping doses of the exact same drug
    # The system only has 8 slots, and forces a 4 hour gap between identical drugs
    # 08:00, 12:00, 16:00, 20:00 -> Max 4 doses in a 16 hour window
    dosages = [
        MedicationDosage(drug_name="IBUPROFEN", frequency=5)
    ]
    
    result = optimizer.generate_schedule(dosages, [])
    
    # Output should contain a warning note about failing to schedule the 5th pill
    assert "WARNING: Insufficient safe time slots" in result["notes"]
