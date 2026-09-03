from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/")
async def get_events():
    return [
        {
            "id": "e1", 
            "event_type": "VEHICLE_SIGHTING", 
            "source": "cam-101", 
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {"plate": "GJ01AB1234"}
        }
    ]
