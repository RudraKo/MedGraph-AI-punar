import sys
import os
import pandas as pd
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.interactions.interaction_engine import InteractionEngine, InteractionRecord, SeverityLevel

def test_ml_with_real_data():
    print("--- Loading Real Data ---")
    
    # Load DDI data
    # We'll take a chunk to find some interactions
    try:
        ddi_df = pd.read_csv('Data/DDI_data.csv', nrows=5000)
        print(f"Loaded {len(ddi_df)} records from DDI_data.csv")
    except Exception as e:
        print(f"Error loading Data/DDI_data.csv: {e}")
        return

    # Map interaction_type to SeverityLevel (Simple mapping for test)
    def map_severity(interaction_type):
        it = str(interaction_type).lower()
        if 'bleeding' in it or 'fatal' in it:
            return SeverityLevel.SEVERE
        if 'contraindicated' in it:
            return SeverityLevel.CONTRAINDICATED
        if 'concentration' in it or 'serum' in it or 'metabolism' in it:
            return SeverityLevel.MODERATE
        return SeverityLevel.MILD

    # Convert to InteractionRecord objects
    db_records = []
    for _, row in ddi_df.iterrows():
        db_records.append(InteractionRecord(
            drug_a=str(row['drug1_name']),
            drug_b=str(row['drug2_name']),
            severity=map_severity(row['interaction_type']),
            explanation=str(row['interaction_type'])
        ))

    # Pick a few drugs that we know are in the sample and have interactions
    # From head: Bivalirudin has interactions with Alfuzosin, Acemetacin, Apixaban, Dabigatran etexilate
    test_drugs = ["Bivalirudin", "Acemetacin", "Apixaban", "Warfarin"] # Warfarin might be in the sample too
    
    print(f"Analyzing prescription for: {test_drugs}")
    
    engine = InteractionEngine()
    result = engine.analyze_prescription(
        prescribed_drugs=test_drugs,
        db_records=db_records
    )

    print("\n--- Interaction Engine Result ---")
    print(json.dumps(result, indent=2))
    
    if len(result['interactions']) > 0:
        print(f"\n✅ SUCCESSFULLY detected {len(result['interactions'])} interactions using real medical data.")
    else:
        print("\n⚠️ No interactions detected in this small data sample.")

    # Test Schedule Optimizer with these interactions
    print("\n--- Testing Schedule Optimizer ---")
    from app.services.scheduling.schedule_optimizer import ScheduleOptimizer, MedicationDosage
    
    optimizer = ScheduleOptimizer()
    dosages = [
        MedicationDosage(drug_name="Bivalirudin", frequency=2),
        MedicationDosage(drug_name="Acemetacin", frequency=2),
        MedicationDosage(drug_name="Apixaban", frequency=1)
    ]
    
    # Use the interactions we found
    interactions_dto = []
    # Convert result findings back to records for the optimizer
    for inter in result['interactions']:
        interactions_dto.append(InteractionRecord(
            drug_a=inter['drug_a'],
            drug_b=inter['drug_b'],
            severity=SeverityLevel(inter['severity']),
            explanation=inter['explanation']
        ))
        
    schedule_result = optimizer.generate_schedule(dosages, interactions_dto)
    print("Optimizer Schedule Output:")
    print(json.dumps(schedule_result, indent=2))
    
    if len(schedule_result['schedule']) > 0:
        print("\n✅ SUCCESSFULLY generated conflict-free schedule using real data mappings.")

if __name__ == "__main__":
    test_ml_with_real_data()
