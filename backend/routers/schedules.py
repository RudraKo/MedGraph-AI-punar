from fastapi import APIRouter, Depends
from backend.db import db
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/today/{patient_id}")
async def get_today_schedule(patient_id: str, current_user: dict = Depends(get_current_user)):
    return []

@router.patch("/{schedule_id}/status")
async def update_status(schedule_id: str, status: str, current_user: dict = Depends(get_current_user)):
    return {"message": "Updated"}
