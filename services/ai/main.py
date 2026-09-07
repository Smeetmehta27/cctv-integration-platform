import os
import io
import time
import httpx
import logging
import cv2
import numpy as np
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel

from services.ai.tracker_manager import TrackerManager
from services.ai.schemas import FrameTracks
from services.ai.simulator import simulator, router as simulator_router
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tracker_manager = TrackerManager()

# Store last reported states to throttle UPDATE events
# {camera_id: {track_id: {"timestamp": float, "plate_emitted": bool}}}
last_reported_tracks = {}
background_tasks = set()
http_client = None

API_INTERNAL_EVENTS_URL = os.getenv("API_URL", "http://127.0.0.1:8000") + "/api/internal/events/"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(follow_redirects=True)
    logger.info("Initializing AI Tracking Service...")
    from services.ai.ingest_worker import worker
    worker_task = asyncio.create_task(worker.run())
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(title="VIGILIS AI Tracking & ANPR Service", version="1.0.0", lifespan=lifespan)

def dispatch_event(payload: dict):
    task = asyncio.create_task(broadcast_detections(payload))
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

async def broadcast_detections(detections_payload: dict):
    """Fire-and-forget background task to send events to the API."""
    if http_client is None:
        return
    try:
        resp = await http_client.post(API_INTERNAL_EVENTS_URL, json=detections_payload, timeout=2.0)
        if resp.status_code not in (200, 201):
            logger.warning(f"Event broadcast returned HTTP {resp.status_code}")
    except Exception as e:
        logger.error(f"Failed to broadcast detections to API: {type(e).__name__} - {e}")

async def process_frame_logic(camera_id: str, frame: np.ndarray, pts_ms: float, timestamp: str | None = None):
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
        
    try:
        tracks, inference_time_ms = tracker_manager.process_frame(camera_id, frame, pts_ms)
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise e
        
    # 3. Process Event Payloads & Throttle
    if camera_id not in last_reported_tracks:
        last_reported_tracks[camera_id] = {}
        
    current_time = time.time()
    
    for trk in tracks:
        t_id = trk["track_id"]
        stable_plate = trk.get("plate_number")
        
        # Determine if we need to send PLATE_CONFIRMED
        if stable_plate:
            prev_rep = last_reported_tracks[camera_id].get(t_id, {})
            if not prev_rep.get("plate_emitted", False):
                plate_event = {
                    "event_type": "PLATE_CONFIRMED",
                    "camera_id": camera_id,
                    "timestamp": timestamp,
                    "payload": {
                        "track_id": t_id,
                        "plate": stable_plate
                    }
                }
                dispatch_event(plate_event)
                
                if t_id not in last_reported_tracks[camera_id]:
                    last_reported_tracks[camera_id][t_id] = {"timestamp": current_time, "plate_emitted": True}
                else:
                    last_reported_tracks[camera_id][t_id]["plate_emitted"] = True
        
        if t_id not in last_reported_tracks[camera_id]:
            event_type = "TRACK_STARTED"
            last_reported_tracks[camera_id][t_id] = {"timestamp": current_time, "plate_emitted": bool(stable_plate)}
        else:
            event_type = "TRACK_UPDATED"
            
        if event_type == "TRACK_UPDATED":
            last_rep_ts = last_reported_tracks[camera_id][t_id]["timestamp"]
            if (current_time - last_rep_ts) < 1.0:
                continue
                
        last_reported_tracks[camera_id][t_id]["timestamp"] = current_time
        
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
                "plate": stable_plate
            }
        }
        dispatch_event(event_payload)
        
    # TRACK_LOST logic
    active_ids = {trk["track_id"] for trk in tracks}
    lost_ids = []
    for t_id, last_rep in list(last_reported_tracks[camera_id].items()):
        if t_id not in active_ids and (current_time - last_rep["timestamp"]) > 3.0: 
            lost_ids.append(t_id)
            
    for t_id in lost_ids:
        if hasattr(tracker_manager, 'plate_stabilizer'):
            tracker_manager.plate_stabilizer.cleanup_track(camera_id, t_id)
        event_payload = {
            "event_type": "TRACK_LOST",
            "camera_id": camera_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "track_id": t_id
            }
        }
        dispatch_event(event_payload)
        del last_reported_tracks[camera_id][t_id]

    return {
        "status": "processed",
        "tracks_count": len(tracks),
        "inference_time_ms": inference_time_ms
    }

@app.post("/process")
async def process_frame(
    camera_id: str = Form(...),
    timestamp: str = Form(...),
    image: UploadFile = File(...)
):
    """
    HTTP proxy to the process_frame_logic. Retained for backwards compatibility.
    """
    image_bytes = await image.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image payload")

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        pts = dt.timestamp() * 1000.0
    except:
        pts = time.time() * 1000.0

    try:
        result = await process_frame_logic(camera_id, frame, pts, timestamp)
        return result
    except Exception:
        raise HTTPException(status_code=500, detail="Inference failure")

@app.get("/health")
async def health():
    return {
        "status": "ONLINE",
        "active_cameras": len(tracker_manager.isolated_trackers)
    }

from fastapi.responses import StreamingResponse

async def generate_ai_frames(camera_id: str):
    while True:
        frame_bytes = tracker_manager.latest_annotated_frames.get(camera_id)
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        await asyncio.sleep(1 / 15.0)

@app.get("/stream/{camera_id}")
async def ai_stream(camera_id: str):
    return StreamingResponse(
        generate_ai_frames(camera_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

app.include_router(simulator_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
