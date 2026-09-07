import cv2
import time
import logging
import asyncio
import httpx
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class RobustVideoReader:
    def __init__(self, camera_id: str, rtsp_url: str):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.cap = None
        self.is_running = False
        self.ai_url = os.getenv("AI_SERVICE_URL", "http://localhost:8002/process")
        self.process_interval_ms = 1000.0 / float(os.getenv("AI_PROCESS_FPS", "3.0"))
        
        # We explicitly enforce TCP transport for stability with AI pipelines
        # and prevent dropping frames over UDP.
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

    async def start(self):
        self.is_running = True
        retry_delay = 2.0          # Start at 2s per hackathon guidelines
        max_retry_delay = 30.0     # Cap at 30s

        while self.is_running:
            logger.info(f"[{self.camera_id}] Connecting to stream: {self.rtsp_url}")
            
            self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            
            if not self.cap.isOpened():
                logger.warning(f"[{self.camera_id}] Failed to open stream. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                continue
            
            logger.info(f"[{self.camera_id}] Stream connected successfully.")
            retry_delay = 2.0  # Reset backoff on successful connection
            
            consecutive_failures = 0
            previous_pts = -1.0            # PTS-based pacing (no wall-clock)
            last_processed_pts = -1.0      # Throttle AI calls by PTS, not time.time()
            
            async with httpx.AsyncClient() as client:
                while self.is_running and self.cap.isOpened():
                    # Guard cap.read() to catch non-fatal decoder warnings
                    # (e.g., missing IDR frames on stream join)
                    try:
                        ret, frame = self.cap.read()
                    except Exception as e:
                        logger.warning(f"[{self.camera_id}] Decoder warning (non-fatal): {e}")
                        await asyncio.sleep(0.05)
                        continue
                    
                    if not ret:
                        consecutive_failures += 1
                        if consecutive_failures > 30:  # Stream died
                            logger.error(f"[{self.camera_id}] Stream read failed repeatedly. Reconnecting...")
                            break
                        await asyncio.sleep(0.1)
                        continue
                    
                    consecutive_failures = 0
                    
                    # Extract Presentation Timestamp (PTS) — all timing from PTS
                    pts_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                    
                    # Detect PTS discontinuity (scene cuts / loop points)
                    if previous_pts >= 0 and pts_ms < previous_pts:
                        logger.warning(
                            f"[{self.camera_id}] PTS discontinuity: "
                            f"{previous_pts:.0f} -> {pts_ms:.0f}ms. "
                            "Treating as scene cut."
                        )
                        last_processed_pts = -1.0  # Allow immediate processing after cut
                    
                    previous_pts = pts_ms
                    
                    # PTS-based frame throttling (replaces wall-clock time.time())
                    pts_since_last = pts_ms - last_processed_pts if last_processed_pts >= 0 else float('inf')
                    if pts_since_last >= self.process_interval_ms:
                        last_processed_pts = pts_ms
                        timestamp = datetime.utcnow().isoformat()
                        
                        # Encode to JPEG
                        success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if success:
                            try:
                                # POST to AI service (timeout=1.0s to drop frames if AI is backlogged)
                                files = {'image': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
                                data = {'camera_id': self.camera_id, 'timestamp': timestamp}
                                
                                response = await client.post(self.ai_url, data=data, files=files, timeout=1.0)
                                if response.status_code == 200:
                                    res_data = response.json()
                                    if res_data.get("detections_count", 0) > 0:
                                        logger.info(f"[{self.camera_id}] AI processed frame in {res_data['inference_time_ms']:.1f}ms. Detections: {res_data['detections_count']}")
                            except Exception as e:
                                logger.warning(f"[{self.camera_id}] AI service unreachable or timeout: {e}")
                    
                    await asyncio.sleep(0.001)  # Yield control
            
            # Cleanup on disconnect
            if self.cap:
                self.cap.release()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
