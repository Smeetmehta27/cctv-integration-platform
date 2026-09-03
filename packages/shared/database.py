import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from packages.shared.models import Base
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vigilis")
USE_FALLBACK = os.getenv("USE_FALLBACK", "false").lower() == "true"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# SQLite fallback (in-memory for simple mocking during UI development)
FALLBACK_URL = "sqlite+aiosqlite:///:memory:"

engine = None
AsyncSessionLocal = None
is_connected = False

def init_db():
    global engine, AsyncSessionLocal
    # Try PostgreSQL first, unless forced fallback
    if not USE_FALLBACK:
        try:
            logger.info(f"Attempting to connect to PostgreSQL at {DB_HOST}:{DB_PORT}...")
            engine = create_async_engine(DATABASE_URL, echo=False)
            AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        except Exception as e:
            logger.warning(f"Failed to initialize PostgreSQL engine: {e}")
            _setup_fallback()
    else:
        _setup_fallback()

from sqlalchemy.pool import StaticPool

def _setup_fallback():
    global engine, AsyncSessionLocal
    logger.info("Setting up SQLite fallback database...")
    engine = create_async_engine(
        FALLBACK_URL, 
        echo=False,
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # The models will be initialized lazily in check_db_health or get_db
    pass

_models_initialized = False

async def _init_fallback_models():
    global _models_initialized
    if _models_initialized:
        return
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("SQLite fallback ORM models initialized successfully.")
            _models_initialized = True
    except Exception as e:
        logger.error(f"Failed to initialize SQLite models: {e}")

async def check_db_health():
    global is_connected
    if not AsyncSessionLocal:
        init_db()
    
    if engine.name == "sqlite":
        await _init_fallback_models()
        
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
    
    if engine.name == "sqlite":
        await _init_fallback_models()
        
    async with AsyncSessionLocal() as session:
        yield session

# Wait to initialize until requested by get_db or health_check
