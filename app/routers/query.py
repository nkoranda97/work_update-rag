from fastapi import APIRouter, HTTPException
from app.schemas.api import QueryReq, QueryRes
from app.core.embeddings import store
from app.services.search import filter_and_rank
from app.services.llm import answer_with_openai

router = APIRouter()


@router.post("/query", response_model=QueryRes)
async def query(req: QueryReq):
    matches = filter_and_rank(req, store)
    if not matches:
        raise HTTPException(404, "No matches")

    snippets = [t for t, _ in matches]
    answer = answer_with_openai(req.question, snippets)

    return QueryRes(answer=answer, snippets=snippets)
