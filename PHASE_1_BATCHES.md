# Phase 1 — Claude Code Batch Prompts
### Course Companion FTE | Panaversity Agent Factory Hackathon IV

---

> **HOW TO USE THIS FILE**
> 1. Both `PHASE_1_PROMPT.md` and this file must be in your project root folder
> 2. Copy ONE batch at a time → paste into Claude Code → wait for completion → review → then move to next batch
> 3. Never skip a batch — each one depends on the previous
> 4. If Claude Code asks a question not covered here → refer it back to `PHASE_1_PROMPT.md`

---

## BATCH 1 — Project Setup, Folders, Config, Database

```
Read PHASE_1_PROMPT.md fully before doing anything.

Now do Batch 1:

1. Create the complete folder structure exactly as defined in Section 3 of PHASE_1_PROMPT.md. Create all folders and empty placeholder files including the empty hybrid/ folder with .gitkeep.

2. Create backend/app/core/config.py using pydantic-settings. Load all environment variables defined in Section 11 of PHASE_1_PROMPT.md. ANTHROPIC_API_KEY and OPENAI_API_KEY must be optional fields with default None — they are NOT used in Phase 1.

3. Create backend/app/core/database.py with asyncpg connection pool to Neon PostgreSQL. Use the DATABASE_URL from config.

4. Create backend/requirements.txt exactly as defined in Section 13 of PHASE_1_PROMPT.md.

5. Create backend/.env.example exactly as defined in Section 11 of PHASE_1_PROMPT.md.

6. Create backend/Dockerfile exactly as defined in Section 14 of PHASE_1_PROMPT.md.

7. Create all 5 database tables in Neon PostgreSQL exactly as defined in Section 4 of PHASE_1_PROMPT.md:
   - users
   - progress
   - streaks
   - quiz_attempts
   - content_metadata

8. Create backend/app/main.py as the FastAPI entry point. Register all routers under /api/v1 prefix. Add the /health endpoint that returns {"status": "ok", "version": "1.0", "phase": "1", "backend_llm": false}.

After completing all 8 tasks, confirm each one is done and show me the folder structure using tree command.
```

---

## BATCH 2 — R2 Storage Service + Course Content

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 2:

1. Create backend/app/services/r2_service.py using boto3 (S3-compatible client for Cloudflare R2). Implement these 4 functions as defined in Section 5 of PHASE_1_PROMPT.md:
   - get_chapter(chapter_id) → fetch markdown from R2
   - list_chapters() → list all chapter keys
   - upload_content(key, content) → upload content to R2
   - Add 5-minute in-memory cache to reduce R2 reads

2. Create all content files locally in backend/content/ folder:

   Create 3 free chapter markdown files (chapter-01.md, chapter-02.md, chapter-03.md) using the structure defined in Section 8 of PHASE_1_PROMPT.md. Each chapter must:
   - Be about AI Agent Development (Option A course topic)
   - Have frontmatter (chapter_id, title, order, tier, estimated_minutes, tags)
   - Be 800-1000 words of real, useful educational content
   - Chapter 1: AI Agents and Digital FTEs Introduction
   - Chapter 2: Claude Agent SDK Deep Dive
   - Chapter 3: MCP and Agent Skills

   Create 3 premium chapter placeholder files (chapter-04.md, chapter-05.md, chapter-06.md) with:
   - Correct frontmatter with tier: premium or pro
   - At least 200 words of real content

3. Create 3 quiz JSON files (quiz-01.json, quiz-02.json, quiz-03.json) in backend/content/quizzes/ using EXACTLY the format defined in Section 7 of PHASE_1_PROMPT.md. Each quiz must have 5 MCQ questions about the corresponding chapter topic.

4. Create a script backend/scripts/upload_content.py that uploads all chapter markdown files and quiz JSON files to Cloudflare R2 in the correct folder structure defined in Section 5 of PHASE_1_PROMPT.md.

5. Insert all 6 chapters into the content_metadata table in Neon with correct order_index, tier_required, r2_key, and tags values.

