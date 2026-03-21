from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.task_manager import monitor_target

router = APIRouter(prefix="/api/tracking", tags=["tracking"])

class TrackRequest(BaseModel):
    target_id: str
    query: str
    query_type: str
    frequency_hours: int = 24

@router.post("/add")
async def add_to_watchlist(request: TrackRequest):
    # 1. Save to DB (Watchlist collection)
    # 2. Schedule initial background task
    try:
        monitor_target.delay(request.target_id, request.query, request.query_type)
    except Exception as e:
        print(f"[ERROR] Celery/Redis not available for background task: {e}")
    
    return {"status": "tracking_active", "target_id": request.target_id, "note": "Background tasks may be restricted without Redis"}

@router.get("/list")
async def get_watchlist():
    # Mock list
    return [
        {"id": "1", "name": "SANTIAGO BALBUENA", "last_check": "hace 2 horas", "alerts": 0},
        {"id": "2", "name": "OBJETIVO DELTA", "last_check": "hace 10 min", "alerts": 2}
    ]
