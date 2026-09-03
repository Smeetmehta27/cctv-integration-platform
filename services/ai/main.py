import os
import io
import time
import httpx
import logging
import cv2
import numpy as np
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel

from services.ai.tracker_manager import TrackerManager
from services.ai.anpr_manager import ANPRManager
from services.ai.plate_stabilizer import PlateStabilizer
from services.ai.schemas import FrameTracks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VIGILIS AI Tracking & ANPR Service", version="1.0.0")

tracker_manager = TrackerManager()
anpr_manager = ANPRManager()
plate_stabilizer = PlateStabilizer(required_hits=2)

# Store last reported states to throttle UPDATE events
# {camera_id: {track_id: timestamp}}
last_reported_tracks = {}

API_INTERNAL_EVENTS_URL = os.getenv("API_URL", "http://localhost:8000") + "/api/internal/events"

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AI Tracking Service...")
    # Trackers initialize lazily per camera

async def broadcast_detections(detections_payload: dict):
    """Fire-and-forget background task to send events to the API."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(API_INTERNAL_EVENTS_URL, json=detections_payload, timeout=2.0)
    except Exception as e:
        logger.error(f"Failed to broadcast detections to API: {e}")

@app.post("/process")
async def process_frame(
    background_tasks: BackgroundTasks,
    camera_id: str = Form(...),
    timestamp: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Receives a JPEG frame from Ingestion, runs inference, and broadcasts results.
    """
    # 1. Read and decode image
    image_bytes = await image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image payload")

    # 2. Run Tracking Inference
    try:
        # Convert timestamp to a PTS-like float for velocity calculation
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            pts = dt.timestamp() * 1000.0
        except:
            pts = time.time() * 1000.0
            
        tracks, inference_time_ms = tracker_manager.process_frame(camera_id, frame, pts)
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="Inference failure")
        
    # 3. Process ANPR and Create Event Payloads & Throttle
    if camera_id not in last_reported_tracks:
        last_reported_tracks[camera_id] = {}
        
    current_time = time.time()
    
    for trk in tracks:
        t_id = trk["track_id"]
        bbox = trk["bbox"]
        
        # ANPR Logic: Only process if it's a vehicle (not person) and no stable plate yet
        if trk["class_name"] in ["car", "truck", "bus", "motorcycle"] and not plate_stabilizer.has_stable_plate(camera_id, t_id):
            # Crop vehicle ROI
            crop = frame[bbox["y1"]:bbox["y2"], bbox["x1"]:bbox["x2"]]
            
            # Read Plate
            plate_result = anpr_manager.read_plate(crop)
            if plate_result:
                raw, norm, conf = plate_result
                # Feed to stabilizer
                stable = plate_stabilizer.add_reading(camera_id, t_id, raw, norm, conf)
                
                # If newly stabilized, send PLATE_CONFIRMED event immediately
                if stable:
                    plate_event = {
                        "event_type": "PLATE_CONFIRMED",
                        "camera_id": camera_id,
                        "timestamp": timestamp,
                        "payload": {
                            "track_id": t_id,
                            "plate": stable
                        }
                    }
                    background_tasks.add_task(broadcast_detections, plate_event)
        
        # Attach stable plate to track if it exists
        trk["plate"] = plate_stabilizer.get_stable_plate(camera_id, t_id)
        
        # Determine Event Type
        if t_id not in last_reported_tracks[camera_id]:
            event_type = "TRACK_STARTED"
        else:
            event_type = "TRACK_UPDATED"
            
        # Throttling logic for TRACK_UPDATED
        if event_type == "TRACK_UPDATED":
            last_reported = last_reported_tracks[camera_id][t_id]
            # Throttle to 1 update per second per track
            if (current_time - last_reported) < 1.0:
                continue
                
        # Send event
        last_reported_tracks[camera_id][t_id] = current_time
        
        event_payload = {
            "event_type": event_type,
            "camera_id": camera_id,
            "timestamp": timestamp,
            "payload": {
                "track_id": t_id,
                "class_name": trk["class_name"],
                "confidence": trk["confidence"],
                "bbox": trk["bbox"],
                "centroid": trk["centroid"],
                "image_plane_velocity": trk["image_plane_velocity"],
                "plate": trk.get("plate")
            }
        }
        background_tasks.add_task(broadcast_detections, event_payload)
        
    # TRACK_LOST logic (simple timeout for prototype)
    active_ids = {trk["track_id"] for trk in tracks}
    lost_ids = []
    for t_id, last_rep in list(last_reported_tracks[camera_id].items()):
        if t_id not in active_ids and (current_time - last_rep) > 3.0: # 3 sec timeout
            lost_ids.append(t_id)
            
    for t_id in lost_ids:
        plate_stabilizer.cleanup_track(camera_id, t_id)
        event_payload = {
            "event_type": "TRACK_LOST",
            "camera_id": camera_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "track_id": t_id
            }
        }
        background_tasks.add_task(broadcast_detections, event_payload)
        del last_reported_tracks[camera_id][t_id]

    return {
        "status": "processed",
        "tracks_count": len(tracks),
        "inference_time_ms": inference_time_ms
    }

@app.get("/health")
async def health():
    return {
        "status": "ONLINE",
        "active_cameras": len(tracker_manager.isolated_trackers)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
