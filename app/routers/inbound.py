from fastapi import APIRouter, HTTPException
from app.services.email_fetcher import fetch_new_emails
from app.core.embeddings import store

router = APIRouter(tags=["Inbound"])

@router.post("/refresh")
async def refresh_emails():
    """Manually trigger email fetch and embedding refresh."""
    try:
        new_count = fetch_new_emails()
        if new_count > 0:
            store.refresh()
            return {"status": "success", "new_emails": new_count}
        return {"status": "success", "new_emails": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))