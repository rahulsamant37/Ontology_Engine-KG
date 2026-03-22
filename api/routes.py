from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_ingestion_service, get_public_data_service, get_query_service
from models.schemas import IngestResult, PublicDataIngestRequest, QueryRequest, RawIngestRequest
from services.ingestion_service import IngestionService
from services.public_data_service import PublicDataService
from services.query_service import QueryService

router = APIRouter()


@router.post("/ingest", response_model=IngestResult)
def ingest(
    request: RawIngestRequest,
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        result, _ = service.ingest(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result


@router.post("/ingest/public", response_model=IngestResult)
def ingest_public_data(
    request: PublicDataIngestRequest,
    public_service: PublicDataService = Depends(get_public_data_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    try:
        events = public_service.fetch_structured_events(
            country_code=request.country_code,
            start_year=request.start_year,
            end_year=request.end_year,
            indicators=request.indicators,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    ingested_items = 0
    for event in events:
        try:
            ingest_request = RawIngestRequest.model_validate(event)
            ingestion_service.ingest(ingest_request) # same as /ingestion endpoint
            ingested_items += 1
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return IngestResult(
        status="success",
        ingested_items=ingested_items,
        message=(
            f"Ingested {ingested_items} records from World Bank API for {request.country_code.upper()}"
        ),
    )


@router.post("/query")
def query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service),
):
    # retrive context from vector store, run through workflow and get insight
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
