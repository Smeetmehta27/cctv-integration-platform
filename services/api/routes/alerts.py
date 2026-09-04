from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from packages.shared.database import get_db
from packages.shared.models import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
@router.get("/")
async def get_alerts():
    return []
