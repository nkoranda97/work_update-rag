from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EmailRow:
    sender: str
    date: str | None
    content: str

    @property
    def parsed_date(self) -> datetime | None:
        from datetime import datetime

        return datetime.fromisoformat(self.date) if self.date else None

    def to_meta(self) -> dict:
        return {"sender": self.sender, "date": self.date}
