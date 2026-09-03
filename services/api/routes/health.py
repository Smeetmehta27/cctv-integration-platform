from fastapi import APIRouter
from packages.shared.database import check_db_health

router = APIRouter()

@router.get("/health")
async def health_check():
    db_status, db_engine = await check_db_health()
    return {
        "status": "ok",
        "service": "api",
        "database": {
            "status": db_status,
            "engine": db_engine
        },
        "redis": {
            "status": "UNKNOWN" # Redis mock
        }
    }
