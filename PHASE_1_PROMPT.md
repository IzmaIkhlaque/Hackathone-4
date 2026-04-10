# Course Companion FTE — Phase 1 Master Prompt
### For Claude Code CLI | Panaversity Agent Factory Hackathon IV
### Written by: Izma | GIAIC Q4 | Version 1.0

---

> **HOW TO USE THIS FILE**
> Open Claude Code in your project folder and say:
> `"Read PHASE_1_PROMPT.md and follow every instruction exactly. Ask me before making any decision not covered here."`

---

## ⚠️ CRITICAL LONG-TERM PLANNING WARNING (READ FIRST)

This is a 3-phase project. You are building Phase 1 NOW but you MUST NOT break Phase 2 and Phase 3 later.

**The 3 phases are:**
- **Phase 1** → Zero-Backend-LLM. FastAPI backend (no LLM calls). ChatGPT App. Basic Web UI.
- **Phase 2** → Add Hybrid Intelligence (LLM calls for PREMIUM users only). Same backend, new routes added inside `api/v1/hybrid/` folder.
- **Phase 3** → Full Next.js Web App. All features. Same backend extended further.

**Your job in Phase 1:**
Build the foundation so clean that Phase 2 and 3 are just ADD-ONS, never a rebuild.

**Forbidden in Phase 1 (instant disqualification):**
- ANY LLM API calls in the backend
- ANY summarization or agent loop in the backend
- ANY RAG or prompt orchestration in the backend

---

## 1. PROJECT IDENTITY

```
Project Name : Course Companion FTE
Course Topic : AI Agent Development (Option A)
               Topics: Claude Agent SDK, OpenAI Agents SDK, MCP, Agent Skills
Hackathon    : Panaversity Agent Factory Hackathon IV
Architecture : Zero-Backend-LLM (Phase 1) → Hybrid (Phase 2) → Full Web App (Phase 3)
```

---

## 2. TECH STACK (EXACT — DO NOT CHANGE)

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI (Python 3.12) | Required by hackathon spec |
| Database | Neon PostgreSQL (Free Tier) | Serverless, free, supports Phase 2/3 |
| Content Storage | Cloudflare R2 | Required by spec. Stores markdown chapters + quizzes |
| ChatGPT App | OpenAI Actions (openapi.yaml) | Phase 1 frontend |
| Basic Web UI | Plain HTML + Tailwind CDN | Simple, fast, works for Phase 1. Next.js added in Phase 3 |
| Deployment | Railway.app (Free) or Fly.io | Simple deploy, free tier |
| Auth | Simple API Key in header | No OAuth needed in Phase 1 |

---

## 3. FOLDER STRUCTURE (BUILD EXACTLY THIS)

```
course-companion-fte/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI app entry point
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── content.py         ← Chapter/content APIs
│   │   │       ├── navigation.py      ← Next/previous chapter
│   │   │       ├── quiz.py            ← Rule-based quiz grading
│   │   │       ├── progress.py        ← Progress tracking
│   │   │       ├── search.py          ← Keyword search
│   │   │       ├── access.py          ← Freemium gate
│   │   │       └── hybrid/            ← EMPTY FOLDER — Phase 2 will add files here
│   │   │           └── .gitkeep
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                ← User model
│   │   │   ├── progress.py            ← Progress model
│   │   │   └── quiz_attempt.py        ← Quiz attempt model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── content.py             ← Pydantic schemas
│   │   │   ├── quiz.py
│   │   │   └── progress.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── r2_service.py          ← Cloudflare R2 read/write
│   │   │   ├── progress_service.py    ← Progress business logic
│   │   │   ├── quiz_service.py        ← Quiz grading logic
│   │   │   └── search_service.py      ← Keyword search logic
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── config.py              ← All env vars
│   │       └── database.py            ← Neon DB connection
│   │
│   ├── skills/                        ← Agent Skills (SKILL.md files)
│   │   ├── concept-explainer.md
│   │   ├── quiz-master.md
│   │   ├── socratic-tutor.md
│   │   └── progress-motivator.md
│   │
│   ├── content/                       ← Sample content to upload to R2
│   │   ├── chapters/
│   │   │   ├── chapter-01.md
│   │   │   ├── chapter-02.md
│   │   │   └── chapter-03.md          ← Free tier: 3 chapters max
│   │   └── quizzes/
│   │       ├── quiz-01.json
│   │       ├── quiz-02.json
│   │       └── quiz-03.json
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── chatgpt-app/
│   ├── openapi.yaml                   ← ChatGPT App Actions definition
│   ├── system-prompt.md               ← Instructions for ChatGPT to behave as tutor
│   └── privacy.md
│
├── web/
│   ├── index.html                     ← Phase 1 basic web UI
│   ├── dashboard.html                 ← Progress dashboard
│   └── assets/
│       └── style.css
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COST_ANALYSIS.md
│   └── API_DOCS.md
│
├── SPEC.md                            ← Master specification document
├── CLAUDE.md                          ← Instructions for Claude Code (this file)
└── README.md
```

