"""
Pre-start script — runs ONCE before Uvicorn spawns workers.
Creates all database tables if they don't exist.
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prestart")


async def init_db():
    from app.db import engine
    from app.models import Base

    logger.info("Running database initialization (create_all)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    logger.info("Database initialization complete.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
