-- Course Companion FTE — Initial Schema
-- Run this once against your Neon PostgreSQL database.
-- Neon supports all standard PostgreSQL extensions including gen_random_uuid().

-- ─── users ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     VARCHAR(255) UNIQUE NOT NULL,  -- ChatGPT user ID or web session ID
    email       VARCHAR(255),
    tier        VARCHAR(20)  DEFAULT 'free',   -- 'free' | 'premium' | 'pro' | 'team'
    created_at  TIMESTAMP    DEFAULT NOW(),
    updated_at  TIMESTAMP    DEFAULT NOW()
);

-- ─── progress ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS progress (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id               VARCHAR(255) NOT NULL REFERENCES users(user_id),
    chapter_id            VARCHAR(100) NOT NULL,
    completed             BOOLEAN      DEFAULT FALSE,
    completion_percentage INTEGER      DEFAULT 0,   -- 0-100
    last_read_at          TIMESTAMP,
    created_at            TIMESTAMP    DEFAULT NOW(),
    updated_at            TIMESTAMP    DEFAULT NOW(),
    UNIQUE(user_id, chapter_id)
);

-- ─── streaks ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS streaks (
    id                 UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            VARCHAR(255) UNIQUE NOT NULL REFERENCES users(user_id),
    current_streak     INTEGER      DEFAULT 0,
    longest_streak     INTEGER      DEFAULT 0,
    last_activity_date DATE,
    total_study_days   INTEGER      DEFAULT 0,
    updated_at         TIMESTAMP    DEFAULT NOW()
);

-- ─── quiz_attempts ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          VARCHAR(255) NOT NULL REFERENCES users(user_id),
    quiz_id          VARCHAR(100) NOT NULL,
    chapter_id       VARCHAR(100) NOT NULL,
    score            INTEGER      NOT NULL,   -- 0-100
    total_questions  INTEGER      NOT NULL,
    correct_answers  INTEGER      NOT NULL,
    answers_json     JSONB,                   -- Full attempt stored for Phase 2 analysis
    passed           BOOLEAN      DEFAULT FALSE,
    attempted_at     TIMESTAMP    DEFAULT NOW()
);

-- ─── content_metadata ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_metadata (
    id                UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id        VARCHAR(100) UNIQUE NOT NULL,
    title             VARCHAR(500) NOT NULL,
    description       TEXT,
    order_index       INTEGER      NOT NULL,   -- For next/prev navigation
    tier_required     VARCHAR(20)  DEFAULT 'free',  -- 'free' | 'premium' | 'pro'
    r2_key            VARCHAR(500) NOT NULL,   -- R2 storage key
    word_count        INTEGER,
    estimated_minutes INTEGER,
    tags              TEXT[],                  -- For keyword search
    created_at        TIMESTAMP    DEFAULT NOW()
);

-- ─── Seed content_metadata with the 6 chapters ───────────────────────────────
INSERT INTO content_metadata (chapter_id, title, description, order_index, tier_required, r2_key, word_count, estimated_minutes, tags)
VALUES
  ('chapter-01', 'Introduction to AI Agents and Digital FTEs',
   'Learn what Digital FTEs are, how AI agents differ from chatbots, and the Agent Factory Architecture.',
   1, 'free', 'chapters/chapter-01.md', 950, 15,
   ARRAY['agents', 'fte', 'introduction', 'claude', 'digital-worker']),

  ('chapter-02', 'Claude Agent SDK Deep Dive',
   'Explore the Claude Agent SDK — tools, memory, handoffs, and building production-grade agents.',
   2, 'free', 'chapters/chapter-02.md', 1100, 20,
   ARRAY['claude', 'sdk', 'tools', 'memory', 'agents']),

  ('chapter-03', 'MCP and Agent Skills',
   'Understand the Model Context Protocol and how Skills extend agent capabilities.',
   3, 'free', 'chapters/chapter-03.md', 1050, 18,
   ARRAY['mcp', 'skills', 'protocol', 'tools', 'agents']),

  ('chapter-04', 'OpenAI Agents SDK',
   'Deep dive into OpenAI Agents SDK, Swarm patterns, and multi-agent orchestration.',
   4, 'premium', 'chapters/chapter-04.md', 1200, 22,
   ARRAY['openai', 'sdk', 'swarm', 'orchestration', 'agents']),

  ('chapter-05', 'Multi-Agent Systems and A2A Protocol',
   'Build networks of collaborating agents using the Agent-to-Agent protocol.',
   5, 'premium', 'chapters/chapter-05.md', 1300, 25,
   ARRAY['a2a', 'multi-agent', 'protocol', 'orchestration']),

  ('chapter-06', 'Production Deployment and Monitoring',
   'Deploy AI agent systems at scale with observability, cost control, and safety guardrails.',
   6, 'pro', 'chapters/chapter-06.md', 1400, 28,
   ARRAY['deployment', 'monitoring', 'production', 'railway', 'safety'])
ON CONFLICT (chapter_id) DO NOTHING;