---

## 4. DATABASE SCHEMA (BUILD THIS IN NEON)

> **Important:** Design this schema to support Phase 2 and 3 from day one. Do NOT make a minimal schema that needs to be broken later.

### Table: `users`
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) UNIQUE NOT NULL,     -- ChatGPT user ID or web session ID
    email VARCHAR(255),
    tier VARCHAR(20) DEFAULT 'free',           -- 'free' | 'premium' | 'pro' | 'team'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `progress`
```sql
CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    chapter_id VARCHAR(100) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completion_percentage INTEGER DEFAULT 0,   -- 0-100
    last_read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, chapter_id)
);
```

### Table: `streaks`
```sql
CREATE TABLE streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) UNIQUE NOT NULL REFERENCES users(user_id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    total_study_days INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `quiz_attempts`
```sql
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    quiz_id VARCHAR(100) NOT NULL,
    chapter_id VARCHAR(100) NOT NULL,
    score INTEGER NOT NULL,                    -- 0-100
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    answers_json JSONB,                        -- Store full attempt for Phase 2 analysis
    passed BOOLEAN DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT NOW()
);
```

### Table: `content_metadata`
```sql
CREATE TABLE content_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,              -- For navigation next/prev
    tier_required VARCHAR(20) DEFAULT 'free',  -- 'free' | 'premium' | 'pro'
    r2_key VARCHAR(500) NOT NULL,              -- R2 storage key
    word_count INTEGER,
    estimated_minutes INTEGER,
    tags TEXT[],                               -- For search
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. CLOUDFLARE R2 SETUP

### R2 Bucket Structure:
```
course-companion-bucket/
├── chapters/
│   ├── chapter-01.md       ← Free
│   ├── chapter-02.md       ← Free
│   ├── chapter-03.md       ← Free
│   ├── chapter-04.md       ← Premium
│   ├── chapter-05.md       ← Premium
│   └── chapter-06.md       ← Pro
├── quizzes/
│   ├── quiz-01.json
│   ├── quiz-02.json
│   └── quiz-03.json
└── media/
    └── (images for Phase 3)
```

### R2 Service (`r2_service.py`):
- `get_chapter(chapter_id)` → fetch markdown from R2
- `list_chapters()` → list all chapter keys
- `upload_content(key, content)` → for admin use
- Cache content in memory for 5 minutes to reduce R2 reads

---

## 6. API ROUTES (BUILD ALL OF THESE)

### Base URL: `https://your-backend.railway.app/api/v1`

---

### 6.1 CONTENT APIs

**GET `/content/chapters`**
- Returns: list of all chapters with metadata (title, id, tier_required, estimated_minutes, order_index)
- No auth needed for metadata
- Example response:
```json
{
  "chapters": [
    {
      "chapter_id": "chapter-01",
      "title": "Introduction to AI Agents",
      "tier_required": "free",
      "order_index": 1,
      "estimated_minutes": 15,
      "tags": ["agents", "introduction", "claude"]
    }
  ]
}
```

**GET `/content/chapters/{chapter_id}`**
- Returns: full chapter markdown content
- Headers: `X-User-ID: {user_id}`
- Checks freemium gate first (call access service internally)
- If user does NOT have access: return `403` with `{"error": "premium_required", "upgrade_message": "This chapter requires Premium tier"}`
- If user HAS access: return full chapter markdown
- After serving: automatically update progress (mark as last_read)

**GET `/content/chapters/{chapter_id}/summary`**
- Returns: first 200 words of chapter (preview for locked chapters)
- Available to all tiers

---

### 6.2 NAVIGATION APIs

**GET `/navigation/chapters/{chapter_id}/next`**
- Returns: next chapter metadata (not full content)
- Example response: `{"chapter_id": "chapter-02", "title": "...", "tier_required": "free"}`

**GET `/navigation/chapters/{chapter_id}/prev`**
- Returns: previous chapter metadata

**GET `/navigation/chapters/sequence`**
- Returns: full ordered list (id, title, tier_required) — for building table of contents

---

### 6.3 QUIZ APIs

**GET `/quiz/{quiz_id}`**
- Returns: quiz questions (WITHOUT correct answers)
- Example:
```json
{
  "quiz_id": "quiz-01",
  "chapter_id": "chapter-01",
  "title": "Chapter 1 Quiz",
  "questions": [
    {
      "question_id": "q1",
      "question": "What is an AI Agent?",
      "options": ["A", "B", "C", "D"],
      "type": "mcq"
    }
  ]
}
```

**POST `/quiz/{quiz_id}/submit`**
- Body: `{"user_id": "...", "answers": [{"question_id": "q1", "answer": "A"}, ...]}`
- Backend grades using answer key from R2 (DETERMINISTIC — no LLM)
- Grading logic: compare answer string to answer key JSON
- Returns: `{"score": 80, "total": 5, "correct": 4, "passed": true, "feedback": [{"question_id": "q1", "correct": true, "correct_answer": "A"}]}`
- Store attempt in `quiz_attempts` table

**GET `/quiz/chapter/{chapter_id}`**
- Returns: quiz ID for a given chapter (for navigation)

---

### 6.4 PROGRESS APIs

**GET `/progress/{user_id}`**
- Returns: all progress for a user
```json
{
  "user_id": "...",
  "completed_chapters": ["chapter-01", "chapter-02"],
  "completion_percentage": 33,
  "current_streak": 5,
  "longest_streak": 7,
  "total_study_days": 12,
  "quiz_scores": [{"quiz_id": "quiz-01", "score": 80, "passed": true}]
}
```

**PUT `/progress/{user_id}/chapter/{chapter_id}`**
- Body: `{"completed": true, "completion_percentage": 100}`
- Updates progress and recalculates streak
- Returns updated progress

**GET `/progress/{user_id}/streak`**
- Returns: `{"current_streak": 5, "longest_streak": 7, "last_activity_date": "2026-01-15"}`

---

### 6.5 SEARCH APIs

**GET `/search?q={query}&user_id={user_id}`**
- Keyword search across chapter content (use PostgreSQL full-text search or simple ILIKE)
- Only return chapters the user has access to
- Returns: list of matching sections with chapter_id, title, and a 150-character excerpt
- Example: `GET /search?q=MCP+protocol`

---

### 6.6 ACCESS CONTROL APIs

**GET `/access/check/{user_id}/{chapter_id}`**
- Returns: `{"has_access": true, "tier_required": "free", "user_tier": "free"}`
- Logic: if `tier_required == "free"` → always True. If `"premium"` → check user.tier in DB.

**POST `/access/users`**
- Create or get user by user_id
- Body: `{"user_id": "chatgpt_user_123", "email": null}`
- Returns user object with tier

**GET `/access/users/{user_id}/tier`**
- Returns: `{"user_id": "...", "tier": "free"}`

---

### 6.7 HEALTH CHECK

**GET `/health`**
- Returns: `{"status": "ok", "version": "1.0", "phase": "1", "backend_llm": false}`
- `"backend_llm": false` — proves Zero-Backend-LLM compliance to judges

---

## 7. QUIZ JSON FORMAT (STORE IN R2)

Create this exact format for each quiz file in `content/quizzes/`:

```json
{
  "quiz_id": "quiz-01",
  "chapter_id": "chapter-01",
  "title": "Chapter 1: Introduction to AI Agents",
  "pass_threshold": 70,
  "questions": [
    {
      "question_id": "q1",
      "question": "What does FTE stand for in the context of AI?",
      "options": {
        "A": "Full Task Execution",
        "B": "Full-Time Equivalent",
        "C": "Functional Task Engine",
        "D": "Fast Token Evaluation"
      },
      "correct_answer": "B",
      "explanation": "FTE stands for Full-Time Equivalent — an AI agent that works 168 hours/week like a full-time employee."
    },
    {
      "question_id": "q2",
      "question": "Which SDK is used for Claude-based agentic execution?",
      "options": {
        "A": "OpenAI Agents SDK",
        "B": "LangChain",
        "C": "Claude Agent SDK",
        "D": "Hugging Face Agents"
      },
      "correct_answer": "C",
      "explanation": "Claude Agent SDK is used at Layer 5 for agentic execution in the Agent Factory Architecture."
    },
    {
      "question_id": "q3",
      "question": "In Zero-Backend-LLM architecture, who handles all reasoning?",
      "options": {
        "A": "The FastAPI backend",
        "B": "The database",
        "C": "The ChatGPT App (frontend LLM)",
        "D": "Cloudflare R2"
      },
      "correct_answer": "C",
      "explanation": "In Zero-Backend-LLM, the ChatGPT App (ChatGPT itself) does ALL intelligent reasoning. The backend is purely deterministic."
    },
    {
      "question_id": "q4",
      "question": "What is MCP in the Agent Factory context?",
      "options": {
        "A": "Model Control Protocol",
        "B": "Model Context Protocol",
        "C": "Multi-Cloud Platform",
        "D": "Machine Compute Pipeline"
      },
      "correct_answer": "B",
      "explanation": "MCP stands for Model Context Protocol — it provides tools and domain knowledge to agents."
    },
    {
      "question_id": "q5",
      "question": "What layer in the Agent Factory architecture handles HTTP interface?",
      "options": {
        "A": "L1 - Kafka",
        "B": "L6 - Runtime Skills",
        "C": "L3 - FastAPI",
        "D": "L7 - A2A Protocol"
      },
      "correct_answer": "C",
      "explanation": "L3 (FastAPI) handles the HTTP interface and A2A protocol in the Agent Factory 8-layer architecture."
    }
  ]
}
```

Create 3 quiz files: `quiz-01.json`, `quiz-02.json`, `quiz-03.json` (one per free chapter).

---

## 8. CHAPTER CONTENT FORMAT (STORE IN R2)

Each chapter file is markdown. Create 3 free chapters + 3 premium chapter placeholders:

### `chapter-01.md` example structure:
```markdown
---
chapter_id: chapter-01
title: Introduction to AI Agents and Digital FTEs
order: 1
tier: free
estimated_minutes: 15
tags: [agents, fte, introduction, claude, digital-worker]
---

# Chapter 1: Introduction to AI Agents and Digital FTEs

## What You Will Learn
- What is a Digital FTE
- How AI Agents differ from chatbots
- The Agent Factory Architecture overview
- Why 168 hours/week matters

## 1.1 What is a Digital FTE?

A Digital Full-Time Equivalent (FTE) is an AI agent designed to perform the complete workload of a human employee...

[Continue with 800-1200 words of educational content about AI Agents SDK, Claude, MCP basics]

## 1.2 How AI Agents Work
...

## 1.3 The Agent Factory Architecture
...

## Summary
- Digital FTEs work 168 hours/week
- They use specifications, skills, and tools
- Cost reduction: 85-90% vs human workers

## Next Steps
Proceed to Chapter 2: Understanding the Claude Agent SDK
```

**Create all 3 free chapters with real, useful content about:**
- Chapter 1: AI Agents & Digital FTEs Introduction
- Chapter 2: Claude Agent SDK Deep Dive
- Chapter 3: MCP and Agent Skills

**Create 3 premium chapter placeholder files** (chapter-04, 05, 06) with brief real content showing they exist.

---

## 9. AGENT SKILLS (SKILL.md FILES)

Create all 4 skills inside `backend/skills/`. These are read by the ChatGPT system prompt.

### `concept-explainer.md`
```markdown
---
name: concept-explainer
version: 1.0
triggers: ["explain", "what is", "how does", "define", "tell me about"]
---

# Concept Explainer Skill

## Purpose
Explain AI Agent Development concepts at the student's level. Always ground explanations in the course content retrieved from the backend.

## Workflow
1. Receive concept to explain
2. Fetch relevant chapter content using GET /content/chapters/{id}
3. Extract the relevant section
4. Explain at the student's current level (beginner/intermediate)
5. Provide a real-world analogy
6. End with a check question

## Response Template
"[Concept] means [simple definition].
Think of it like [analogy from real life].
In the context of our course: [course-specific explanation].
Quick check: [simple question to confirm understanding]?"

## Key Principles
- NEVER explain something not in the course content
- If not in content: "That topic isn't covered in this chapter. Let me find the right chapter for you."
- Always keep explanation grounded in retrieved text
- Adapt complexity based on student questions
```

### `quiz-master.md`
```markdown
---
name: quiz-master
version: 1.0
triggers: ["quiz", "test me", "practice", "questions", "exam", "challenge me"]
---

# Quiz Master Skill

## Purpose
Guide students through quizzes with encouragement. Present questions one at a time. Never reveal answers before attempt.

## Workflow
1. Fetch quiz using GET /quiz/{quiz_id}
2. Present first question with 4 options (A/B/C/D)
3. Wait for student answer
4. Submit to POST /quiz/{quiz_id}/submit
5. Give encouraging feedback on each answer
6. Show final score and celebrate/motivate

## Response Template — Correct Answer
"✅ Correct! [Brief explanation of why it's correct].
[Encouragement phrase]. Moving to question [N]..."

## Response Template — Wrong Answer
"Not quite! The correct answer was [X].
Here's why: [explanation from backend feedback].
Don't worry — this is how learning works! Next question..."

## Response Template — Quiz Complete
"🎉 Quiz Complete! You scored [score]% ([correct]/[total]).
[If passed]: Amazing work! You've mastered Chapter [N].
[If failed]: Good attempt! Review [specific weak areas] and try again."

## Key Principles
- Never reveal correct answers before student attempts
- Always submit to backend for grading — never grade manually
- Celebrate wins loudly, handle failures gently
```

### `socratic-tutor.md`
```markdown
---
name: socratic-tutor
version: 1.0
triggers: ["help me think", "I'm stuck", "I don't understand", "confused", "guide me"]
---

# Socratic Tutor Skill

## Purpose
Guide students to discover answers themselves through questions. Do NOT give direct answers immediately.

## Workflow
1. Understand what the student is stuck on
2. Fetch relevant content section
3. Ask a leading question that points toward the answer
4. If student still stuck after 2 questions → give a hint
5. If still stuck after hint → provide the explanation directly

## Response Template
"Interesting question! Let's think about this together.
[Leading question that guides toward answer]
What do you think?"

## Key Principles
- Maximum 3 rounds of Socratic questioning before giving direct help
- Never leave student frustrated — always end with resolution
- Use content from backend as source of truth
```

### `progress-motivator.md`
```markdown
---
name: progress-motivator
version: 1.0
triggers: ["my progress", "streak", "how am I doing", "achievements", "stats"]
---

# Progress Motivator Skill

## Purpose
Celebrate achievements and maintain student motivation using real progress data.

## Workflow
1. Fetch progress: GET /progress/{user_id}
2. Analyze: completed chapters, streak, quiz scores
3. Generate personalized motivation message
4. Suggest next action

## Response Templates

### High Performer (>80% completion)
"🔥 You're on a [N]-day streak! That's incredible dedication.
You've completed [N] chapters — you're [X]% through the course.
Your best quiz score is [score]%. You're crushing it!
Next: [specific chapter recommendation]"

### Mid Progress (40-80%)
"📚 Great progress! [N] chapters down, [N] to go.
Your [N]-day streak shows real commitment.
Tip: [specific advice based on weak quiz areas]"

### Just Starting (0-40%)
"🚀 You've started your AI Agent journey!
[N] chapters completed so far.
Today's goal: Complete Chapter [N] and take the quiz.
You've got this!"

## Key Principles
- Always use REAL numbers from backend, never make up data
- Celebrate streaks loudly — they drive retention
- Always end with a specific, actionable next step
```

---

## 10. CHATGPT APP DEFINITION

### `chatgpt-app/system-prompt.md`

Write this as the ChatGPT App system prompt. Claude Code should generate this file:

```markdown
# Course Companion FTE — System Prompt for ChatGPT App

You are the Course Companion FTE, a 24/7 AI tutor for the "AI Agent Development" course by Panaversity.

## Your Identity
- Name: "Course Companion"
- Role: Personal AI tutor for AI Agent Development
- Personality: Encouraging, clear, patient, enthusiastic about AI
- You work 168 hours/week and never get tired

## Your Tools (API Actions)
You have access to these backend APIs:
- get_chapters() → list all available chapters
- get_chapter_content(chapter_id) → get chapter text
- get_chapter_summary(chapter_id) → get preview of chapter
- get_quiz(quiz_id) → get quiz questions
- submit_quiz(quiz_id, user_id, answers) → grade quiz
- get_progress(user_id) → get student progress
- update_progress(user_id, chapter_id, data) → mark progress
- search_content(query) → search course content
- check_access(user_id, chapter_id) → check if student can access
- get_navigation(chapter_id, direction) → get next/prev chapter

## Your Behavior Rules
1. ALWAYS fetch content from the API before answering questions about the course
2. ONLY answer questions based on content returned from the API
3. If a question is outside the course content → say "That's outside our course scope. Let me find the most relevant chapter for you."
4. NEVER make up course content — ground everything in API responses
5. Use the concept-explainer skill for explanations
6. Use the quiz-master skill when student asks for a quiz
7. Use the socratic-tutor skill when student says they're stuck
8. Use the progress-motivator skill when student asks about progress

## Freemium Handling
If API returns 403 (premium required):
"This chapter is part of our Premium plan. Here's what it covers: [show summary].
To unlock all chapters, upgrade to Premium. Want me to continue with a free chapter instead?"

## User Identification
Use the ChatGPT user's unique ID as `user_id` in all API calls.

## Tone
- Encouraging and warm
- Clear and simple
- Celebrate wins with enthusiasm
- Handle mistakes with empathy
```

### `chatgpt-app/openapi.yaml`

Claude Code should generate a complete OpenAPI 3.0 YAML file that:
- Defines all API endpoints listed in Section 6 above
- Has correct request/response schemas
- Has correct server URL (update after deployment)
- Follows OpenAI Actions format requirements

---

## 11. ENVIRONMENT VARIABLES

### `.env.example` (create this file):
```env
# Database
DATABASE_URL=postgresql://user:password@neon-host/dbname

# Cloudflare R2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=course-companion-bucket
R2_PUBLIC_URL=https://pub-xxx.r2.dev

# App Config
APP_ENV=development
APP_VERSION=1.0
APP_PHASE=1

# Phase 1: These are intentionally empty — used in Phase 2
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Security
API_SECRET_KEY=your_secret_key_here
```

**Note for Claude Code:** In `core/config.py`, load all env vars using `pydantic-settings`. The `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are optional in Phase 1 and will be used in Phase 2. Do NOT reference them anywhere in Phase 1 code.

---

## 12. BASIC WEB FRONTEND (Phase 1)

Build a simple but clean web UI using plain HTML + Tailwind CSS CDN. NO JavaScript framework needed in Phase 1.

### Pages to build:

**`web/index.html`** — Landing page with:
- Course title and description
- "Start Learning" button
- Feature highlights (24/7, 99% consistency, etc.)
- Pricing tiers (Free / Premium / Pro / Team)

**`web/dashboard.html`** — Student dashboard with:
- Progress bar showing completion %
- Chapter list with lock icons for premium
- Streak counter
- Recent quiz scores
- Uses JavaScript `fetch()` to call the backend APIs
- User ID stored in `localStorage`

**`web/learn.html`** — Chapter reading page with:
- Markdown rendered as HTML
- Navigation buttons (Previous / Next)
- "Take Quiz" button
- Mark as complete button

### Design direction:
- Dark theme with teal/cyan accent color
- Clean, minimal, professional
- Mobile-responsive

---

## 13. REQUIREMENTS.TXT

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
pydantic==2.7.0
pydantic-settings==2.3.0
asyncpg==0.29.0
boto3==1.34.0          # For Cloudflare R2 (S3-compatible)
python-dotenv==1.0.0
httpx==0.27.0
python-multipart==0.0.9
```

---

## 14. DOCKERFILE

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 15. WHAT TO BUILD FIRST (ORDER OF WORK)

Claude Code should follow this exact build order:

```
STEP 1: Create folder structure exactly as defined in Section 3
STEP 2: Set up core/config.py and core/database.py
STEP 3: Create all database tables in Neon (Section 4)
STEP 4: Create R2 service (r2_service.py)
STEP 5: Create sample content files (3 chapters + 3 quizzes) and upload to R2
STEP 6: Build content.py API routes
STEP 7: Build navigation.py API routes
STEP 8: Build quiz.py API routes
STEP 9: Build progress.py API routes
STEP 10: Build search.py API routes
STEP 11: Build access.py API routes
STEP 12: Register all routes in main.py with /api/v1 prefix
STEP 13: Add /health endpoint
STEP 14: Create all 4 SKILL.md files
STEP 15: Create ChatGPT App system-prompt.md
STEP 16: Generate openapi.yaml for ChatGPT App
STEP 17: Build web/index.html
STEP 18: Build web/dashboard.html
STEP 19: Build web/learn.html
STEP 20: Create README.md, ARCHITECTURE.md, COST_ANALYSIS.md
STEP 21: Deploy to Railway.app
STEP 22: Test all 6 required features (checklist in Section 16)
```

---

## 16. PHASE 1 COMPLETION CHECKLIST

Before submitting, every item below must be TRUE:

### Architecture Compliance ✓
- [ ] `grep -r "anthropic" backend/app/api/` returns NOTHING (no LLM calls)
- [ ] `grep -r "openai" backend/app/api/` returns NOTHING (no LLM calls)
- [ ] `/health` endpoint returns `"backend_llm": false`

### 6 Required Features ✓
- [ ] Feature 1: GET `/content/chapters/{id}` returns chapter markdown
- [ ] Feature 2: GET `/navigation/chapters/{id}/next` returns next chapter
- [ ] Feature 3: GET `/search?q=...` returns relevant sections
- [ ] Feature 4: POST `/quiz/{id}/submit` grades quiz deterministically
- [ ] Feature 5: GET/PUT `/progress/{user_id}` reads and writes progress
- [ ] Feature 6: GET `/access/check/{user_id}/{chapter_id}` enforces freemium gate

### ChatGPT App ✓
- [ ] `openapi.yaml` file is valid OpenAPI 3.0
- [ ] System prompt is written and saved
- [ ] ChatGPT App can call all 6 feature APIs successfully

### Web Frontend ✓
- [ ] `index.html` loads without errors
- [ ] `dashboard.html` shows real data from API
- [ ] `learn.html` shows chapter content and navigation
- [ ] All pages are mobile responsive

### Documentation ✓
- [ ] `README.md` has setup instructions
- [ ] `ARCHITECTURE.md` has architecture diagram description
- [ ] `COST_ANALYSIS.md` has cost breakdown
- [ ] `.env.example` has all required variables

