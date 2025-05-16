from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.embeddings import store
from app.routers import query, gui, auth, inbound
from app.core.config import settings
from app.services.email_fetcher import fetch_new_emails

SECRET_KEY = settings.secret_key

# Initialize scheduler
scheduler = AsyncIOScheduler()

async def daily_refresh():
    """Fetch new emails and refresh embeddings."""
    try:
        new_count = fetch_new_emails()
        if new_count > 0:
            store.refresh()
            print(f"[scheduler] Processed {new_count} new emails")
    except Exception as e:
        print(f"[scheduler] Error during refresh: {e}")

# ────────────── lifespan (startup/shutdown) ────────────── #
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initial load
    rows = store.refresh()  # build FAISS index
    app.state.senders = sorted({r.sender for r in rows if r.sender})
    print(f"[startup] loaded {len(rows)} emails — index ready")

    # Start scheduler
    scheduler.add_job(daily_refresh, CronTrigger(hour=2))  # Run at 2am
    scheduler.start()
    print("[startup] scheduler started")

    yield

    scheduler.shutdown()
    print("[shutdown] done")


app = FastAPI(
    title="Email‑RAG",
    version="0.5.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(gui.router)
#app.include_router(inbound.router)
