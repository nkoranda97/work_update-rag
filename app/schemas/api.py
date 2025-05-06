from __future__ import annotations
from pydantic import BaseModel, Field, RootModel 


class QueryReq(BaseModel):
    question: str = Field(..., examples=["Summarize Andy's trimer work in 2020"])
    sender: str | None = None
    start: str | None = Field(None, description="ISO‑8601 start date")
    end: str | None = Field(None, description="ISO‑8601 end date")
    k: int = Field(10, ge=1, le=50, description="Top‑k snippets")


class QueryRes(BaseModel):
    answer: str
    snippets: list[str]


class SenderList(RootModel[list[str]]): 
    """Schema for /senders endpoint (list of strings)."""

    pass