After completing, confirm each task and show me a sample of chapter-01.md content.
```

---

## BATCH 3 — Content + Navigation + Search APIs

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 3:

1. Create all Pydantic schemas in backend/app/schemas/:
   - schemas/content.py → ChapterMetadata, ChapterContent, ChapterList
   - schemas/quiz.py → QuizQuestion, QuizSubmission, QuizResult
   - schemas/progress.py → UserProgress, ProgressUpdate, StreakInfo

2. Create backend/app/models/ files:
   - models/user.py
   - models/progress.py
   - models/quiz_attempt.py
   Using asyncpg (NOT SQLAlchemy) — raw SQL queries only.

3. Create backend/app/api/v1/content.py with these 3 routes exactly as defined in Section 6.1 of PHASE_1_PROMPT.md:
   - GET /content/chapters → list all chapters with metadata
   - GET /content/chapters/{chapter_id} → serve full markdown (checks access first, updates progress after serving)
   - GET /content/chapters/{chapter_id}/summary → first 200 words preview

4. Create backend/app/api/v1/navigation.py with these 3 routes exactly as defined in Section 6.2 of PHASE_1_PROMPT.md:
   - GET /navigation/chapters/{chapter_id}/next
   - GET /navigation/chapters/{chapter_id}/prev
   - GET /navigation/chapters/sequence

5. Create backend/app/services/search_service.py using PostgreSQL full-text search (tsvector/tsquery) or ILIKE fallback.

6. Create backend/app/api/v1/search.py with this route as defined in Section 6.5 of PHASE_1_PROMPT.md:
   - GET /search?q={query}&user_id={user_id}

7. Register content, navigation, and search routers in main.py.

8. Test all routes with curl commands and show me the output for:
   - GET /api/v1/content/chapters
   - GET /api/v1/navigation/chapters/chapter-01/next
   - GET /api/v1/search?q=agent&user_id=test_user
```

---

## BATCH 4 — Quiz, Progress, and Access Control APIs

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 4:

1. Create backend/app/services/quiz_service.py with deterministic grading logic:
   - Load answer key from R2 (quiz JSON file)
   - Compare submitted answers to correct_answer field
   - Calculate score (0-100)
   - Return per-question feedback
   - ZERO LLM calls — pure rule-based comparison

2. Create backend/app/api/v1/quiz.py with these 3 routes exactly as defined in Section 6.3 of PHASE_1_PROMPT.md:
   - GET /quiz/{quiz_id} → questions WITHOUT correct answers
   - POST /quiz/{quiz_id}/submit → grade deterministically, store in quiz_attempts table
   - GET /quiz/chapter/{chapter_id} → get quiz ID for a chapter

3. Create backend/app/services/progress_service.py with:
   - Calculate completion percentage across all chapters
   - Update streak logic (check last_activity_date, increment or reset)
   - Aggregate quiz scores

4. Create backend/app/api/v1/progress.py with these 3 routes exactly as defined in Section 6.4 of PHASE_1_PROMPT.md:
   - GET /progress/{user_id} → full progress summary
   - PUT /progress/{user_id}/chapter/{chapter_id} → update chapter progress
   - GET /progress/{user_id}/streak → streak info only

5. Create backend/app/api/v1/access.py with these 3 routes exactly as defined in Section 6.6 of PHASE_1_PROMPT.md:
   - GET /access/check/{user_id}/{chapter_id} → returns has_access boolean
   - POST /access/users → create or get user (upsert)
   - GET /access/users/{user_id}/tier → return user tier

6. Register quiz, progress, and access routers in main.py.

7. Verify Phase 1 architecture compliance by running:
   grep -r "anthropic" backend/app/api/
   grep -r "openai" backend/app/api/
   Both must return NOTHING.

8. Test all routes with curl and show me output for:
   - POST /api/v1/access/users with body {"user_id": "test_user_001"}
   - GET /api/v1/access/check/test_user_001/chapter-01
   - GET /api/v1/access/check/test_user_001/chapter-04
   - POST /api/v1/quiz/quiz-01/submit with sample answers
   - GET /api/v1/progress/test_user_001
```

---

## BATCH 5 — Agent Skills (SKILL.md Files)

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 5:

Create all 4 Agent Skill files in backend/skills/ folder.
Use EXACTLY the content defined in Section 9 of PHASE_1_PROMPT.md.
Do not summarize or shorten them — write the full content for each:

1. backend/skills/concept-explainer.md
   - Full metadata, purpose, workflow, response templates, key principles
   - As defined in Section 9 of PHASE_1_PROMPT.md

2. backend/skills/quiz-master.md
   - Full metadata, purpose, workflow, response templates for correct/wrong/complete
   - As defined in Section 9 of PHASE_1_PROMPT.md

3. backend/skills/socratic-tutor.md
   - Full metadata, purpose, workflow, response template, key principles
   - As defined in Section 9 of PHASE_1_PROMPT.md

4. backend/skills/progress-motivator.md
   - Full metadata, purpose, workflow, all 3 response templates (high/mid/starting)
   - As defined in Section 9 of PHASE_1_PROMPT.md

After creating all 4 files, show me the content of each file to confirm they are complete and correctly formatted.
```

