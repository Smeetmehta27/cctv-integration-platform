from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services.ai.tracker_manager import RouteReconstructor

router = APIRouter(prefix="/tracking", tags=["tracking"])

HISTORICAL_DETECTIONS = []

class RouteRequest(BaseModel):
    plate_number: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@router.post("/route")
async def get_route(req: RouteRequest):
    return await RouteReconstructor.reconstruct(req.plate_number, HISTORICAL_DETECTIONS)
