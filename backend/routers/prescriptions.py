from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.db import db
from backend.auth_utils import get_current_user
from datetime import datetime

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

class Prescription(BaseModel):
    patient_email: str
    drugs: list[str]
    notes: str = ""

@router.post("/")
async def create_prescription(data: Prescription, current_user: dict = Depends(get_current_user)):
    doc = data.dict()
    doc["doctor_email"] = current_user.get("email")
    doc["created_at"] = datetime.utcnow()
    res = await db.prescriptions.insert_one(doc)
    return {"message": "Prescription created", "id": str(res.inserted_id)}
