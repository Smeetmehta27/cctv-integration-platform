from pydantic import BaseModel
from typing import Optional, List

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    track_id: Optional[str] = None

class Point(BaseModel):
    x: int
    y: int

class PlateData(BaseModel):
    raw_text: str
    normalized_text: str
    confidence: float

class TrackResult(BaseModel):
    track_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox
    centroid: Point
    image_plane_velocity: float
    plate: Optional[PlateData] = None

class FrameTracks(BaseModel):
    camera_id: str
    timestamp: str
    inference_time_ms: float
    model_name: str
    tracks: List[TrackResult]