---

## BATCH 6 — ChatGPT App Definition

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 6:

1. Create chatgpt-app/system-prompt.md using EXACTLY the content defined in Section 10 of PHASE_1_PROMPT.md. This is the system prompt for the ChatGPT App. Make sure:
   - All 10 tool names (API actions) are listed correctly
   - All behavior rules are included
   - Freemium handling message is included
   - All 4 skill references are included

2. Create chatgpt-app/openapi.yaml — a complete, valid OpenAPI 3.0 spec for ALL API routes built in Batches 3 and 4. This file must:
   - Follow OpenAI Actions format exactly
   - Define every route from Sections 6.1 through 6.7 of PHASE_1_PROMPT.md
   - Include correct request bodies and response schemas
   - Use placeholder server URL: https://your-backend.railway.app
   - Be valid (no YAML errors)

3. Create chatgpt-app/privacy.md with a simple privacy policy stating:
   - What data is stored (user_id, progress, quiz scores)
   - What data is NOT stored (no personal data beyond user_id)
   - Contact information placeholder

4. Validate the openapi.yaml file is correct by checking its structure. Show me the first 50 lines of the generated openapi.yaml file.
```

---

## BATCH 7 — Web UI + Documentation + Final Check

```
Refer to PHASE_1_PROMPT.md.

Now do Batch 7 (final batch):

1. Create web/index.html — landing page using plain HTML + Tailwind CSS CDN as defined in Section 12 of PHASE_1_PROMPT.md:
   - Dark theme with teal/cyan accent
   - Course title and description
   - Feature highlights (24/7, 99% consistency, cost comparison)
   - Pricing tiers (Free / Premium / Pro / Team) with features listed
   - "Start Learning" button that goes to dashboard.html
   - Mobile responsive

2. Create web/dashboard.html — student dashboard:
   - Progress bar showing completion percentage
   - Chapter list with lock icons for premium chapters
   - Streak counter (days)
   - Recent quiz scores table
   - Uses JavaScript fetch() to call backend APIs
   - User ID stored in localStorage (generate random UUID if none exists)
   - Mobile responsive

3. Create web/learn.html — chapter reading page:
   - Renders markdown as HTML (use marked.js CDN)
   - Previous / Next navigation buttons
   - "Take Quiz" button
   - "Mark as Complete" button
   - Shows chapter title and estimated reading time
   - Mobile responsive

4. Generate docs/ARCHITECTURE.md describing:
   - Zero-Backend-LLM architecture diagram (text-based)
   - All layers (L3 FastAPI + L6 Skills + MCP)
   - Data flow: User → ChatGPT App → Backend → R2/Neon
   - Phase evolution path (Phase 1 → 2 → 3)

5. Generate docs/COST_ANALYSIS.md using EXACTLY the template defined in Section 19 of PHASE_1_PROMPT.md.

6. Generate SPEC.md master specification document covering all 8 points defined in Section 18 of PHASE_1_PROMPT.md.

7. Generate README.md with:
   - Project overview
   - Tech stack
   - Setup instructions (clone → .env → pip install → run)
   - API endpoints summary
   - How to use the ChatGPT App
   - Link to SPEC.md and COST_ANALYSIS.md

8. Run the complete Phase 1 checklist from Section 16 of PHASE_1_PROMPT.md and show me the result of every single item — confirmed ✅ or failed ❌ with reason.

After completing all tasks, give me a final summary:
- Total files created
- All API routes working (list them)
- Any items that need my attention before submission
```

---

## AFTER ALL 7 BATCHES — Deploy Prompt

Once all 7 batches are done and checklist passes, use this final prompt:

```
Refer to PHASE_1_PROMPT.md.

Help me deploy to Railway.app:

1. Make sure Dockerfile is correct and builds successfully
2. List all environment variables I need to set in Railway dashboard
3. Give me exact steps to:
   - Push code to GitHub
   - Connect Railway to GitHub repo
   - Set environment variables in Railway
   - Deploy and get the live URL
4. After deployment, update the server URL in chatgpt-app/openapi.yaml to the real Railway URL
5. Give me instructions to register the ChatGPT App on platform.openai.com using the openapi.yaml and system-prompt.md
```

---

*Phase 1 complete → Start Phase 2 prompt file when ready.*
