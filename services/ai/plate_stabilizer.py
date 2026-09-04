from typing import Dict, Optional
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class PlateStabilizer:
    """
    Maintains a sliding window of OCR reads for active vehicle tracks.
    A plate is 'stabilized' when the same normalized text wins the majority vote
    across the last N frames.
    """
    def __init__(self, window_size=10, required_hits=4):
        self.window_size = window_size
        self.required_hits = required_hits
        # { camera_id: { track_id: { "reads": deque, "stable_plate": "GJ01AB1234", "stable_conf": 0.9, "raw_text": "..." } } }
        self.state: Dict[str, Dict[int, dict]] = defaultdict(lambda: defaultdict(self._empty_state))

    def _empty_state(self):
        return {
            "reads": deque(maxlen=self.window_size), # stores tuples (normalized_text, raw_text, confidence)
            "stable_plate": None,
            "stable_conf": 0.0,
            "raw_text": None
        }

    def add_reading(self, camera_id: str, track_id: int, raw_text: str, normalized_text: str, confidence: float) -> Optional[dict]:
        """
        Adds a reading. Returns the stable plate data if one has been locked in or updated, else None.
        """
        track_state = self.state[camera_id][track_id]
        
        # Add to sliding window
        track_state["reads"].append((normalized_text, raw_text, confidence))
        
        # Tally votes in the window
        vote_counts = defaultdict(int)
        conf_sums = defaultdict(float)
        
        for n_text, r_text, conf in track_state["reads"]:
            vote_counts[n_text] += 1
            conf_sums[n_text] += conf
            
        # Find majority vote
        best_plate = None
        best_votes = 0
        for p, v in vote_counts.items():
            if v > best_votes:
                best_votes = v
                best_plate = p
                
        # Is it stable?
        if best_votes >= self.required_hits:
            avg_conf = conf_sums[best_plate] / best_votes
            
            # Lock or upgrade the stable plate
            # We allow upgrading if we get a substantially better read confidence
            is_new_lock = track_state["stable_plate"] is None
            is_upgrade = not is_new_lock and best_plate == track_state["stable_plate"] and avg_conf > track_state["stable_conf"] + 0.05
            
            if is_new_lock or is_upgrade:
                track_state["stable_plate"] = best_plate
                track_state["stable_conf"] = avg_conf
                track_state["raw_text"] = raw_text
                
                logger.info(f"[{camera_id}] Track #{track_id} stabilized plate: {best_plate} (conf: {avg_conf:.2f}, votes: {best_votes})")
                return {
                    "raw_text": raw_text,
                    "normalized_text": best_plate,
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
