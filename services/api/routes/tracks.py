from fastapi import APIRouter
from typing import Dict, List

router = APIRouter(prefix="/tracks", tags=["tracks"])

# In-memory store for active tracks: {camera_id: {track_id: track_data}}
# In a full production system, this would be backed by Redis or Postgres.
ACTIVE_TRACKS: Dict[str, Dict[int, dict]] = {}

@router.get("/")
async def get_all_active_tracks():
    """Returns all currently active tracks across all cameras."""
    results = []
    for cam_id, tracks in ACTIVE_TRACKS.items():
        for t_id, t_data in tracks.items():
            results.append({
                "camera_id": cam_id,
                **t_data
            })
    return {"status": "success", "tracks": results}

@router.get("/{camera_id}")
async def get_camera_tracks(camera_id: str):
    """Returns active tracks for a specific camera."""
    tracks = ACTIVE_TRACKS.get(camera_id, {})
    return {
        "status": "success", 
        "camera_id": camera_id,
        "tracks": [{"track_id": k, **v} for k, v in tracks.items()]
    }
