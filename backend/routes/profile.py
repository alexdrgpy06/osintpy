from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ai.processor import AIProcessor
from services.identity_resolver import IdentityResolver

router = APIRouter(prefix="/api/profile", tags=["profile"])
ai_processor = AIProcessor()

class ProfileUpdate(BaseModel):
    name: str
    data: dict

@router.get("/{profile_id}")
async def get_profile(profile_id: str):
    # Mock retrieval from MongoDB
    return {
        "id": profile_id,
        "full_name": "SANTIAGO BALBUENA",
        "ci": "4567890",
        "status": "Active"
    }

@router.post("/{profile_id}/summarize")
async def summarize_profile(profile_id: str, data: dict):
    summary = await ai_processor.summarize_person(profile_id, data)
    return {"summary": summary}

@router.post("/resolve")
async def resolve_identity(gov_data: List[dict], osint_data: List[dict]):
    profile = IdentityResolver.merge_profiles(gov_data, osint_data)
    return profile
