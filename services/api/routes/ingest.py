from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.get("/")
async def get_catalogue():
    # Hackathon camera catalogue mock response
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
