from __future__ import annotations

from langchain_core.documents import Document

from models.schemas import Entity, Relationship


class ReasoningService:
    def build_drivers(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
        retrieved_docs: list[Document],
    ) -> list[str]:
        drivers: list[str] = []

        for entity in entities:
            if entity.name not in drivers:
                drivers.append(entity.name)

        for rel in relationships:
            text = f"{rel.source_id} {rel.relation} {rel.target_id}"
            if text not in drivers:
                drivers.append(text)

        for doc in retrieved_docs:
            snippet = doc.page_content[:100].strip()
            if snippet and snippet not in drivers:
                drivers.append(snippet)

        return drivers[:6]

    def confidence_score(self, relationships: list[Relationship], retrieved_docs: list[Document]) -> float:
        raw = 0.35 + (0.1 * min(len(relationships), 4)) + (0.08 * min(len(retrieved_docs), 3))
        return round(min(0.95, raw), 2)
