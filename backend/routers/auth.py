from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from backend.db import db
from backend.auth_utils import create_access_token, get_current_user
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class GoogleCallback(BaseModel):
    google_id: str
    email: str
    name: str
    picture: str

class Onboarding(BaseModel):
    role: str

@router.post("/google-callback")
async def google_callback(user_info: GoogleCallback):
    user = await db.users.find_one({"email": user_info.email})
    is_new = False
    if not user:
        is_new = True
        user_dict = user_info.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["role"] = None
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        user = user_dict
    else:
        user["_id"] = str(user["_id"])
        if not user.get("role"):
            is_new = True

    token = create_access_token({"sub": str(user["_id"]), "email": user["email"], "role": user.get("role")})
    user.pop("_id", None)
    return {"token": token, "user": user, "is_new": is_new}

@router.post("/onboarding")
async def onboarding(data: Onboarding, current_user: dict = Depends(get_current_user)):
    email = current_user.get("email")
    await db.users.update_one({"email": email}, {"$set": {"role": data.role}})
    return {"message": "Onboarding complete", "role": data.role}

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({"email": current_user.get("email")})
    if user:
        user["_id"] = str(user["_id"])
    return {"user": user}
