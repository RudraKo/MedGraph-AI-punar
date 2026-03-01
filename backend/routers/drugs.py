from fastapi import APIRouter
from backend.db import db

router = APIRouter(prefix="/drugs", tags=["drugs"])

@router.get("/search")
async def search_drugs(q: str):
    regex = {"$regex": q, "$options": "i"}
    docs = await db.drugs.find({"medicine name": regex}).limit(20).to_list(length=20)
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs
