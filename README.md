# Course Companion FTE

**24/7 AI Tutor for AI Agent Development**
Panaversity Agent Factory Hackathon IV · Built by Izma · GIAIC Q4

> A Digital FTE (Full-Time Equivalent) that teaches you how to build Digital FTEs.

---

## What Is This?

Course Companion FTE is a **Zero-Backend-LLM** learning companion for the AI Agent Development course. It uses ChatGPT as the intelligent frontend and a deterministic FastAPI backend for all data — zero LLM calls on the server.

**Architecture in one line:** ChatGPT App → OpenAI Actions → FastAPI → Neon PostgreSQL + Cloudflare R2

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12) + asyncpg |
| Database | Neon PostgreSQL (serverless, free tier) |
| Content Storage | Cloudflare R2 (S3-compatible) |
| Frontend LLM | ChatGPT App (OpenAI Actions) |
| Web UI | Plain HTML + Tailwind CSS CDN |
| Deployment | Railway.app |

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/course-companion-fte.git
cd course-companion-fte/backend
```

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Edit `.env` and fill in your real credentials:
```env
DATABASE_URL=postgresql://user:password@your-neon-host/dbname
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=course-companion-bucket
R2_PUBLIC_URL=https://pub-xxx.r2.dev
APP_ENV=development
API_SECRET_KEY=change-me-to-something-random
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create database tables
```bash
python migrations/run_migrations.py
```

### 5. Seed content metadata
```bash
python scripts/seed_content_metadata.py
```

### 6. Upload content to R2
```bash
python scripts/upload_content.py
```

### 7. Start the server
```bash
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API documentation.

---

## API Endpoints Summary

```
GET  /health                                    → Architecture compliance proof
GET  /api/v1/content/chapters                   → List all chapters (metadata)
GET  /api/v1/content/chapters/{id}              → Full markdown (freemium gated)
GET  /api/v1/content/chapters/{id}/summary      → 200-word preview (all tiers)
GET  /api/v1/navigation/chapters/{id}/next      → Next chapter metadata
GET  /api/v1/navigation/chapters/{id}/prev      → Previous chapter metadata
GET  /api/v1/navigation/chapters/sequence       → Full ordered sequence (TOC)
GET  /api/v1/quiz/{quiz_id}                     → Questions without answer keys
POST /api/v1/quiz/{quiz_id}/submit              → Deterministic grading
GET  /api/v1/quiz/chapter/{chapter_id}          → Quiz ID for a chapter
GET  /api/v1/progress/{user_id}                 → Full progress summary
PUT  /api/v1/progress/{user_id}/chapter/{id}    → Update chapter progress
GET  /api/v1/progress/{user_id}/streak          → Streak info only
GET  /api/v1/search?q={query}&user_id={id}      → Full-text content search
GET  /api/v1/access/check/{user_id}/{chapter}   → Freemium gate check
POST /api/v1/access/users                       → Create or get user
GET  /api/v1/access/users/{user_id}/tier        → Get user tier
```

**Architecture compliance check:**
```bash
grep -r "anthropic" backend/app/api/   # must return nothing
grep -r "openai" backend/app/api/      # must return nothing
curl http://localhost:8000/health      # must return backend_llm: false
```

---

## How to Use the ChatGPT App

1. **Deploy the backend** to Railway.app (see deployment section below)
2. **Update server URL** in `chatgpt-app/openapi.yaml` (line 11)
3. **Go to** platform.openai.com → My GPTs → Create a GPT
4. **Set the system prompt** from `chatgpt-app/system-prompt.md`
5. **Add Actions** → import `chatgpt-app/openapi.yaml`
6. **Set privacy policy URL** to your deployed `chatgpt-app/privacy.md`
7. **Publish** and share the link with students

The ChatGPT App will automatically use all 4 skills (Concept Explainer, Quiz Master, Socratic Tutor, Progress Motivator) based on what the student says.

---

## Deploy to Railway.app

```bash
# 1. Push to GitHub
git init && git add . && git commit -m "Course Companion FTE Phase 1"
git remote add origin https://github.com/your-username/course-companion-fte.git
git push -u origin main

# 2. Go to railway.app → New Project → Deploy from GitHub
# 3. Select your repo → Railway auto-detects Dockerfile

# 4. Set environment variables in Railway dashboard:
#    DATABASE_URL, R2_ACCOUNT_ID, R2_ACCESS_KEY_ID,
#    R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, API_SECRET_KEY

# 5. Deploy → get your URL (e.g. https://course-companion.railway.app)

# 6. Update chatgpt-app/openapi.yaml line 11:
#    url: https://course-companion.railway.app
```

---

## Project Structure

```
course-companion-fte/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point + all routers
│   │   ├── api/v1/              ← 6 route modules + empty hybrid/ folder
│   │   ├── models/              ← asyncpg raw SQL models
│   │   ├── schemas/             ← Pydantic v2 schemas
│   │   ├── services/            ← Business logic (quiz grading, search, R2)
│   │   └── core/                ← config.py + database.py
│   ├── content/chapters/        ← 6 chapter markdown files
│   ├── content/quizzes/         ← 3 quiz JSON files
│   ├── skills/                  ← 4 SKILL.md agent skill files
│   ├── migrations/              ← SQL init + Python migration runner
│   ├── scripts/                 ← upload_content.py + seed_content_metadata.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── chatgpt-app/
│   ├── openapi.yaml             ← OpenAPI 3.1.0 spec (17 endpoints)
│   ├── system-prompt.md         ← ChatGPT App system prompt
│   └── privacy.md
├── web/
│   ├── index.html               ← Landing page (Tailwind CDN)
│   ├── dashboard.html           ← Progress dashboard (fetch() API calls)
│   └── learn.html               ← Chapter reader (marked.js markdown)
├── docs/
│   ├── ARCHITECTURE.md          ← System design + data flow diagrams
│   ├── COST_ANALYSIS.md         ← Cost breakdown all 3 phases
│   └── API_DOCS.md
└── SPEC.md                      ← Master specification (hackathon judging)
```

---

## Documentation

- **Architecture:** `docs/ARCHITECTURE.md` — Zero-Backend-LLM design, data flow, phase evolution
- **Cost Analysis:** `docs/COST_ANALYSIS.md` — Full cost breakdown for all 3 phases
- **Master Spec:** `SPEC.md` — Complete project specification for hackathon judges

---

## Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | **COMPLETE** | Zero-Backend-LLM. FastAPI + ChatGPT App + Basic Web UI |
| Phase 2 | Planned | Hybrid Intelligence. LLM for premium users only (hybrid/ folder ready) |
| Phase 3 | Planned | Full Next.js Web App. JWT auth. Admin dashboard. |

---

*Built for Panaversity Agent Factory Hackathon IV · Course: AI Agent Development (Option A)*
