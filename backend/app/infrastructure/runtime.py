from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


class UuidIdentifierGenerator:
    def new_identifier(self, prefix: str) -> str:
        normalized_prefix = prefix.strip().lower()
        if not normalized_prefix or not normalized_prefix.replace("-", "").isalnum():
            raise ValueError("identifier prefix must contain lowercase letters, digits or hyphens")
        return f"{normalized_prefix}-{uuid4().hex}"
