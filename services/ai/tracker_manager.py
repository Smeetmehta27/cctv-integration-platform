import os
import time
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class TrackerManager:
    """
    Maintains isolated YOLO + ByteTrack instances per camera to guarantee track IDs
    never cross-contaminate between different video streams.
    """
    def __init__(self):
        self.model_name = os.getenv("AI_MODEL", "yolov8n.pt")
        self.confidence_threshold = float(os.getenv("AI_CONFIDENCE", "0.4"))
        self.device = os.getenv("AI_DEVICE", "cpu")
        
        # camera_id -> YOLO instance
        self.isolated_trackers: Dict[str, YOLO] = {}
        
        # Keep track of previous centroids for image-plane velocity estimation
        # {camera_id: {track_id: {"centroid": (x,y), "pts": float}}}
        self.previous_states: Dict[str, Dict[int, Dict[str, Any]]] = {}
        
        self.target_classes = {0, 1, 2, 3, 5, 7} # person, bicycle, car, motorcycle, bus, truck

    def _get_or_create_tracker(self, camera_id: str) -> YOLO:
        if camera_id not in self.isolated_trackers:
            logger.info(f"[{camera_id}] Initializing isolated tracking pipeline...")
            model = YOLO(self.model_name)
            if self.device != "cpu":
                model.to(self.device)
            self.isolated_trackers[camera_id] = model
            self.previous_states[camera_id] = {}
        return self.isolated_trackers[camera_id]

    def process_frame(self, camera_id: str, image_np: np.ndarray, pts: float) -> Tuple[List[Dict[str, Any]], float]:
        """
        Runs tracking on a frame for a specific camera.
        Returns a tuple of (track_results, inference_time_ms).
        """
        model = self._get_or_create_tracker(camera_id)
        
        start_time = time.time()
        
        # Use ByteTrack and persist=True to keep track state
        results = model.track(
            source=image_np,
            conf=self.confidence_threshold,
            device=self.device,
            classes=list(self.target_classes),
            tracker="bytetrack.yaml",
            persist=True,
            verbose=False
        )
        
        inference_time_ms = (time.time() - start_time) * 1000.0
        
        tracks = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            # Ultralytics boxes may not have 'id' if tracker hasn't assigned one yet
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxys = boxes.xyxy.cpu().tolist()
                confs = boxes.conf.cpu().tolist()
                clss = boxes.cls.cpu().tolist()
                
                for t_id, xyxy, conf, cls in zip(track_ids, xyxys, confs, clss):
                    x1, y1, x2, y2 = map(int, xyxy)
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    class_name = model.names[int(cls)]
                    
                    # Calculate basic image-plane velocity (pixels per second)
                    velocity = 0.0
                    prev_state = self.previous_states[camera_id].get(t_id)
                    if prev_state and pts > prev_state["pts"]:
                        px, py = prev_state["centroid"]
                        dt_sec = (pts - prev_state["pts"]) / 1000.0
                        if dt_sec > 0:
                            dist = np.sqrt((cx - px)**2 + (cy - py)**2)
                            velocity = round(dist / dt_sec, 2)
                    
                    # Update state
                    self.previous_states[camera_id][t_id] = {
                        "centroid": (cx, cy),
                        "pts": pts
                    }
                    
                    tracks.append({
                        "track_id": t_id,
                        "class_name": class_name,
                        "confidence": round(conf, 3),
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                        "centroid": {"x": cx, "y": cy},
                        "image_plane_velocity": velocity
                    })
                    
        return tracks, inference_time_ms
