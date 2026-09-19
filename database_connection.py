"""
DATABASE CONNECTION POOL.

Opening a fresh connection on every single request for a database is slow and wasteful.
Instead, a POOL of connections gets created ONCE when the server starts, reused across
every request, and closed cleanly once the server shuts down.

This is now the first thing in my project that needs to exist BEFORE the app starts
serving requests, and needs to clean up after it stops. FastAPI's answer to this is 'lifespan'.
"""

import asyncpg
from config_settings import settings

pool: asyncpg.Pool | None = None

async def connect_to_database():
    global pool
    pool = await asyncpg.create_pool(settings.supabase_database_url, min_size=1, max_size=5)

async def close_database_connection():
    global pool
    if pool:
        await pool.close()

def get_pool() -> asyncpg.Pool:
    return pool




