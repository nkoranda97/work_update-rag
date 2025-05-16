from __future__ import annotations
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.models.email import EmailRow
from app.services.loader import load_emails, clean


class EmbeddingStore:
    """Holds model, corpus, and FAISS index in memory."""

    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.texts: list[str] = []
        self.meta: list[dict] = []
        self.embeds: np.ndarray = None
        self.index: faiss.Index = None

    def refresh(self, rows: list[EmailRow] | None = None):
        """(Re)load emails, embed, and build FAISS index."""
        if rows is None:
            rows = load_emails(settings.email_dir)

        if self.model is None:
            self.model = SentenceTransformer(settings.embed_model)

        # build corpus
        self.texts = [
            f"SENDER: {r.sender} | DATE: {r.date or 'UNK'} | CONTENT: {clean(r.content)}"
            for r in rows
        ]
        self.meta = [r.to_meta() for r in rows]

        # encode
        self.embeds = self.model.encode(self.texts, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(self.embeds.shape[1])
        self.index.add(self.embeds)

        return rows  # convenient for caller

    def knn(self, query: str, k: int = 10):
        qv, _ = self._encode_query(query)
        _, search = self.index.search(qv, min(k, len(self.texts)))
        return [(self.texts[i], self.meta[i]) for i in search[0]]

    def _encode_query(self, q: str):
        return self.model.encode([q], convert_to_numpy=True), q


store = EmbeddingStore()
