"""
Seed the content_metadata table in Neon PostgreSQL with all 6 chapters.

Usage (from backend/ directory):
    DATABASE_URL="postgresql://..." python scripts/seed_content_metadata.py
    -- or add DATABASE_URL to backend/.env and run:
    python scripts/seed_content_metadata.py

This script is idempotent — it uses INSERT ... ON CONFLICT DO UPDATE so it
can be re-run safely after content changes.
"""
import asyncio
import os
import sys
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

import asyncpg

CHAPTERS = [
    {
        "chapter_id": "chapter-01",
        "title": "Introduction to AI Agents and Digital FTEs",
        "description": "Learn what Digital FTEs are, how AI agents differ from chatbots, and the Agent Factory Architecture overview.",
        "order_index": 1,
        "tier_required": "free",
        "r2_key": "chapters/chapter-01.md",
        "word_count": 950,
        "estimated_minutes": 15,
        "tags": ["agents", "fte", "introduction", "claude", "digital-worker", "agent-factory"],
    },
    {
        "chapter_id": "chapter-02",
        "title": "Claude Agent SDK Deep Dive",
        "description": "Explore the Claude Agent SDK — tools, memory, handoffs, guardrails, and the agent execution loop.",
        "order_index": 2,
        "tier_required": "free",
        "r2_key": "chapters/chapter-02.md",
        "word_count": 1100,
        "estimated_minutes": 20,
        "tags": ["claude", "sdk", "tools", "memory", "handoffs", "agents", "anthropic"],
    },
    {
        "chapter_id": "chapter-03",
        "title": "MCP and Agent Skills",
        "description": "Understand the Model Context Protocol and how Skills extend agent capabilities through SKILL.md files.",
        "order_index": 3,
        "tier_required": "free",
        "r2_key": "chapters/chapter-03.md",
        "word_count": 1050,
        "estimated_minutes": 18,
        "tags": ["mcp", "skills", "protocol", "tools", "agents", "context", "model-context-protocol"],
    },
    {
        "chapter_id": "chapter-04",
        "title": "OpenAI Agents SDK",
        "description": "Deep dive into OpenAI Agents SDK, Swarm patterns, and multi-agent orchestration. Compare with Claude SDK.",
        "order_index": 4,
        "tier_required": "premium",
        "r2_key": "chapters/chapter-04.md",
        "word_count": 1200,
        "estimated_minutes": 22,
        "tags": ["openai", "sdk", "swarm", "orchestration", "agents", "multi-agent", "handoffs"],
    },
    {
        "chapter_id": "chapter-05",
        "title": "Multi-Agent Systems and the A2A Protocol",
        "description": "Build networks of collaborating agents using the Agent-to-Agent protocol and registry discovery.",
        "order_index": 5,
        "tier_required": "premium",
        "r2_key": "chapters/chapter-05.md",
        "word_count": 1300,
        "estimated_minutes": 25,
        "tags": ["a2a", "multi-agent", "protocol", "orchestration", "agent-network", "communication"],
    },
    {
        "chapter_id": "chapter-06",
        "title": "Production Deployment and Monitoring",
        "description": "Deploy AI agent systems to Railway.app with full observability, cost guardrails, and safety at scale.",
        "order_index": 6,
        "tier_required": "pro",
        "r2_key": "chapters/chapter-06.md",
        "word_count": 1400,
        "estimated_minutes": 28,
        "tags": ["deployment", "monitoring", "production", "railway", "safety", "observability", "cost"],
    },
]

UPSERT_SQL = """
INSERT INTO content_metadata
    (chapter_id, title, description, order_index, tier_required,
     r2_key, word_count, estimated_minutes, tags)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
ON CONFLICT (chapter_id) DO UPDATE SET
    title             = EXCLUDED.title,
    description       = EXCLUDED.description,
    order_index       = EXCLUDED.order_index,
    tier_required     = EXCLUDED.tier_required,
    r2_key            = EXCLUDED.r2_key,
    word_count        = EXCLUDED.word_count,
    estimated_minutes = EXCLUDED.estimated_minutes,
    tags              = EXCLUDED.tags
"""


async def main():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL not set.")
        sys.exit(1)

    print("Connecting to Neon PostgreSQL...")
    conn = await asyncpg.connect(dsn=dsn, ssl="require")
    try:
        print(f"Seeding {len(CHAPTERS)} chapters into content_metadata...")
        for ch in CHAPTERS:
            await conn.execute(
                UPSERT_SQL,
                ch["chapter_id"],
                ch["title"],
                ch["description"],
                ch["order_index"],
                ch["tier_required"],
                ch["r2_key"],
                ch["word_count"],
                ch["estimated_minutes"],
                ch["tags"],
            )
            tier_label = f"[{ch['tier_required'].upper()}]"
            print(f"  {tier_label:12s} {ch['chapter_id']} — {ch['title']}")

        # Verify
        rows = await conn.fetch(
            "SELECT chapter_id, title, tier_required, order_index "
            "FROM content_metadata ORDER BY order_index"
        )
        print()
        print("content_metadata table now contains:")
        for row in rows:
            print(f"  [{row['order_index']}] {row['chapter_id']} ({row['tier_required']}) — {row['title']}")

        print()
        print("Seed complete.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
