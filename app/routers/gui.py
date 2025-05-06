from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.embeddings import store

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


from app.routers.auth import require_login


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, _: str = Depends(require_login)):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/senders", response_model=list[str])
async def list_senders():
    """Return unique senders for the dropdown."""
    return sorted({m["sender"] for m in store.meta if m["sender"]})
