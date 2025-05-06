from __future__ import annotations
from datetime import datetime

import faiss

from app.core.embeddings import EmbeddingStore
from app.schemas.api import QueryReq


def _date_ok(date_iso: str | None, start: str | None, end: str | None) -> bool:
    if not date_iso:
        return False
    dt = datetime.fromisoformat(date_iso)
    if start and dt < datetime.fromisoformat(start):
        return False
    if end and dt > datetime.fromisoformat(end):
        return False
    return True


def filter_and_rank(req: QueryReq, store: EmbeddingStore):
    """
    Apply sender / date filtering, then run kNN on the FAISS index.
    Returns a list of (snippet_text, meta_dict) tuples.
    """
    q = req.question
    k = req.k

    if not (req.sender or req.start or req.end):
        qv = store.model.encode([q], convert_to_numpy=True)
        _, search = store.index.search(qv, min(k, len(store.texts)))
        return [(store.texts[i], store.meta[i]) for i in search[0]]

    valid_idx: list[int] = []
    for i, m in enumerate(store.meta):
        if req.sender and req.sender.lower() not in m["sender"].lower():
            continue
        if not _date_ok(m["date"], req.start, req.end):
            continue
        valid_idx.append(i)

    if not valid_idx:
        return []

    sub_embeds = store.embeds[valid_idx]
    sub_texts = [store.texts[i] for i in valid_idx]
    sub_meta = [store.meta[i] for i in valid_idx]

    sub_idx = faiss.IndexFlatL2(sub_embeds.shape[1])
    sub_idx.add(sub_embeds)

    qv = store.model.encode([q], convert_to_numpy=True)
    _, search = sub_idx.search(qv, min(k, len(sub_texts)))
    return [(sub_texts[i], sub_meta[i]) for i in search[0]]
