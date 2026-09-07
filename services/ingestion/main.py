from fastapi import FastAPI
import os
import asyncio
import logging
from services.ingestion.stream_manager import StreamManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VIGILIS Ingestion Service", version="1.0.0")
manager = StreamManager()

background_tasks = set()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Ingestion Stream Manager...")
    task = asyncio.create_task(manager.poll_catalogue())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping Ingestion Stream Manager...")
    manager.stop_all()

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "service": "ingestion",
        "active_streams": len(manager.active_streams)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("INGESTION_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
