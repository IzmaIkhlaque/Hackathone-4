# Course Companion FTE — Master Specification

**Hackathon:** Panaversity Agent Factory Hackathon IV
**Course Topic:** AI Agent Development (Option A)
**Architecture:** Zero-Backend-LLM (Phase 1) → Hybrid Intelligence (Phase 2) → Full Web App (Phase 3)
**Author:** Izma · GIAIC Q4

---

## 1. Project Overview

### What It Does
Course Companion FTE is a 24/7 AI tutor for the "AI Agent Development" course. It allows students to:
- Read structured course content (6 chapters covering Claude Agent SDK, MCP, OpenAI Agents SDK, multi-agent systems, and production deployment)
- Take rule-based quizzes with deterministic grading
- Track learning progress, streaks, and quiz scores across sessions
- Search course content by keyword
- Get personalized tutoring via a ChatGPT App backed by 4 Agent Skills

### Who It's For
- GIAIC Q4 students learning AI Agent Development
- Any developer wanting structured, guided learning on Claude Agent SDK, MCP, and production agent patterns
- Teams who want to deploy a Digital FTE learning companion at scale

### The "FTE" in the Name
FTE stands for Full-Time Equivalent. A Digital FTE is an AI agent that works 168 hours/week (vs 40 for a human) at a fraction of the cost. This course teaches you how to build them, and the course itself IS one — demonstrating the architecture while teaching it.

---

## 2. Architecture Decisions

### Why Zero-Backend-LLM?

The Phase 1 architecture makes a deliberate choice: **no LLM calls in the backend**.

**Rationale:**
1. **Cost**: Students already have ChatGPT subscriptions. Their LLM usage is pre-paid. Server-side LLM calls would add $0.015–$0.018 per request — uneconomical at scale.
2. **Speed**: Deterministic backends respond in <50ms. LLM calls add 1–5s latency per request.
3. **Reliability**: A database read never hallucinates. Graded quiz answers are always correct.
4. **Compliance**: The hackathon spec required demonstrating Zero-Backend-LLM as a valid production architecture pattern.

**How it works:**
- ChatGPT App (with Course Companion system prompt) acts as the intelligent frontend
- The backend provides structured data via 17 REST endpoints
- ChatGPT reasons over retrieved data — never invents course content
- `/health` endpoint returns `"backend_llm": false` as architectural proof

### Why FastAPI?
Required by hackathon specification. Chosen for async-native support (asyncpg), Pydantic v2 validation, automatic OpenAPI generation, and Python 3.12 support.

### Why Neon PostgreSQL?
Serverless PostgreSQL with a free tier that handles Phase 1 and likely Phase 2 load. Auto-suspend reduces cost to near-zero for low-traffic periods. Full PostgreSQL feature set including `tsvector` for full-text search and `JSONB` for quiz answer storage.

### Why Cloudflare R2?
S3-compatible object storage with no egress fees. Stores markdown chapters and quiz JSON files. Chosen over AWS S3 to eliminate data transfer costs at scale.

---

## 3. API Specification Summary

All routes live under `/api/v1/`. Full spec in `chatgpt-app/openapi.yaml`.

| Section | Routes | Purpose |
|---|---|---|
| 6.1 Content | GET /content/chapters, GET /content/chapters/{id}, GET /content/chapters/{id}/summary | Serve chapter content with freemium gate |
| 6.2 Navigation | GET /navigation/chapters/{id}/next, /prev, /sequence | Chapter ordering and navigation |
| 6.3 Quiz | GET /quiz/{id}, POST /quiz/{id}/submit, GET /quiz/chapter/{id} | Deterministic quiz grading |
| 6.4 Progress | GET /progress/{user_id}, PUT /progress/{user_id}/chapter/{chapter_id}, GET /progress/{user_id}/streak | Progress and streak tracking |
| 6.5 Search | GET /search?q={query}&user_id={id} | Full-text content search |
| 6.6 Access | GET /access/check/{user_id}/{chapter_id}, POST /access/users, GET /access/users/{user_id}/tier | Freemium access control |
| 6.7 Health | GET /health | Architecture compliance proof |

**Total: 17 endpoints, 15 unique operationIds, all documented in openapi.yaml**

---

## 4. Data Model Overview

Five tables in Neon PostgreSQL, designed for all 3 phases from day 1:

| Table | Primary Purpose | Phase 2/3 Extensions |
|---|---|---|
| `users` | User registration, tier management | Auth tokens (Phase 3) |
| `progress` | Chapter completion tracking | Analytics (Phase 2) |
| `streaks` | Daily study streak calculation | Gamification (Phase 3) |
| `quiz_attempts` | Quiz score history (JSONB answers) | LLM re-analysis (Phase 2) |
| `content_metadata` | Chapter catalog, tier requirements, tags | Semantic search index (Phase 2) |

All tables use UUID primary keys, `TIMESTAMP DEFAULT NOW()` for audit trails, and `ON CONFLICT DO UPDATE` for idempotent upserts.

---

## 5. Agent Skills Overview

Four SKILL.md files in `backend/skills/` define the ChatGPT App's behaviour patterns:

| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Concept Explainer | concept-explainer.md | "explain", "what is", "how does" | Ground explanations in course content; never hallucinate |
| Quiz Master | quiz-master.md | "quiz me", "test me", "practice" | Present questions one-at-a-time; submit to backend for grading |
| Socratic Tutor | socratic-tutor.md | "I'm stuck", "help me think" | Guide student to answers via questions (max 3 rounds before direct help) |
| Progress Motivator | progress-motivator.md | "my progress", "streak", "stats" | Celebrate achievements using REAL data from API |

**Key Rule**: All skills are API-grounded. Every fact comes from the backend. ChatGPT's parametric memory is never used as a source of course content.

---

## 6. Freemium Model

### Tier Structure

| Tier | Chapters | Price | Target |
|---|---|---|---|
| Free | chapter-01, 02, 03 | $0 | New students, evaluation |
| Premium | + chapter-04, 05 | $9/month | Committed learners |
| Pro | + chapter-06 | $19/month | Production engineers |
| Team | All + 10 seats | $49/month | Teams and bootcamps |

### Access Control Logic

```python
TIER_RANK = {"free": 0, "premium": 1, "pro": 2, "team": 3}

def can_access(user_tier, required_tier) -> bool:
    return TIER_RANK[user_tier] >= TIER_RANK[required_tier]
```

- `GET /access/check/{user_id}/{chapter_id}` — returns `has_access` boolean
- `GET /content/chapters/{id}` — enforces gate; returns 403 with upgrade message
- `GET /content/chapters/{id}/summary` — always returns 200 (preview available to all)

### Upgrade Flow
1. User hits a locked chapter
2. ChatGPT receives 403 response
3. ChatGPT shows summary + upgrade message (from system prompt Freemium Handling section)
4. User clicks upgrade link to `web/index.html#pricing`
5. (Payment integration is Phase 3 scope)

---

## 7. Phase Evolution Plan

### Phase 1 → Phase 2 (Hybrid Intelligence)
**What changes:** Add `backend/app/api/v1/hybrid/` routes. Nothing else changes.
- `hybrid/adaptive.py` — LLM-generated personalized learning paths
- `hybrid/assessment.py` — Claude-graded open-ended questions
- `hybrid/synthesis.py` — Cross-chapter concept synthesis

**What stays the same:**
- All Phase 1 routes continue to work unchanged
- Database schema requires zero migration (already has JSONB + tags)
- Free tier users never see LLM calls (still Zero-Backend-LLM for them)

### Phase 2 → Phase 3 (Full Web App)
**What changes:** Replace `web/` HTML pages with Next.js app. Add JWT auth.
- `web/nextjs/` — Full Next.js application
- Add JWT middleware to existing FastAPI routes
- Admin dashboard routes
- Team management routes

**What stays the same:** All API routes, database schema, R2 structure, ChatGPT App.

### The Core Promise
_Phase 2 is just adding files. Phase 3 is just adding files. Nothing gets rebuilt._

---

## 8. Cost Analysis

See `docs/COST_ANALYSIS.md` for full breakdown.

**Summary:**
- Phase 1: ~$11/month for 10,000 users (~$0.001/user/month)
- Phase 2: ~$41/month for 10,000 users (LLM cost offset by premium revenue)
- Phase 3: ~$149/month for 50,000 users (~97% gross margin at $9/month premium)

The Zero-Backend-LLM architecture is not just an architecture pattern — it's a business model that makes this course companion economically viable from day one with zero initial investment.