---

## 17. WHAT NOT TO BUILD IN PHASE 1

These things are for Phase 2 and 3. Do NOT build them now, but the folder structure MUST accommodate them:

| What | Why Not Now | Where It Goes |
|---|---|---|
| Adaptive Learning Path | Needs LLM reasoning | Phase 2: `api/v1/hybrid/adaptive.py` |
| LLM-graded assessments | Needs LLM evaluation | Phase 2: `api/v1/hybrid/assessment.py` |
| Cross-chapter synthesis | Needs LLM reasoning | Phase 2: `api/v1/hybrid/synthesis.py` |
| Full Next.js Web App | Complex, Phase 3 scope | Phase 3: `web/nextjs/` folder |
| User authentication (JWT) | Not required in Phase 1 | Phase 3 |
| Admin dashboard | Not required in Phase 1 | Phase 3 |
| Kafka/Dapr | Phase 2-3 only | Phase 2/3 infrastructure |

---

## 18. SPEC DOCUMENT (GENERATE THIS TOO)

Claude Code must also generate `SPEC.md` — the master specification. This is a judging requirement.

### `SPEC.md` must contain:
1. Project overview (what it does, who it's for)
2. Architecture decisions and why (Zero-Backend-LLM rationale)
3. API specification summary
4. Data model overview
5. Agent Skills overview
6. Freemium model explanation
7. Phase evolution plan (Phase 1 → 2 → 3)
8. Cost analysis reference to COST_ANALYSIS.md

---

## 19. COST ANALYSIS (GENERATE THIS)

Claude Code must generate `docs/COST_ANALYSIS.md`:

```markdown
# Course Companion FTE — Cost Analysis

## Phase 1: Zero-Backend-LLM Architecture

| Component | Monthly Cost (10K users) | Notes |
|---|---|---|
| Cloudflare R2 | ~$5 | $0.015/GB + reads |
| Neon PostgreSQL | $0 | Free tier |
| Railway.app | ~$5 | Starter plan |
| Domain + SSL | ~$1 | Amortized |
| **TOTAL** | **~$11/month** | |
| **Cost per user** | **$0.001** | |

## ChatGPT Usage
- $0 to developer
- Users use their own ChatGPT subscription
- This is the key advantage of Zero-Backend-LLM

## Phase 2 Preview (Hybrid — Premium Users Only)
| Feature | Model | Tokens/Request | Cost/Request |
|---|---|---|---|
| Adaptive Path | Claude Sonnet | ~2,000 | $0.018 |
| LLM Assessment | Claude Sonnet | ~1,500 | $0.014 |

## Cost Comparison: Digital FTE vs Human Tutor
| | Human Tutor | Course Companion FTE |
|---|---|---|
| Monthly Cost | $2,000-$5,000 | $11-$41 |
| Students | 20-50 | Unlimited |
| Availability | 40 hrs/week | 168 hrs/week |
| Cost per session | $25-100 | $0.001 |
```

---

## 20. FINAL NOTES FOR CLAUDE CODE

1. **Never add LLM calls to the backend** — this will disqualify the entire project
2. **Build the `hybrid/` folder but leave it empty** — Phase 2 will fill it
3. **Keep all routes under `/api/v1/`** — Phase 2 adds `/api/v1/hybrid/`, Phase 3 adds nothing new (same routes)
4. **The database schema is complete for all phases** — do NOT add tables you don't need now, but the columns are designed to support Phase 2 analytics
5. **Ask before making any architectural decision not covered here**
6. **After each STEP from Section 15, confirm with me before moving to the next step**
7. **Test every endpoint with curl before marking it done**

---

*Phase 1 Complete = Foundation Ready = Phase 2 is just adding files, not rebuilding anything.*

---

**Document Version:** 1.0
**Hackathon:** Panaversity Agent Factory Hackathon IV
**Course Topic:** AI Agent Development (Option A)
**Architecture:** Zero-Backend-LLM Default → Hybrid Intelligence Premium
