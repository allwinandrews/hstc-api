"""Quick asyncpg connectivity check for local debugging."""

import asyncio
import asyncpg

async def main():
    """Connect to Postgres and run a minimal query."""
    conn = await asyncpg.connect(
        user="hstc",
        password="hstc",
        database="hstc",
        host="127.0.0.1",
        port=5432,
    )
    value = await conn.fetchval("SELECT 1")
    print(value)
    await conn.close()

asyncio.run(main())
