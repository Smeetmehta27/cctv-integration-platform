from __future__ import annotations

import os
import time
import logging
import cv2
import numpy as np
from typing import Any, Dict
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class TrackerManager:
    """
    Maintains isolated YOLO + ByteTrack instances per camera to guarantee track IDs
    never cross-contaminate between different video streams.
    """
    def __init__(self):
        self.confidence_threshold = float(os.getenv("AI_CONFIDENCE", "0.15"))
        self.iou_threshold = float(os.getenv("AI_IOU", "0.50"))
        self.imgsz = int(os.getenv("AI_IMGSZ", "320"))
        self.device = os.getenv("AI_DEVICE", "cpu")

        # Resolve the best available weight file once at startup
        self._ai_dir = os.path.dirname(os.path.abspath(__file__))
        self._project_root = os.path.abspath(os.path.join(self._ai_dir, "..", ".."))
        weight_env = os.getenv("AI_WEIGHTS", "itd_yolov8.pt")
        if os.path.isabs(weight_env):
            self.weights = weight_env
        else:
            self.weights = os.path.join(self._ai_dir, weight_env)
            
        logger.info(
            f"TrackerManager config: weights={os.path.basename(self.weights)} "
            f"conf={self.confidence_threshold} iou={self.iou_threshold} "
            f"imgsz={self.imgsz} device={self.device}"
        )

        # camera_id -> YOLO instance
        self.isolated_trackers: Dict[str, YOLO] = {}

        # Keep track of previous centroids for image-plane velocity estimation
        # {camera_id: {track_id: {"centroid": (x,y), "pts": float}}}
        self.previous_states: Dict[str, Dict[int, Dict[str, Any]]] = {}

        # Track whether we've created the OpenCV window
        self._window_initialised = False

        # Cache the latest annotated frames as MJPEG bytes for HTTP proxying
        self.latest_annotated_frames: Dict[str, bytes] = {}

        # Frame counter for periodic diagnostic logging
        self._frame_count = 0


    def _get_or_create_tracker(self, camera_id: str) -> YOLO:
        if camera_id not in self.isolated_trackers:
            logger.info(f"[{camera_id}] Initializing isolated tracking pipeline with {os.path.basename(self.weights)}...")
            model = YOLO(self.weights)
            if self.device != "cpu":
                model.to(self.device)
            self.isolated_trackers[camera_id] = model
            self.previous_states[camera_id] = {}
        return self.isolated_trackers[camera_id]

    def reset_tracker(self, camera_id: str):
        """
        Flushes the tracking state for a specific camera.
        Crucial for looping video feeds (scene cuts) when the PTS resets.
        """
        if camera_id in self.isolated_trackers:
            logger.info(f"[{camera_id}] Scene cut detected! Resetting tracker state.")
            # Delete the instance so it gets recreated completely clean on next frame
            del self.isolated_trackers[camera_id]
        if camera_id in self.previous_states:
            del self.previous_states[camera_id]

    def process_frame(self, camera_id: str, image_np: np.ndarray, pts: float) -> tuple[list[dict[str, Any]], float]:
        """
        Runs tracking on a frame for a specific camera.
        Returns a tuple of (track_results, inference_time_ms).
        """
        model = self._get_or_create_tracker(camera_id)
        
        self._frame_count += 1
        start_time = time.time()

        # Use ByteTrack and persist=True to keep track state
        # No class filter — allows all FGVD fine-grained classes
        results = model.track(
            source=image_np,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            imgsz=self.imgsz,
            device=self.device,
            tracker="bytetrack.yaml",
            persist=True,
            verbose=False,
        )

        inference_time_ms = (time.time() - start_time) * 1000.0

        # --- Diagnostic logging (every 25 frames) ---
        num_boxes = len(results[0].boxes) if len(results) > 0 and results[0].boxes is not None else 0
        if self._frame_count % 25 == 0:
            logger.info(
                f"[TRACKER] frame={self._frame_count} | "
                f"model={os.path.basename(self.weights)} | "
                f"detections={num_boxes} | "
                f"conf≥{self.confidence_threshold} | "
                f"imgsz={self.imgsz} | "
                f"inference={inference_time_ms:.1f}ms"
            )

        # --- Live OpenCV visualiser ---
        if len(results) > 0:
            if not self._window_initialised:
                cv2.namedWindow("VIGILIS AI - Live Tracking", cv2.WINDOW_NORMAL)
                self._window_initialised = True
            annotated_frame = results[0].plot()
            cv2.imshow("VIGILIS AI - Live Tracking", annotated_frame)
            cv2.waitKey(1)  # flush UI buffer without blocking
            
            # Encode frame to JPEG and cache it for the local API MJPEG stream
            success, buffer = cv2.imencode('.jpg', annotated_frame)
            if success:
                self.latest_annotated_frames[camera_id] = buffer.tobytes()
        
        tracks = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            
            # Ultralytics boxes may not have 'id' if tracker hasn't assigned one yet
            if boxes is not None and boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()  # type: ignore[union-attr]
                xyxys = boxes.xyxy.cpu().tolist()  # type: ignore[union-attr]
                confs = boxes.conf.cpu().tolist()  # type: ignore[union-attr]
                clss = boxes.cls.cpu().tolist()  # type: ignore[union-attr]
                
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

