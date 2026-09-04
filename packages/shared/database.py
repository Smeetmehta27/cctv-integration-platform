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

def _setup_fallback():
    global engine, AsyncSessionLocal
    logger.info("Setting up SQLite fallback database...")
    
    try:
        conn = sqlite3.connect("./fallback.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS cameras (id TEXT PRIMARY KEY, name TEXT, status TEXT, latitude REAL, longitude REAL)")
        
        cursor.execute("SELECT COUNT(*) FROM cameras")
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("SQLite fallback active. Seeding 30 baseline sentinel cameras...")
            for i in range(1, 31):
                cam_id = f"cam{i:02d}"
                cam_name = f"Fallback Sentinel {i:02d}"
                cursor.execute(
                    "INSERT INTO cameras (id, name, status, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                    (cam_id, cam_name, "ONLINE", 23.0225, 72.5714)
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
