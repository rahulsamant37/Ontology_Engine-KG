from __future__ import annotations

from db.vector_store import VectorIndex, VectorRecord
from ingestion.normalizer import normalize_payload
from models.schemas import IngestResult, RawIngestRequest
from utils.logging import get_logger

logger = get_logger(__name__)


class IngestionService:
    def __init__(self, vector_index: VectorIndex) -> None:
        self.vector_index = vector_index

    def ingest(self, request: RawIngestRequest) -> tuple[IngestResult, dict]:
        normalized = normalize_payload(
            source=request.source,
            payload=request.payload,
            payload_type=request.payload_type,
        )

        metric_names = [metric.get("name", "") for metric in normalized.get("metrics", []) if metric.get("name")]
        text_parts = [normalized.get("title", ""), normalized.get("text", "")]
        if metric_names:
            text_parts.append(f"metrics: {', '.join(metric_names)}")
        text = " | ".join(part for part in text_parts if part).strip() or str(normalized.get("metrics"))

        metadata = {
            "source": request.source,
            "timestamp": normalized["timestamp"],
            "payload_type": str(normalized.get("payload_type", "auto")),
            "event_type": str(normalized.get("event_type", "")),
            "country": str(normalized.get("country", "India")),
            "tags": ",".join(normalized.get("tags", [])),
            "entities": ",".join(normalized.get("entities", [])),
            "metric_names": ",".join(metric_names),
        }

        self.vector_index.add(
            [
                VectorRecord(
                    text=text,
                    metadata=metadata,
                )
            ]
        )

        logger.info("Ingested payload from source=%s", request.source)
        return (
            IngestResult(
                status="success",
                ingested_items=1,
                message=f"Ingested data from {request.source}",
            ),
            normalized,
        )
