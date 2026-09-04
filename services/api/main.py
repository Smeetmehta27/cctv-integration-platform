from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from services.api.routes import health, cameras, ingest, departments, events, alerts, watchlists, internal_events, tracks, tracking, reports, stream
from services.api.websockets.manager import router as websockets_router
from packages.shared.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="VIGILIS API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cameras.router, prefix="/api")
app.include_router(cameras.router, prefix="/api/v1") # API v1 requirement
app.include_router(ingest.router, prefix="/api")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(watchlists.router, prefix="/api/v1")
app.include_router(internal_events.router, prefix="/api")
app.include_router(tracking.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(tracks.router, prefix="/api")
app.include_router(stream.router, prefix="/api/v1/stream", tags=["stream"])
app.include_router(websockets_router)



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
