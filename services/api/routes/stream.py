import os
import asyncio
import httpx
import cv2
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

async def proxy_ai_stream(camera_id: str):
    ai_port = os.getenv("AI_PORT", 8002)
    url = f"http://127.0.0.1:{ai_port}/stream/{camera_id}"
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("GET", url) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
        except Exception:
            pass

@router.get("/hls/{camera_id}/{filename:path}")
async def proxy_hls(camera_id: str, filename: str):
    url = f"https://cctv.corp8.cloud/{camera_id}/{filename}"
    
    cookie = os.getenv("CONTROL_ROOM_COOKIE", "")

    async with httpx.AsyncClient(
        verify=False,
        timeout=httpx.Timeout(30.0, read=None),
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=50),
        headers={"Cookie": cookie}
    ) as client:
        if filename.endswith(".ts"):
            # Stream .ts file chunk by chunk to save memory
            async def stream_segment():
                async with client.stream("GET", url) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            return StreamingResponse(stream_segment(), media_type="video/MP2T")
            
        else:
            # Manifest file
            response = await client.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch HLS content")
                
            content = response.content
            media_type = response.headers.get("Content-Type", "application/vnd.apple.mpegurl")
            
            if filename.endswith(".m3u8"):
                text = content.decode('utf-8')
                new_lines = []
                for line in text.splitlines():
                    if line and not line.startswith("#"):
                        # Extract the segment filename to ensure clean routing
                        segment_filename = line.split('/')[-1]
                        new_lines.append(f"/api/v1/stream/hls/{camera_id}/{segment_filename}")
                    else:
                        new_lines.append(line)
                content = "\n".join(new_lines).encode('utf-8')
                
            return Response(content=content, media_type=media_type)

@router.get("/{camera_id}")
async def get_stream(camera_id: str):
    if camera_id == "cam01":
        # Active inference feed proxy
        return StreamingResponse(proxy_ai_stream(camera_id), media_type="multipart/x-mixed-replace; boundary=frame")
    else:
        raise HTTPException(status_code=404, detail="Use /hls/{camera_id}/index.m3u8 for this camera")

async def generate_mock_frames(camera_id: str):
    width, height = 640, 360
    while True:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        text = f"CAM: {camera_id} | {current_time}"
        
        cv2.putText(frame, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "SIMULATED LIVE FEED", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        success, buffer = cv2.imencode('.jpg', frame)
        if success:
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        await asyncio.sleep(1 / 15.0)

@router.get("/simulate-feed/{camera_id}")
async def simulate_feed(camera_id: str):
    return StreamingResponse(
        generate_mock_frames(camera_id), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
