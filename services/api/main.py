from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from services.api.routes import health, cameras, ingest, departments, events, alerts, watchlists, internal_events, tracks
from services.api.websockets.manager import router as websockets_router

app = FastAPI(title="VIGILIS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cameras.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(departments.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(watchlists.router, prefix="/api")
app.include_router(internal_events.router, prefix="/api")
app.include_router(tracks.router, prefix="/api")
app.include_router(websockets_router)

from packages.shared.database import init_db, _init_fallback_models, engine

@app.on_event("startup")
async def startup_event():
    init_db()
    if engine and engine.name == "sqlite":
        await _init_fallback_models()

@app.on_event("shutdown")
async def shutdown_event():
    pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
