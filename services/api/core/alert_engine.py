import time
import logging
from typing import Dict
from services.api.websockets.manager import manager
import json
from sqlalchemy import select
from packages.shared.models import WatchlistEntry, Alert

logger = logging.getLogger(__name__)

class AlertEngine:
    def __init__(self):
        # Deduplication cache: {camera_id: {plate_number: last_timestamp}}
        self.last_alerts: Dict[str, Dict[str, float]] = {}
        self.dedup_window_seconds = 300 # 5 minutes

    async def process_plate_event(self, event_envelope: dict, db_session):
        """
        Receives a PLATE_CONFIRMED event envelope, matches against watchlists,
        deduplicates, and fires an alert if necessary.
        """
        camera_id = event_envelope.get("camera_id")
        payload = event_envelope.get("payload", {})
        plate_data = payload.get("plate", {})
        plate_number = plate_data.get("normalized_text")
        track_id = payload.get("track_id")
        
        if not camera_id or not plate_number:
            return
            
        # 1. Query Watchlist (Database)
        stmt = select(WatchlistEntry).where(WatchlistEntry.entity_value == plate_number)
        result = await db_session.execute(stmt)
        watchlist_entry = result.scalars().first()
        
        if not watchlist_entry:
            return # Not on a watchlist
            
        # 2. Deduplication check
        if camera_id not in self.last_alerts:
            self.last_alerts[camera_id] = {}
            
        last_alert_time = self.last_alerts[camera_id].get(plate_number, 0)
        current_time = time.time()
        
        if current_time - last_alert_time < self.dedup_window_seconds:
            logger.info(f"Duplicate alert suppressed for plate {plate_number} on camera {camera_id}")
            return
            
        # Update cache
        self.last_alerts[camera_id][plate_number] = current_time
        
        # 3. Create Alert in Database
        alert = Alert(
            camera_id=camera_id,
            watchlist_entry_id=watchlist_entry.id,
            alert_type="WATCHLIST_MATCH",
            priority="HIGH",
            status="NEW",
            description=f"Watchlist match for {plate_number}",
            evidence={
                "track_id": track_id,
                "plate": plate_data,
                "notes": watchlist_entry.notes
            }
        )
        db_session.add(alert)
        await db_session.commit()
        await db_session.refresh(alert)
        
        # 4. Broadcast Event via WebSocket
        alert_payload = {
            "event_type": "ALERT_TRIGGERED",
            "camera_id": camera_id,
            "timestamp": alert.timestamp.isoformat() if alert.timestamp else "",
            "payload": {
                "alert_id": alert.id,
                "plate_number": plate_number,
                "priority": alert.priority,
                "description": alert.description,
                "evidence": alert.evidence
            }
        }
        
        await manager.broadcast(json.dumps(alert_payload))
        logger.warning(f"ALERT FIRED: {plate_number} detected on {camera_id}!")

# Singleton instance
alert_engine = AlertEngine()
