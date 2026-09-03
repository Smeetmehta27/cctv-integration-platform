import asyncio
import sys
import os

import json
from services.api.core.alert_engine import alert_engine
from services.api.websockets.manager import manager
from packages.shared.database import get_db, init_db, _setup_fallback
from packages.shared.models import Watchlist, WatchlistEntry, Base
from sqlalchemy import select

broadcasts = []
async def mock_broadcast(message: str):
    broadcasts.append(message)
manager.broadcast = mock_broadcast

async def main():
    print("Initializing Database...")
    # Force SQLite fallback for test
    os.environ["USE_FALLBACK"] = "true"
    _setup_fallback()
    
    # Wait for tables to be created (run_sync in _setup_fallback runs in background task)
    await asyncio.sleep(1)
    
    print("Seeding test watchlist...")
    async for db in get_db():
        wl = Watchlist(name="Test Stolen", category="STOLEN_VEHICLE")
        db.add(wl)
        await db.flush()
        
        entry = WatchlistEntry(
            watchlist_id=wl.id,
            entity_type="VEHICLE",
            entity_value="GJ01AB1234",
            notes="Test entry"
        )
        db.add(entry)
        await db.commit()
        break
        
    print("\n--- Triggering Plate Event 1 (Expected: ALERT FIRED) ---")
    mock_event = {
        "event_type": "PLATE_CONFIRMED",
        "camera_id": "TEST_CAM",
        "payload": {
            "track_id": "TEST_TRACK_001",
            "plate": {
                "normalized_text": "GJ01AB1234",
                "confidence": 0.98,
                "raw_text": "GJ01AB1234"
            }
        }
    }
    
    async for db in get_db():
        await alert_engine.process_plate_event(mock_event, db)
        
    print("\n--- Triggering Plate Event 2 immediately (Expected: SUPPRESSED) ---")
    async for db in get_db():
        await alert_engine.process_plate_event(mock_event, db)
        
    # Check alert history
    print("\n--- Checking Alert History ---")
    async for db in get_db():
        from packages.shared.models import Alert
        stmt = select(Alert)
        res = await db.execute(stmt)
        alerts = res.scalars().all()
        print(f"Total Alerts in DB: {len(alerts)}")
        assert len(alerts) == 1, f"Expected 1 alert due to deduplication, got {len(alerts)}"
        print("Deduplication successfully prevented alert storm!")
        break
        
    print("\n--- Checking Broadcasts ---")
    assert len(broadcasts) == 1, f"Expected exactly 1 broadcast, got {len(broadcasts)}"
    alert_event = json.loads(broadcasts[0])
    assert alert_event["event_type"] == "ALERT_TRIGGERED", "Event must be ALERT_TRIGGERED"
    assert alert_event["payload"]["plate_number"] == "GJ01AB1234", "Plate number must match"
    print("ALERT_TRIGGERED broadcast successful!")
        
    print("\nTEST PASSED: Alert Engine successfully processes envelopes, deduplicates events, and broadcasts alerts.")

if __name__ == "__main__":
    asyncio.run(main())
