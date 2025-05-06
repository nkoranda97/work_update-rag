from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.embeddings import store
from app.routers import query, gui


# ────────────── lifespan (startup/shutdown) ────────────── #
@asynccontextmanager
async def lifespan(app: FastAPI):
    rows = store.refresh()  # build FAISS index
    app.state.senders = sorted({r.sender for r in rows if r.sender})
    print(f"[startup] loaded {len(rows)} emails — index ready")

    yield  

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

app.include_router(query.router)
app.include_router(gui.router)
