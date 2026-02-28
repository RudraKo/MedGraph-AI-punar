from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.interactions.interaction_engine import InteractionEngine, InteractionRecord, SeverityLevel

router = APIRouter(
    prefix="/check-interactions",
    tags=["Interaction Engine"]
)

class PrescriptionsRequest(BaseModel):
    prescribed_drugs: List[str]

# --- Dependency Providers ---
def get_interaction_engine() -> InteractionEngine:
    return InteractionEngine()

def get_interaction_records() -> List[InteractionRecord]:
    # Placeholder for SQLite db fetch
    return [
        InteractionRecord(drug_a="ASPIRIN", drug_b="WARFARIN", severity=SeverityLevel.SEVERE, explanation="Increased bleeding risk."),
        InteractionRecord(drug_a="OMEPRAZOLE", drug_b="WARFARIN", severity=SeverityLevel.MODERATE, explanation="Altered metabolism.")
    ]
# ----------------------------

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def check_interactions(
    request: PrescriptionsRequest,
    engine: InteractionEngine = Depends(get_interaction_engine),
    db_records: List[InteractionRecord] = Depends(get_interaction_records)
):
    if not request.prescribed_drugs:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Medication list cannot be empty."
         )
         
    try:
        raw_result = engine.analyze_prescription(request.prescribed_drugs, db_records)
        return {
            "success": True,
            "data": raw_result,
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interaction engine failure: {str(e)}"
        )
