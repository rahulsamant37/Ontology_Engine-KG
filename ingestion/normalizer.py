from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from ingestion.text_transformer import OntologyTextTransformer
from models.schemas import StructuredEventPayload, UnstructuredTextPayload


_TEXT_TRANSFORMER = OntologyTextTransformer()


def _resolve_payload_type(payload: dict[str, Any], payload_type: str) -> str:
    if payload_type in {"structured", "unstructured"}:
        return payload_type

    if any(marker in payload for marker in {"event_type", "country", "entities"}):
        return "structured"

    metrics = payload.get("metrics")
    if isinstance(metrics, list) and metrics:
        return "structured"

    return "unstructured"


def _normalize_structured(source: str, payload: dict[str, Any], fallback_timestamp: str) -> dict[str, Any]:
    structured = StructuredEventPayload.model_validate(payload)
    timestamp = structured.timestamp.isoformat() if structured.timestamp else fallback_timestamp

    return {
        "source": source,
        "payload_type": "structured",
        "timestamp": timestamp,
        "title": structured.title,
        "text": structured.text or structured.title,
        "event_type": structured.event_type,
        "country": structured.country,
        "metrics": [metric.model_dump() for metric in structured.metrics],
        "tags": structured.tags,
        "entities": structured.entities,
    }


def _normalize_unstructured(source: str, payload: dict[str, Any], fallback_timestamp: str) -> dict[str, Any]:
    unstructured = UnstructuredTextPayload.model_validate(payload)
    raw_text = (unstructured.raw_text or unstructured.text or "").strip()
    transformed = _TEXT_TRANSFORMER.transform(raw_text)
    title = unstructured.title.strip() or transformed["title"]

    return {
        "source": source,
        "payload_type": "unstructured",
        "timestamp": fallback_timestamp,
        "title": title,
        "text": transformed["text"],
        "event_type": transformed["event_type"],
        "country": transformed["country"],
        "metrics": transformed["metrics"],
        "tags": transformed["tags"],
        "entities": transformed["entities"],
        "language": unstructured.language,
        "metadata": unstructured.metadata,
    }


def normalize_payload(source: str, payload: dict[str, Any], payload_type: str = "auto") -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    resolved_type = _resolve_payload_type(payload=payload, payload_type=payload_type)

    try:
        if resolved_type == "structured":
            return _normalize_structured(source=source, payload=payload, fallback_timestamp=timestamp)
        return _normalize_unstructured(source=source, payload=payload, fallback_timestamp=timestamp)
    except ValidationError as exc:
        msg = f"Payload validation failed for {resolved_type} input: {exc.errors()}"
        raise ValueError(msg) from exc
