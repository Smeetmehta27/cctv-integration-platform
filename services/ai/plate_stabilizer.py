from typing import Dict, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class PlateStabilizer:
    """
    Maintains a temporal history of OCR reads for active vehicle tracks.
    A plate is 'stabilized' when the same normalized text is read consistently
    across multiple frames.
    """
    def __init__(self, required_hits=2):
        self.required_hits = required_hits
        # { camera_id: { track_id: { "reads": {"GJ01AB1234": [0.8, 0.9]}, "stable_plate": "GJ01AB1234", "stable_conf": 0.9 } } }
        self.state: Dict[str, Dict[int, dict]] = defaultdict(lambda: defaultdict(self._empty_state))

    def _empty_state(self):
        return {
            "reads": defaultdict(list), # Maps normalized_text -> list of confidences
            "stable_plate": None,
            "stable_conf": 0.0,
            "raw_text": None
        }

    def add_reading(self, camera_id: str, track_id: int, raw_text: str, normalized_text: str, confidence: float) -> Optional[dict]:
        """
        Adds a reading. Returns the stable plate data if one has been locked in or updated, else None.
        """
        track_state = self.state[camera_id][track_id]
        
        # If we already have a stable plate, we don't necessarily need to overwrite it unless
        # we see a vastly better read. For Stage 3.4, we lock onto the first stable read to save CPU.
        # But we still record it.
        track_state["reads"][normalized_text].append(confidence)
        
        # Is this plate now stable?
        hits = len(track_state["reads"][normalized_text])
        if hits >= self.required_hits:
            avg_conf = sum(track_state["reads"][normalized_text]) / hits
            
            # Lock or upgrade the stable plate
            if track_state["stable_plate"] is None or (normalized_text == track_state["stable_plate"] and avg_conf > track_state["stable_conf"]):
                track_state["stable_plate"] = normalized_text
                track_state["stable_conf"] = avg_conf
                track_state["raw_text"] = raw_text
                
                logger.info(f"[{camera_id}] Track #{track_id} locked stable plate: {normalized_text} (conf: {avg_conf:.2f})")
                return {
                    "raw_text": raw_text,
                    "normalized_text": normalized_text,
                    "confidence": round(avg_conf, 3)
                }
                
        return None

    def has_stable_plate(self, camera_id: str, track_id: int) -> bool:
        return self.state[camera_id][track_id]["stable_plate"] is not None

    def get_stable_plate(self, camera_id: str, track_id: int) -> Optional[dict]:
        state = self.state[camera_id][track_id]
        if state["stable_plate"]:
            return {
                "raw_text": state["raw_text"],
                "normalized_text": state["stable_plate"],
                "confidence": round(state["stable_conf"], 3)
            }
        return None

    def cleanup_track(self, camera_id: str, track_id: int):
        if camera_id in self.state and track_id in self.state[camera_id]:
            del self.state[camera_id][track_id]
