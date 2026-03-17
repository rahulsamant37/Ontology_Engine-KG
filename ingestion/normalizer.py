from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def normalize_payload(source: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": payload.get("text", ""),
        "metrics": payload.get("metrics", {}),
        "title": payload.get("title", ""),
    }
