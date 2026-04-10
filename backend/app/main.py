from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import startup_db, shutdown_db
from app.api.v1 import content, navigation, quiz, progress, search, access


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_db()
    yield
    # Shutdown
    await shutdown_db()


app = FastAPI(
    title="Course Companion FTE",
    description="Zero-Backend-LLM AI Agent Development Course API — Phase 1",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API v1 routers ──────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(content.router,    prefix=f"{API_PREFIX}/content",    tags=["content"])
app.include_router(navigation.router, prefix=f"{API_PREFIX}/navigation",  tags=["navigation"])
app.include_router(quiz.router,       prefix=f"{API_PREFIX}/quiz",        tags=["quiz"])
app.include_router(progress.router,   prefix=f"{API_PREFIX}/progress",    tags=["progress"])
app.include_router(search.router,     prefix=f"{API_PREFIX}/search",      tags=["search"])
app.include_router(access.router,     prefix=f"{API_PREFIX}/access",      tags=["access"])


# ── Health check ────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "version": "1.0",
        "phase": "1",
        "backend_llm": False,
    }
