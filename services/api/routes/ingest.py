from fastapi import APIRouter
from typing import List
from packages.shared.database import AsyncSessionLocal, USE_FALLBACK
from sqlalchemy import text

router = APIRouter(prefix="/ingest", tags=["ingest"])

def _get_mock_catalogue():
    return [
        {
            "id": "cam-101",
            "name": "SG Highway Junction 1",
            "department": "Ahmedabad City Police",
            "location": "SG Highway, Ahmedabad",
            "latitude": 23.0312,
            "longitude": 72.5255,
            "codec": "H.264",
            "resolution": "1080p",
            "live_status": "ONLINE",
            "stream_properties": {
                "fps": 25,
                "bitrate": "2Mbps"
            },
            "rtsp_url": "rtsp://demo:demo@192.168.1.100:554/stream1",
            "webrtc_url": "webrtc://demo.stream/cam-101",
            "hls_url": "https://demo.stream/cam-101/index.m3u8"
        },
        {
            "id": "cam-102",
            "name": "Ashram Road Cross",
            "department": "Ahmedabad City Police",
            "location": "Ashram Road, Ahmedabad",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "codec": "H.265",
            "resolution": "720p",
            "live_status": "OFFLINE",
            "stream_properties": {
                "fps": 15,
                "bitrate": "1Mbps"
            },
            "rtsp_url": "rtsp://demo:demo@192.168.1.101:554/stream1",
            "webrtc_url": None,
            "hls_url": None
        }
    ]

@router.get("")
@router.get("/")
async def get_catalogue():
    if USE_FALLBACK or not AsyncSessionLocal:
        return _get_mock_catalogue()
        
    try:
        async with AsyncSessionLocal() as session:
            q = """
                SELECT c.id, c.name, d.name as department, c.address, 
                       c.latitude as lat, c.longitude as lng, 
                       c.codec, c.resolution, c.status, c.fps, c.url 
                FROM cameras c 
                LEFT JOIN departments d ON c.department_id = d.id 
                WHERE c.status IN ('ONLINE', 'DEGRADED')
            """
            result = await session.execute(text(q))
            rows = result.fetchall()
            
            catalogue = []
            for r in rows:
                catalogue.append({
                    "id": str(r[0]),
                    "name": r[1],
                    "department": r[2] or "Unknown",
                    "location": r[3] or "Unknown",
                    "latitude": r[4] if r[4] is not None else 23.0225,
                    "longitude": r[5] if r[5] is not None else 72.5714,
                    "codec": r[6],
                    "resolution": r[7],
                    "live_status": r[8],
                    "stream_properties": {
                        "fps": r[9] or 30,
                        "bitrate": "2Mbps"
                    },
                    "rtsp_url": r[10] or "rtsp://demo:demo@localhost:554/stream",
                    "webrtc_url": None,
                    "hls_url": None
                })
            return catalogue
    except Exception as e:
        print(f"Error fetching catalogue: {e}")
        return _get_mock_catalogue()
