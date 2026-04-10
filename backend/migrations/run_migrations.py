"""
Run this script once to create all tables in Neon PostgreSQL.
Usage:
    cd backend
    DATABASE_URL="postgresql://..." python migrations/run_migrations.py
"""
import asyncio
import os
from pathlib import Path

import asyncpg


async def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        # Fall back to .env file
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
        dsn = os.environ.get("DATABASE_URL")

    if not dsn:
        raise SystemExit("ERROR: DATABASE_URL not set. Export it or add it to backend/.env")

    sql_path = Path(__file__).parent / "001_init.sql"
    sql = sql_path.read_text(encoding="utf-8")

    print(f"Connecting to Neon PostgreSQL...")
    conn = await asyncpg.connect(dsn=dsn, ssl="require")
    try:
        print("Running 001_init.sql ...")
        await conn.execute(sql)
        print("Migration complete. All 5 tables created (IF NOT EXISTS).")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
