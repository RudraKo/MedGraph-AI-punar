from fastapi import APIRouter, Depends
from backend.db import db
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/guardian/{guardian_id}")
async def get_alerts(guardian_id: str, current_user: dict = Depends(get_current_user)):
    return []
