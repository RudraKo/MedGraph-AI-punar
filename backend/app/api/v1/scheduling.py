from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.scheduling.schedule_optimizer import ScheduleOptimizer, MedicationDosage
from app.services.interactions.interaction_engine import InteractionRecord, SeverityLevel

router = APIRouter(
    prefix="/schedule",
    tags=["Scheduling Optimization"]
)

class ScheduleRequest(BaseModel):
    dosages: List[MedicationDosage]

# --- Dependency Providers ---
def get_schedule_optimizer() -> ScheduleOptimizer:
    return ScheduleOptimizer()

def get_interaction_records() -> List[InteractionRecord]:
    # Placeholder for SQLite db fetch
    return [
        InteractionRecord(drug_a="ASPIRIN", drug_b="WARFARIN", severity=SeverityLevel.SEVERE, explanation="Increased bleeding risk.")
    ]
# ----------------------------

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def generate_schedule(
    request: ScheduleRequest,
    optimizer: ScheduleOptimizer = Depends(get_schedule_optimizer),
    db_records: List[InteractionRecord] = Depends(get_interaction_records)
):
    if not request.dosages:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Dosage list cannot be empty."
         )
         
    try:
        raw_result = optimizer.generate_schedule(request.dosages, db_records)
        return {
            "success": True,
            "data": raw_result,
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schedule optimization failure: {str(e)}"
        )
