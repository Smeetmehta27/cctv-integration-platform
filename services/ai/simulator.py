import asyncio
import httpx
import logging
import cv2
import numpy as np
import time
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter()

class AsyncSimulator:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.sequence_names = [
            "Ahmedabad SG Highway Toll",
            "Gandhinagar CH-0",
            "Vadodara Express Highway Start",
            "Vadodara Express Highway End",
            "Bharuch Narmada Bridge",
            "Surat Kadodara Checkpost"
        ]
        self.camera_ids = []
        self.current_step = 0
        self.target_plate = "GJ01ER8842"
        self.is_running = False

    async def fetch_cameras(self):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self.api_url}/api/v1/cameras")
                if resp.status_code == 200:
                    cameras = resp.json()
                    name_to_id = {c["name"]: c["id"] for c in cameras}
                    self.camera_ids = [name_to_id[name] for name in self.sequence_names if name in name_to_id]
                    logger.info(f"Simulator mapped {len(self.camera_ids)} sequence cameras out of {len(cameras)} total cameras.")
            except Exception as e:
                logger.error(f"Failed to fetch cameras: {e}")

    async def run(self):
        self.is_running = True
        await asyncio.sleep(2) # Give API time to boot up
        await self.fetch_cameras()
        
        while self.is_running:
            if not self.camera_ids:
                await self.fetch_cameras()
                await asyncio.sleep(5)
                continue
                
            camera_id = self.camera_ids[self.current_step % len(self.camera_ids)]
            self.current_step += 1
            
            # 50% chance to emit the target plate, 50% random plate
            is_target = np.random.rand() > 0.5
            plate = self.target_plate if is_target else f"GJ01XX{np.random.randint(1000,9999)}"
            conf = np.random.uniform(0.88, 0.98)
            
            payload = {
                "event_type": "PLATE_CONFIRMED",
                "camera_id": camera_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "track_id": f"sim_track_{int(time.time())}",
                    "plate": {
                        "raw_text": plate,
                        "normalized_text": plate,
                        "confidence": conf
                    }
                }
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(f"{self.api_url}/api/internal/events", json=payload)
                    logger.info(f"Simulated ANPR {plate} at camera {camera_id} (conf: {conf:.2f})")
                except Exception as e:
                    logger.error(f"Simulator post failed: {e}")
                    
            await asyncio.sleep(5)

simulator = AsyncSimulator()

def generate_frames(camera_id: str):
    """Generates a synthetic MJPEG stream with OpenCV."""
    while True:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Grid overlay for realism
        for i in range(0, 640, 40):
            cv2.line(frame, (i, 0), (i, 480), (20, 20, 20), 1)
        for i in range(0, 480, 40):
            cv2.line(frame, (0, i), (640, i), (20, 20, 20), 1)
            
        cv2.putText(frame, f"CAM: {camera_id[:8]}...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        cv2.putText(frame, f"VIGILIS ENGINE SIMULATION", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"TIME: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw a moving vehicle bounding box
        t = time.time()
        x = int(320 + 200 * np.sin(t * 0.5))
        y = int(240 + 100 * np.cos(t * 0.5))
        
        cv2.rectangle(frame, (x-70, y-40), (x+70, y+40), (0, 255, 0), 2)
        cv2.putText(frame, "VEHICLE 98%", (x-70, y-50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.05) # ~20 FPS

@router.get("/api/v1/stream/simulate-feed/{camera_id}")
async def simulate_feed(camera_id: str):
    return StreamingResponse(generate_frames(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")
