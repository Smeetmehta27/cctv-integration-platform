from fastapi import APIRouter, Body, Depends
from services.api.websockets.manager import manager
import json
from services.api.routes.tracks import ACTIVE_TRACKS
from packages.shared.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.core.alert_engine import alert_engine

router = APIRouter(prefix="/internal/events", tags=["internal"])

@router.post("/")
async def broadcast_internal_event(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Receives an event from an internal service (like AI or Ingestion)
    and broadcasts it directly to all connected WebSocket clients.
    """
    # The payload is assumed to be a fully formed event envelope.
    event_json = json.dumps(payload)
    await manager.broadcast(event_json)
    
    # Update in-memory track state if tracking events
    event_type = payload.get("event_type")
    camera_id = payload.get("camera_id")
    event_data = payload.get("payload", {})
    
    if camera_id and event_type in ["TRACK_STARTED", "TRACK_UPDATED"]:
        track_id = event_data.get("track_id")
        if track_id is not None:
            if camera_id not in ACTIVE_TRACKS:
                ACTIVE_TRACKS[camera_id] = {}
            # Update the latest observation for this track
            ACTIVE_TRACKS[camera_id][track_id] = event_data
            
    elif camera_id and event_type == "PLATE_CONFIRMED":
        track_id = event_data.get("track_id")
        plate_data = event_data.get("plate")
        if track_id is not None and camera_id in ACTIVE_TRACKS:
            if track_id in ACTIVE_TRACKS[camera_id]:
                ACTIVE_TRACKS[camera_id][track_id]["plate"] = plate_data
                
        # Forward to Alert Engine for Watchlist matching
        await alert_engine.process_plate_event(payload, db)
            
    elif camera_id and event_type == "TRACK_LOST":
        track_id = event_data.get("track_id")
        if track_id is not None and camera_id in ACTIVE_TRACKS:
            if track_id in ACTIVE_TRACKS[camera_id]:
                del ACTIVE_TRACKS[camera_id][track_id]
                
    # Normally we would persist this event to the DB here as well
    return {"status": "broadcasted"}
