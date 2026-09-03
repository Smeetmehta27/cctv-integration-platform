from fastapi import APIRouter
from packages.shared.database import AsyncSessionLocal, USE_FALLBACK
from sqlalchemy import text
from typing import List

router = APIRouter(prefix="/cameras", tags=["cameras"])

def _get_mock_cameras():
    return [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "SG Highway Junction 1",
            "location": {"lat": 23.0312, "lng": 72.5255},
            "status": "ONLINE"
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "Ashram Road Cross",
            "location": {"lat": 23.0225, "lng": 72.5714},
            "status": "OFFLINE"
        }
    ]

@router.get("/")
async def get_cameras():
    if USE_FALLBACK or not AsyncSessionLocal:
        return _get_mock_cameras()
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT id, name, status FROM cameras"))
            rows = result.fetchall()
            return [{"id": str(r[0]), "name": r[1], "status": r[2]} for r in rows]
    except Exception as e:
        return _get_mock_cameras()

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    if USE_FALLBACK or not AsyncSessionLocal:
        return _get_mock_cameras()[0]
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT id, name, status FROM cameras WHERE id = :id"), {"id": camera_id})
            row = result.fetchone()
            if row:
                return {"id": str(row[0]), "name": row[1], "status": row[2]}
    except Exception as e:
        pass
    
    return _get_mock_cameras()[0]

@router.get("/{camera_id}/health")
async def get_camera_health(camera_id: str):
    return {"status": "ok", "last_ping": "2026-09-03T00:00:00Z"}
