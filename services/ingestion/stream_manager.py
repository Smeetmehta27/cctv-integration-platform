import httpx
import asyncio
import logging
import os
from services.ingestion.video_reader import RobustVideoReader

logger = logging.getLogger(__name__)

# Fallback to local API if not set
API_URL = os.getenv("API_URL", "http://localhost:8000")

class StreamManager:
    def __init__(self):
        self.active_streams = {} # camera_id -> RobustVideoReader instance
        self.is_running = False

    async def poll_catalogue(self):
        self.is_running = True
        while self.is_running:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{API_URL}/api/ingest")
                    
                    if response.status_code == 200:
                        catalogue = response.json()
                        await self.reconcile_streams(catalogue)
                    else:
                        logger.warning(f"Failed to fetch catalogue: HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"Error connecting to catalogue API: {e}")
            
            await asyncio.sleep(15) # Poll every 15 seconds

    async def reconcile_streams(self, catalogue):
        # We only want cameras marked as ONLINE with a valid RTSP URL
        valid_cameras = {
            cam["id"]: cam 
            for cam in catalogue 
            if cam.get("live_status") == "ONLINE" and cam.get("rtsp_url")
        }
        
        # Stop streams that are no longer in the valid catalogue
        for cam_id in list(self.active_streams.keys()):
            if cam_id not in valid_cameras:
                logger.info(f"Stopping stream {cam_id} - no longer active in catalogue.")
                self.active_streams[cam_id].stop()
                del self.active_streams[cam_id]
                
        # Start new streams
        for cam_id, cam_info in valid_cameras.items():
            if cam_id not in self.active_streams:
                logger.info(f"Starting new stream for {cam_id}")
                reader = RobustVideoReader(camera_id=cam_id, rtsp_url=cam_info["rtsp_url"])
                self.active_streams[cam_id] = reader
                # Run the stream reader in the background
                if not hasattr(self, 'background_tasks'):
                    self.background_tasks = set()
                task = asyncio.create_task(reader.start())
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)

    def stop_all(self):
        self.is_running = False
        for cam_id, reader in self.active_streams.items():
            reader.stop()
        self.active_streams.clear()
