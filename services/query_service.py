from __future__ import annotations

from agents.workflow import FinancialWorkflow, WorkflowState
from db.neo4j_client import GraphRepository
from db.postgres_client import InsightRepository
from db.vector_store import VectorIndex
from models.schemas import Insight, QueryRequest
from utils.logging import get_logger

logger = get_logger(__name__)


class QueryService:
    def __init__(
        self,
        workflow: FinancialWorkflow,
        vector_index: VectorIndex,
        insight_repository: InsightRepository,
        graph_repo: GraphRepository,
    ) -> None:
        self.workflow = workflow
        self.vector_index = vector_index
        self.insight_repository = insight_repository
        self.graph_repo = graph_repo

    def answer(self, request: QueryRequest) -> tuple[Insight, list[str]]:
        retrieved_docs = self.vector_index.search(request.question)
        initial_state: WorkflowState = {
            "question": request.question,
            "retrieved_docs": retrieved_docs,
            "logs": [],
        }

        final_state = self.workflow.run(initial_state)
        insight = Insight(**final_state["insight"])

        self.insight_repository.save_insight(question=request.question, payload=insight)
        logger.info("Query answered: %s", request.question)
        return insight, final_state.get("logs", [])

    def latest_insights(self):
        return self.insight_repository.list_insights()

    def graph_snapshot(self):
        return self.graph_repo.snapshot()
