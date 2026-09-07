import os
import urllib.parse
import socket
from dotenv import load_dotenv

# Force load environment variables for Uvicorn subprocesses
load_dotenv()

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from packages.shared.models import Base
import asyncio
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USE_FALLBACK = os.getenv("USE_FALLBACK", "false").lower() == "true"

DATABASE_URL_ENV = os.getenv("DATABASE_URL")

if not DATABASE_URL_ENV and not USE_FALLBACK:
    raise ValueError("CRITICAL: DATABASE_URL environment variable is missing. Cannot boot AI/API service.")

# URL Sanitization: Strip whitespace, quotes, and accidental placeholder brackets
DATABASE_URL: str = (DATABASE_URL_ENV or "").strip().strip("\"'").replace("[", "").replace("]", "")

# Ensure asyncpg dialect is used for Supabase Postgres connections by strictly sanitizing the URL scheme
if DATABASE_URL:
    if "://" in DATABASE_URL:
        scheme, rest = DATABASE_URL.split("://", 1)
        if scheme.startswith("postgres"):
            DATABASE_URL = f"postgresql+asyncpg://{rest}"

db_hostname = ""
if DATABASE_URL:
    parsed = urllib.parse.urlparse(DATABASE_URL)
    db_hostname = parsed.hostname

# SQLite fallback (persistent local file for connection pool sharing)
FALLBACK_URL = "sqlite+aiosqlite:///./fallback.db"

engine: Any = None
AsyncSessionLocal: Any = None
is_connected = False

def init_db():
    global engine, AsyncSessionLocal
    # Try PostgreSQL first, unless forced fallback
    if not USE_FALLBACK:
        try:
            logger.info("Attempting to connect to PostgreSQL via DATABASE_URL...")
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL is empty")
                
            if db_hostname:
                logger.info(f"Attempting to resolve database host: {db_hostname}")
                try:
                    socket.getaddrinfo(db_hostname, None)
                except socket.gaierror:
                    raise ValueError("CRITICAL: DNS Resolution failed for database host. Check your .env file for typos or leftover placeholders.")
                    
            engine = create_async_engine(DATABASE_URL, echo=False)
            AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore
        except Exception as e:
            logger.warning(f"Failed to initialize PostgreSQL engine: {e}")
            _setup_fallback()
    else:
        _setup_fallback()

import sqlite3
import random

# Gujarat city base coordinates for realistic scatter
_GUJARAT_CITIES = [
    ("Ahmedabad", 23.0225, 72.5714),
    ("Surat", 21.1702, 72.8311),
    ("Vadodara", 22.3072, 73.1812),
    ("Rajkot", 22.3039, 70.8022),
    ("Bhavnagar", 21.7645, 72.1519),
    ("Jamnagar", 22.4707, 70.0577),
    ("Junagadh", 21.5222, 70.4579),
    ("Gandhinagar", 23.2156, 72.6369),
    ("Anand", 22.5565, 72.9520),
    ("Nadiad", 22.6916, 72.8634),
    ("Morbi", 22.8173, 70.8370),
    ("Mehsana", 23.5880, 72.3693),
    ("Bharuch", 21.7051, 72.9959),
    ("Vapi", 20.3893, 72.9106),
    ("Navsari", 20.9467, 72.9520),
    ("Veraval", 20.9159, 70.3629),
    ("Porbandar", 21.6417, 69.6293),
    ("Godhra", 22.7788, 73.6143),
    ("Bhuj", 23.2420, 69.6669),
    ("Palanpur", 24.1725, 72.4340),
    ("Valsad", 20.5992, 72.9342),
    ("Patan", 23.8493, 72.1266),
    ("Dahod", 22.8350, 74.2525),
    ("Amreli", 21.6015, 71.2204),
    ("Surendranagar", 22.7201, 71.6480),
    ("Kutch-Gandhidham", 23.0753, 70.1337),
    ("Dwarka", 22.2394, 68.9678),
    ("Diu", 20.7141, 70.9874),
    ("Silvassa", 20.2766, 73.0088),
    ("Daman", 20.3974, 72.8328),
]

def _setup_fallback():
    global engine, AsyncSessionLocal
    logger.info("Setting up SQLite fallback database...")
    
    try:
        conn = sqlite3.connect("./fallback.db")
        cursor = conn.cursor()

        # Drop and recreate to ensure scattered coordinates overwrite old identical ones
        cursor.execute("DROP TABLE IF EXISTS cameras")
        cursor.execute("CREATE TABLE cameras (id TEXT PRIMARY KEY, name TEXT, status TEXT, latitude REAL, longitude REAL)")

        logger.info("SQLite fallback active. Seeding 30 cameras scattered across Gujarat...")
        rng = random.Random(42)  # Fixed seed for reproducible scatter
        for i in range(1, 31):
            cam_id = f"cam{i:02d}"
            city_name, base_lat, base_lng = _GUJARAT_CITIES[i - 1]
            # Small jitter so pins don't land exactly on the city center
            lat = base_lat + rng.uniform(-0.02, 0.02)
            lng = base_lng + rng.uniform(-0.02, 0.02)
            cam_name = f"{city_name} Sentinel {i:02d}"
            cursor.execute(
                "INSERT INTO cameras (id, name, status, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                (cam_id, cam_name, "ONLINE", round(lat, 6), round(lng, 6))
            )
        conn.commit()
        conn.close()
        logger.info("SQLite fallback ORM models initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite models: {e}")

    engine = create_async_engine(
        FALLBACK_URL, 
        echo=False,
        connect_args={'check_same_thread': False}
    )
    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore

async def check_db_health():
    global is_connected
    if not AsyncSessionLocal:
        init_db()
        
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            is_connected = True
            return "CONNECTED", engine.name
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        is_connected = False
        return "DISCONNECTED", "none"

async def get_db():
    if not AsyncSessionLocal:
        init_db()
        
    async with AsyncSessionLocal() as session:
        yield session

# Wait to initialize until requested by get_db or health_check
