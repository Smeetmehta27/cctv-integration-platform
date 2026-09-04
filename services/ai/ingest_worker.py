import os
import asyncio
import logging
import time
import httpx

# Force FFMPEG TCP Transport (Must be before cv2 import)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2
import numpy as np
import urllib.parse
from services.ai.main import process_frame_logic, tracker_manager

logger = logging.getLogger(__name__)

class IngestWorker:
    def __init__(self):
        self.gateway_url = os.getenv("HACKATHON_GATEWAY_URL", "http://localhost:8000")
        self.tasks = []

    async def fetch_catalogue(self):
        """Fetches the active camera catalogue from the ingest API."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.gateway_url}/api/ingest", follow_redirects=True, timeout=5.0)
                if resp.status_code == 200:
                    return resp.json()
                logger.error(f"Failed to fetch catalogue: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Catalogue fetch failed: {e}")
        return []

    async def capture_loop(self, camera: dict):
        """
        Connects to a single RTSP stream, reads frames, handles PTS and backoff,
        and pushes to the AI pipeline.
        """
        camera_id = camera.get("id")
        rtsp_url = camera.get("rtsp_url")
        
        email = os.getenv("CONTROL_ROOM_EMAIL")
        password = os.getenv("CONTROL_ROOM_PASSWORD")
        host = os.getenv("CONTROL_ROOM_HOST", "103.250.160.189")
        
        if email and password and camera_id:
            encoded_email = urllib.parse.quote(email)
            rtsp_url = f"rtsp://{encoded_email}:{password}@{host}:8554/stream/{camera_id}"
        
        if not camera_id or not rtsp_url:
            logger.warning("Camera missing ID or RTSP URL, skipping.")
            return

        logger.info(f"[{camera_id}] Starting capture loop for {rtsp_url}")
        
        backoff = 2.0
        max_backoff = 30.0
        
        while True:
            logger.info(f"[{camera_id}] Connecting via FFMPEG/TCP...")
            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            
            if not cap.isOpened():
                logger.error(f"[{camera_id}] Connection failed. Retrying in {backoff}s...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5, max_backoff)
                continue
                
            # Connected successfully!
            backoff = 2.0 
            previous_pts = -1.0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"[{camera_id}] Stream disconnected or EOF.")
                    break
                    
                # Extract Presentation Timestamp (PTS)
                pts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                
                # Detect Scene Cut (looping video restarted)
                if pts_ms < previous_pts:
                    logger.warning(f"[{camera_id}] PTS dropped from {previous_pts} to {pts_ms}. Scene cut detected.")
                    tracker_manager.reset_tracker(camera_id)
                
                previous_pts = pts_ms
                
                # Dynamic Resolution Handling (Standardize to 640x640 for inference)
                # Note: YOLOv8 usually handles resizing internally, but resizing early 
                # normalizes the grid's mixed resolutions and speeds up OpenCV memory transfers.
                resized = cv2.resize(frame, (640, 640))
                
                # Pass to pipeline
                try:
                    await process_frame_logic(camera_id, resized, pts_ms)
                except Exception as e:
                    logger.error(f"[{camera_id}] Inference crash: {e}")
                
                # Yield to event loop to allow other cameras to process
                await asyncio.sleep(0.001)

            cap.release()
            
            # If we break out of inner loop, we wait before reconnecting
            await asyncio.sleep(backoff)
            backoff = min(backoff * 1.5, max_backoff)

    async def run(self):
        """Main entry point: fetches catalogue and spins up capture tasks."""
        logger.info("IngestWorker starting...")
        
        # Initial wait to let the API boot
        await asyncio.sleep(2)
        
        catalogue = await self.fetch_catalogue()
        
        if not catalogue:
            logger.warning("Catalogue empty. Check connection to gateway. (Will not retry for prototype simplicity)")
        
        for cam in catalogue:
            # Only connect to ONLINE cameras that have an RTSP URL
            if cam.get("status") == "ONLINE" and cam.get("rtsp_url"):
                task = asyncio.create_task(self.capture_loop(cam))
                self.tasks.append(task)
                
        if self.tasks:
            await asyncio.gather(*self.tasks)

worker = IngestWorker()
