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

# Resolve the demo video path relative to the project root
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEMO_VIDEO_PATH = os.path.join(_PROJECT_ROOT, "demo_traffic.mp4")

# Simulation camera ID used when ingesting the demo video
SIM_CAMERA_ID = "SIM_DEMO_TRAFFIC"


class IngestWorker:
    def __init__(self):
        self.api_host = os.getenv("CONTROL_ROOM_API_HOST", "cctv.corp8.cloud")
        self.stream_host = os.getenv("CONTROL_ROOM_STREAM_HOST", "103.250.160.189")
        self.email = os.getenv("CONTROL_ROOM_EMAIL")
        self.password = os.getenv("CONTROL_ROOM_PASSWORD")
        
        self.enable_simulation = os.getenv("ENABLE_SIMULATION", "false").lower() == "true"
        self.max_active_streams = int(os.getenv("MAX_ACTIVE_STREAMS", "1"))
        self.default_camera_id = os.getenv("DEFAULT_CAMERA_ID", "1")
        self.tasks = []

    # ------------------------------------------------------------------
    # Simulation: read real frames from demo_traffic.mp4
    # ------------------------------------------------------------------

    async def _simulation_capture_loop(self):
        """
        Reads frames from the local demo_traffic.mp4 file and feeds them
        through the full ANPR / YOLO pipeline.  Loops the video infinitely
        by resetting to frame 0 on EOF.
        """
        camera_id = SIM_CAMERA_ID
        logger.info(f"[{camera_id}] Opening local video: {DEMO_VIDEO_PATH}")

        try:
            cap = cv2.VideoCapture(DEMO_VIDEO_PATH)
            if not cap.isOpened():
                raise IOError(f"cv2.VideoCapture failed to open {DEMO_VIDEO_PATH}")
        except Exception as e:
            logger.warning(
                f"[{camera_id}] Could not open demo video ({e}). "
                "Falling back to mock event simulator."
            )
            await self._fallback_to_mock_simulator()
            return

        previous_pts = -1.0

        logger.info(
            f"[{camera_id}] Video opened — "
            f"{int(cap.get(cv2.CAP_PROP_FRAME_COUNT))} frames"
        )

        try:
            while True:
                ret, frame = cap.read()

                # ---- infinite-loop: reset on EOF ----
                if not ret or frame is None:
                    logger.info(f"[{camera_id}] Video EOF — rewinding to start.")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    tracker_manager.reset_tracker(camera_id)
                    previous_pts = -1.0
                    continue

                # PTS handling — all timing derived from PTS, never CAP_PROP_FPS
                pts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

                # Detect scene cuts / loop points via PTS discontinuity
                if pts_ms < previous_pts:
                    logger.warning(
                        f"[{camera_id}] PTS dropped {previous_pts:.0f} → {pts_ms:.0f}. "
                        "Scene cut detected."
                    )
                    tracker_manager.reset_tracker(camera_id)

                # Adaptive pacing: use PTS delta to sleep the correct duration
                if previous_pts >= 0 and pts_ms > previous_pts:
                    pts_delta_sec = (pts_ms - previous_pts) / 1000.0
                    # Clamp to avoid stalling on large gaps (variable framerate resilience)
                    await asyncio.sleep(min(pts_delta_sec, 0.5))
                else:
                    # First frame or discontinuity — minimal yield
                    await asyncio.sleep(0.001)

                previous_pts = pts_ms

                # Standardize to 640×640 for inference
                resized = cv2.resize(frame, (640, 640))

                try:
                    await process_frame_logic(camera_id, resized, pts_ms)
                except Exception as e:
                    logger.error(f"[{camera_id}] Inference crash: {e}")
        finally:
            cap.release()
            logger.info(f"[{camera_id}] Video capture released.")

    async def _fallback_to_mock_simulator(self):
        """Falls back to the existing mock event simulator (simulator.py)."""
        from services.ai.simulator import simulator
        logger.info("Starting mock event simulator as fallback…")
        await simulator.run()

    # ------------------------------------------------------------------
    # Production: RTSP capture (unchanged)
    # ------------------------------------------------------------------

    async def fetch_catalogue(self):
        """Fetches the active camera catalogue from a local catalogue.json file."""
        import json
        catalogue_path = os.path.join(_PROJECT_ROOT, "catalogue.json")
        try:
            with open(catalogue_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Successfully loaded catalogue from {catalogue_path}")
                return data
        except FileNotFoundError:
            logger.error(f"Critical: catalogue.json not found at {catalogue_path}. Please download it manually and place it in the project root.")
        except json.JSONDecodeError as e:
            logger.error(f"Critical: Failed to parse catalogue.json: {e}")
        except Exception as e:
            logger.error(f"Critical: Failed to read catalogue.json: {e}")
        
        return []

    async def capture_loop(self, camera: dict):
        """
        Connects to a single RTSP stream, reads frames, handles PTS and backoff,
        and pushes to the AI pipeline.
        """
        camera_id = str(camera.get("id"))
        
        # Use provided RTSP URL or construct based on stream host
        rtsp_url = camera.get("rtsp_url")
        if not rtsp_url:
            rtsp_url = f"rtsp://{self.stream_host}:8554/stream/{camera_id}"
        else:
            # Ensure the hostname defaults to stream_host before injecting credentials
            parsed = urllib.parse.urlparse(rtsp_url)
            port = parsed.port if parsed.port else 8554
            rtsp_url = f"rtsp://{self.stream_host}:{port}{parsed.path}"
            
        # Inject authentication credentials
        if self.email and self.password and rtsp_url.startswith("rtsp://"):
            # Ensure we only inject if credentials aren't already present
            if "@" not in rtsp_url.replace("rtsp://", ""):
                encoded_email = urllib.parse.quote(self.email, safe='')
                encoded_password = urllib.parse.quote(self.password, safe='')
                rtsp_url = rtsp_url.replace("rtsp://", f"rtsp://{encoded_email}:{encoded_password}@")
        
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

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self):
        """Main entry point: routes to simulation or production RTSP mode."""
        logger.info("IngestWorker starting...")
        
        # Initial wait to let the API boot
        await asyncio.sleep(2)

        # ---- Simulation mode: ingest demo_traffic.mp4 ----
        if self.enable_simulation:
            logger.info(
                "ENABLE_SIMULATION=true — ingesting demo_traffic.mp4 "
                "instead of RTSP catalogue."
            )
            await self._simulation_capture_loop()
            return

        # ---- Production mode: RTSP catalogue ----
        catalogue = await self.fetch_catalogue()
        
        if not catalogue:
            logger.warning("Catalogue empty. Check connection to gateway. (Will not retry for prototype simplicity)")
        
        live_cameras = []
        for cam in catalogue:
            status = cam.get("status", "").lower()
            if status in ("live", "active", "online"):
                live_cameras.append(cam)
                
        # Prioritize default camera
        live_cameras.sort(key=lambda c: 0 if str(c.get("id")) == self.default_camera_id else 1)
        
        # Limit by max active streams
        selected_cameras = live_cameras[:self.max_active_streams]
        
        for cam in selected_cameras:
            task = asyncio.create_task(self.capture_loop(cam))
            self.tasks.append(task)
                
        if self.tasks:
            await asyncio.gather(*self.tasks)

worker = IngestWorker()

