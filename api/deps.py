from __future__ import annotations

from functools import lru_cache

from agents.workflow import FinancialWorkflow
from db.neo4j_client import GraphRepository
from db.postgres_client import InsightRepository
from db.vector_store import VectorIndex
from services.extraction_service import ExtractionService
from services.ingestion_service import IngestionService
from services.insight_service import InsightService
from services.public_data_service import PublicDataService
from services.query_service import QueryService
from services.reasoning_service import ReasoningService


@lru_cache
def get_vector_index() -> VectorIndex:
    return VectorIndex()


@lru_cache
def get_graph_repository() -> GraphRepository:
    return GraphRepository()


@lru_cache
def get_insight_repository() -> InsightRepository:
    repository = InsightRepository()
    repository.initialize()
    return repository


@lru_cache
def get_extraction_service() -> ExtractionService:
    return ExtractionService()


@lru_cache
def get_reasoning_service() -> ReasoningService:
    return ReasoningService()


@lru_cache
def get_insight_service() -> InsightService:
    return InsightService()


@lru_cache
def get_workflow() -> FinancialWorkflow:
    return FinancialWorkflow(
        extraction_service=get_extraction_service(),
        reasoning_service=get_reasoning_service(),
        insight_service=get_insight_service(),
        graph_repo=get_graph_repository(),
    )


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(vector_index=get_vector_index())


@lru_cache
def get_public_data_service() -> PublicDataService:
    return PublicDataService()


@lru_cache
def get_query_service() -> QueryService:
    return QueryService(
        workflow=get_workflow(),
        vector_index=get_vector_index(),
        insight_repository=get_insight_repository(),
        graph_repo=get_graph_repository(),
    )
