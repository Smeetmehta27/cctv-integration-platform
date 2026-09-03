from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from packages.shared.database import get_db
from packages.shared.models import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    stmt = select(Alert).order_by(Alert.timestamp.desc()).limit(50)
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "camera_id": a.camera_id,
            "alert_type": a.alert_type,
            "priority": a.priority,
            "status": a.status,
            "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            "description": a.description,
            "evidence": a.evidence
        }
        for a in alerts
    ]
