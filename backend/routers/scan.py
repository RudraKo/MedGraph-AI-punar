from fastapi import APIRouter, UploadFile, File, Depends
from backend.db import db
from backend.auth_utils import get_current_user

router = APIRouter(prefix="/scan", tags=["scan"])

@router.post("/upload")
async def upload_scan(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    return {"text": "dummy ocr text"}
