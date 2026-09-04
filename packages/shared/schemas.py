from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class CameraBase(BaseModel):
    name: str
    location: Optional[Dict[str, Any]] = None
    address: Optional[str] = None
    protocol: Optional[str] = None
    url: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    codec: Optional[str] = None
    status: str = 'OFFLINE'
    is_active: bool = True
    edge_node_cpu: Optional[float] = None
    edge_node_gpu: Optional[float] = None
    stream_errors: Optional[int] = 0

class CameraHealthSummary(BaseModel):
    total_cameras: int
    online: int
    offline: int
    degraded: int
    stream_errors: int
    avg_edge_node_cpu: float
    avg_edge_node_gpu: float

class CameraResponse(CameraBase):
    id: UUID
    department_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class EventBase(BaseModel):
    event_type: str
    source: str
    payload: Dict[str, Any]

class EventResponse(EventBase):
    id: UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)