import math
from datetime import datetime, timezone
from packages.shared.database import AsyncSessionLocal
from sqlalchemy import text

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class RouteReconstructor:
    @staticmethod
    async def reconstruct(plate_number: str, raw_events: list):
        events = [e for e in raw_events if e['plate_number'] == plate_number]
        if not events:
            return {"summary": {}, "waypoints": []}
            
        for e in events:
            if isinstance(e['timestamp'], str):
                try:
                    e['dt'] = datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00'))
                except:
                    e['dt'] = datetime.now(timezone.utc)
            else:
                e['dt'] = e['timestamp']
                
        events.sort(key=lambda x: x['dt'])
        
        waypoints = []
        current_wp = None
        
        for e in events:
            if current_wp is None:
                current_wp = {
                    "camera_id": e['camera_id'],
                    "entry_time": e['dt'],
                    "exit_time": e['dt'],
                    "snapshot_url": e.get('snapshot_url', ''),
                    "confidence": e.get('confidence', 0.95),
                    "events": 1
                }
            else:
                dt_diff = (e['dt'] - current_wp['exit_time']).total_seconds()
                if e['camera_id'] == current_wp['camera_id'] and dt_diff <= 40:
                    current_wp['exit_time'] = e['dt']
                    current_wp['events'] += 1
                    current_wp['confidence'] = max(current_wp['confidence'], e.get('confidence', 0.95))
                else:
                    waypoints.append(current_wp)
                    current_wp = {
                        "camera_id": e['camera_id'],
                        "entry_time": e['dt'],
                        "exit_time": e['dt'],
                        "snapshot_url": e.get('snapshot_url', ''),
                        "confidence": e.get('confidence', 0.95),
                        "events": 1
                    }
        if current_wp:
            waypoints.append(current_wp)
            
        cam_ids = tuple(set(wp['camera_id'] for wp in waypoints))
        cam_meta = {}
        if cam_ids:
            try:
                async with AsyncSessionLocal() as session:
                    placeholders = ','.join([f"'{cid}'" for cid in cam_ids])
                    q = f"SELECT id, name, ST_Y(location::geometry) as lat, ST_X(location::geometry) as lng, address FROM cameras WHERE id IN ({placeholders})"
                    result = await session.execute(text(q))
                    for r in result.fetchall():
                        cam_meta[str(r[0])] = {
                            "name": r[1],
                            "lat": r[2],
                            "lng": r[3],
                            "address": r[4]
                        }
            except Exception as e:
                logger.error(f"DB Error fetching camera coords: {e}")
                
        total_dist = 0.0
        total_time_hr = 0.0
        
        for i, wp in enumerate(waypoints):
            cid = wp['camera_id']
            meta = cam_meta.get(cid, {})
            wp['camera_name'] = meta.get('name', 'Unknown Camera')
            wp['latitude'] = meta.get('lat', 0.0)
            wp['longitude'] = meta.get('lng', 0.0)
            wp['district'] = meta.get('address', 'Unknown')
            wp['speed_from_prev'] = 0.0
            
            wp['entry_time'] = wp['entry_time'].isoformat()
            wp['exit_time'] = wp['exit_time'].isoformat()
            
            if i > 0:
                prev_wp = waypoints[i-1]
                lat1, lng1 = prev_wp['latitude'], prev_wp['longitude']
                lat2, lng2 = wp['latitude'], wp['longitude']
                if lat1 and lng1 and lat2 and lng2:
                    dist_km = haversine(lat1, lng1, lat2, lng2)
                    total_dist += dist_km
                    
                    prev_dt = datetime.fromisoformat(prev_wp['exit_time'])
                    curr_dt = datetime.fromisoformat(wp['entry_time'])
                    dt_hr = (curr_dt - prev_dt).total_seconds() / 3600.0
                    
                    if dt_hr > 0:
                        speed = dist_km / dt_hr
                        wp['speed_from_prev'] = round(speed, 2)
                        total_time_hr += dt_hr
                        if speed > 150:
                            wp['anomaly'] = "Speed exceeds 150 km/h"
                        elif speed < 0:
                            wp['anomaly'] = "Negative time delta"
                        
        avg_speed = round(total_dist / total_time_hr, 2) if total_time_hr > 0 else 0.0
        
        return {
            "summary": {
                "total_distance_km": round(total_dist, 2),
                "total_transit_time_minutes": round(total_time_hr * 60, 2),
                "cameras_passed_count": len(waypoints),
                "average_speed_kmh": avg_speed
            },
            "waypoints": waypoints
        }
