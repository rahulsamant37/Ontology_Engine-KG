from __future__ import annotations

from fastapi import APIRouter, Depends

from api.deps import get_ingestion_service, get_query_service
from models.schemas import IngestResult, QueryRequest, RawIngestRequest
from services.ingestion_service import IngestionService
from services.query_service import QueryService

router = APIRouter()


@router.post("/ingest", response_model=IngestResult)
def ingest(
    request: RawIngestRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    result, _ = service.ingest(request)
    return result


@router.post("/query")
def query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service),
):
    insight, logs = service.answer(request)
    return {
        **insight.model_dump(),
        "reasoning_logs": logs,
    }


@router.get("/insights")
def insights(service: QueryService = Depends(get_query_service)):
    records = service.latest_insights()
    return [record.model_dump() for record in records]


@router.get("/graph")
def graph(service: QueryService = Depends(get_query_service)):
    snapshot = service.graph_snapshot()
    return snapshot.model_dump()
