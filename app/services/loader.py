from __future__ import annotations
import os
import re
from datetime import timezone
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

from app.models.email import EmailRow
from app.core.config import settings

_strip_tags = re.compile(r"<[^>]+>").sub


def strip_html(text: str) -> str:
    return _strip_tags("", text)


def clean(text: str) -> str:
    """Condense whitespace so the LLM prompt is compact."""
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())


def load_emails(folder: str | None = None) -> list[EmailRow]:
    """
    Parse all .eml files in *folder* and return a sorted list of EmailRow.
    """
    folder = folder or settings.email_dir
    rows: list[EmailRow] = []

    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".eml"):
            continue
        path = os.path.join(folder, fname)
        try:
            with open(path, "rb") as fh:
                msg = BytesParser(policy=policy.default).parse(fh)

            # sender
            raw = msg.get("From", "")
            sender = " ".join(raw.split("<", 1)[0].split()).replace('"', "").strip()

            try:
                dt = parsedate_to_datetime(msg.get("Date"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                date = dt.astimezone(timezone.utc).isoformat()
            except Exception:
                date = None

            # body
            body = (
                msg.get_body(preferencelist=("plain", "html")).get_content()
                if msg.is_multipart()
                else msg.get_content()
            )
            if msg.is_multipart() and msg.get_body().get_content_type() == "text/html":
                body = strip_html(body)
            body = body.strip()

            if body:
                rows.append(EmailRow(sender, date, body))

        except Exception as exc:
            print("[PARSE ERROR]", fname, exc)

    rows.sort(key=lambda r: r.date or "")
    return rows

