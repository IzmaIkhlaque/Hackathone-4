# Course Companion FTE — Architecture

## Phase 1: Zero-Backend-LLM Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STUDENT (USER)                              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ natural language question
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ChatGPT App (Frontend LLM)                       │
│                                                                     │
│  System Prompt: Course Companion FTE                                │
│  Skills loaded: concept-explainer · quiz-master                     │
│                 socratic-tutor · progress-motivator                 │
│                                                                     │
│  ALL reasoning happens here. Backend has ZERO LLM calls.            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP calls via OpenAI Actions
                               │ (openapi.yaml defines the contract)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              L3 — FastAPI Backend (Railway.app)                     │
│                                                                     │
│  /api/v1/content/     → fetch markdown chapters                    │
│  /api/v1/navigation/  → next/prev/sequence                         │
│  /api/v1/quiz/        → serve questions + grade answers            │
│  /api/v1/progress/    → read/write progress + streak               │
│  /api/v1/search/      → full-text search                           │
│  /api/v1/access/      → freemium gate check                        │
│  /health              → status proof (backend_llm: false)          │
│                                                                     │
│  100% deterministic. No LLM calls. No AI in the server.            │
└──────────┬─────────────────────────────────────┬────────────────────┘
           │ asyncpg (PostgreSQL wire protocol)  │ boto3 (S3 API)
           ▼                                     ▼
┌──────────────────────┐             ┌───────────────────────────────┐
│  Neon PostgreSQL     │             │    Cloudflare R2              │
│  (Serverless)        │             │    (Object Storage)           │
│                      │             │                               │
│  users               │             │  chapters/chapter-01.md       │
│  progress            │             │  chapters/chapter-02.md       │
│  streaks             │             │  chapters/chapter-03.md       │
│  quiz_attempts       │             │  chapters/chapter-04.md       │
│  content_metadata    │             │  chapters/chapter-05.md       │
│                      │             │  chapters/chapter-06.md       │
│  Free tier: $0/mo    │             │  quizzes/quiz-01.json         │
│                      │             │  quizzes/quiz-02.json         │
└──────────────────────┘             │  quizzes/quiz-03.json         │
                                     │                               │
                                     │  ~$5/month at 10K users       │
                                     └───────────────────────────────┘
```

---

## Why Zero-Backend-LLM?

### The Core Insight
ChatGPT is already a powerful reasoning engine that the student is *already paying for*. Instead of calling Claude or GPT-4 from our server (adding cost + latency + attack surface), we turn the ChatGPT App itself into the reasoning layer.

Our backend becomes a **pure data API**:
- Deterministic — every input produces the same output
- Fast — no LLM latency, just DB + object storage reads
- Cheap — no per-request AI cost on the server side
- Safe — no risk of hallucinated content served as facts

### Cost Equation
```
Phase 1 server cost per 10,000 users = ~$11/month
LLM cost per request                 = $0.00
Total AI cost to developer           = $0.00
```
Users bring their own ChatGPT subscription — we provide the structured backend.

---

## Agent Factory Architecture Mapping (8 Layers)

| Layer | Component | Phase 1 Status |
|---|---|---|
| L1 — Event Bus | Kafka / Dapr | Phase 2/3 |
| L2 — State Store | Redis | Phase 2/3 |
| **L3 — HTTP Interface** | **FastAPI (our backend)** | **BUILT** |
| **L4 — MCP Server** | **SKILL.md files** | **BUILT** |
| L5 — Agent SDK | Claude Agent SDK | Phase 2 |
| **L6 — Runtime Skills** | **concept-explainer, quiz-master, socratic-tutor, progress-motivator** | **BUILT** |
| **L7 — A2A Protocol** | **OpenAI Actions (openapi.yaml)** | **BUILT** |
| L8 — Observability | Langfuse / Arize | Phase 2/3 |

---

## Data Flow: A Complete Request Lifecycle

```
Student: "Can you quiz me on Chapter 1?"
    │
    ├─ ChatGPT matches trigger: "quiz me" → quiz-master skill activates
    │
    ├─ Step 1: GET /api/v1/quiz/chapter/chapter-01
    │          ← { "quiz_id": "quiz-01" }
    │
    ├─ Step 2: GET /api/v1/quiz/quiz-01
    │          ← { questions: [...] }  // NO correct_answers in response
    │
    ├─ ChatGPT presents Question 1 to student
    │
    ├─ Student answers: "B"
    │
    ├─ Step 3: POST /api/v1/quiz/quiz-01/submit
    │          body: { user_id, answers: [{q1: "B"}, ...] }
    │          ← { score: 80, passed: true, feedback: [...] }
    │          (deterministic string comparison, ZERO LLM)
    │
    ├─ ChatGPT generates celebration message using quiz-master template
    │
    └─ Step 4: PUT /api/v1/progress/{user_id}/chapter/chapter-01
               body: { completed: true, completion_percentage: 100 }
               ← updated progress + streak recalculated
```

---

## Phase Evolution Path

### Phase 1 (Current) — Zero-Backend-LLM
- ChatGPT App does all reasoning
- Backend = pure deterministic data API
- Cost: ~$11/month at 10K users

### Phase 2 — Hybrid Intelligence
- Add `api/v1/hybrid/` routes (folder already exists as `hybrid/`)
- LLM calls ONLY for premium features: adaptive paths, semantic search, LLM-graded assessments
- Claude Sonnet at ~$0.018/request, charged to premium users only
- Free tier remains Zero-Backend-LLM

### Phase 3 — Full Next.js Web App
- Replace `web/` HTML pages with Next.js app (folder: `web/nextjs/`)
- Add JWT authentication
- Admin dashboard
- Full observability (Langfuse)
- Same backend — just adding features, never rebuilding

---

## Database Schema Design Philosophy

All 5 tables are designed to support all 3 phases from day 1:

- `users.tier` — supports free/premium/pro/team tiers needed in Phase 2/3
- `quiz_attempts.answers_json` (JSONB) — stores full attempt for Phase 2 LLM analysis
- `progress.completion_percentage` — enables Phase 3 granular tracking
- `content_metadata.tags` (TEXT[]) — enables Phase 2 semantic search bootstrapping
- `streaks.total_study_days` — enables Phase 3 gamification features
