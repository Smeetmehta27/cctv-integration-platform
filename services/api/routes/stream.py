import asyncio
import cv2
import numpy as np
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()

async def generate_mock_frames(camera_id: str):
    """
    Generates a continuous MJPEG stream.
    Creates a black frame with the camera ID and current timestamp.
    """
    width, height = 640, 360
    while True:
        # Create a black frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add text
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        text = f"CAM: {camera_id} | {current_time}"
        
        cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SIMULATED LIVE FEED", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Encode to JPEG
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # Yield in multipart/x-mixed-replace format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        # Simulate ~15 FPS
        await asyncio.sleep(1 / 15.0)

@router.get("/simulate-feed/{camera_id}")
async def simulate_feed(camera_id: str):
    """
    Serves a live simulated MJPEG video feed for the specified camera.
    """
    return StreamingResponse(
        generate_mock_frames(camera_id), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
