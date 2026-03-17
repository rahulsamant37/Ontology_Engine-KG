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
        normalized = normalize_payload(source=request.source, payload=request.payload)
        text = normalized.get("text") or normalized.get("title") or str(normalized.get("metrics"))

        self.vector_index.add(
            [
                VectorRecord(
                    text=text,
                    metadata={"source": request.source, "timestamp": normalized["timestamp"]},
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
