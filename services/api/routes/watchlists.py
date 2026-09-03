from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from packages.shared.database import get_db
from packages.shared.models import Watchlist, WatchlistEntry

router = APIRouter(prefix="/watchlists", tags=["watchlists"])

@router.get("/")
async def get_watchlists(db: AsyncSession = Depends(get_db)):
    stmt = select(Watchlist)
    result = await db.execute(stmt)
    watchlists = result.scalars().all()
    
    return [
        {
            "id": w.id,
            "name": w.name,
            "category": w.category,
            "description": w.description
        }
        for w in watchlists
    ]

@router.get("/{watchlist_id}/entries")
async def get_watchlist_entries(watchlist_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(WatchlistEntry).where(WatchlistEntry.watchlist_id == watchlist_id)
    result = await db.execute(stmt)
    entries = result.scalars().all()
    
    return [
        {
            "id": e.id,
            "entity_type": e.entity_type,
            "entity_value": e.entity_value,
            "notes": e.notes
        }
        for e in entries
    ]

@router.post("/seed")
async def seed_watchlists(db: AsyncSession = Depends(get_db)):
    """Seed dummy watchlists for prototyping."""
    # Check if exists
    stmt = select(Watchlist).where(Watchlist.name == "Stolen Vehicles (Statewide)")
    result = await db.execute(stmt)
    if result.scalars().first():
        return {"status": "already seeded"}
        
    wl = Watchlist(
        name="Stolen Vehicles (Statewide)",
        category="STOLEN_VEHICLE",
        description="Vehicles reported stolen across Gujarat"
    )
    db.add(wl)
    await db.flush()
    
    entry1 = WatchlistEntry(
        watchlist_id=wl.id,
        entity_type="VEHICLE",
        entity_value="GJ01AB1234",
        notes="Stolen White Hyundai Creta. FIR #12345."
    )
    db.add(entry1)
    await db.commit()
    
    return {"status": "success", "seeded": wl.name}
