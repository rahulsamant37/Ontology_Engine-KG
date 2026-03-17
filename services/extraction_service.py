from __future__ import annotations

from collections.abc import Iterable

from langchain_core.runnables import RunnableLambda

from models.ontology import EntityType, RelationType
from models.schemas import Entity, Relationship


KEYWORD_MAP: dict[str, tuple[str, EntityType]] = {
    "rbi": ("Reserve Bank of India", EntityType.INSTITUTION),
    "inflation": ("Inflation", EntityType.ECONOMIC_INDICATOR),
    "cpi": ("CPI", EntityType.ECONOMIC_INDICATOR),
    "bond yield": ("Indian Government Bond Yield", EntityType.ECONOMIC_INDICATOR),
    "nifty": ("NIFTY 50", EntityType.ASSET),
    "oil": ("Crude Oil", EntityType.ASSET),
    "india": ("India", EntityType.COUNTRY),
    "repo rate": ("Repo Rate Decision", EntityType.EVENT),
}


class ExtractionService:
    def __init__(self) -> None:
        self._entity_pipeline = RunnableLambda(self._extract_entities)
        self._event_pipeline = RunnableLambda(self._extract_events)
        self._sentiment_pipeline = RunnableLambda(self._analyze_sentiment)
        self._relation_pipeline = RunnableLambda(self._extract_relationships)

    def extract(self, text: str) -> tuple[list[Entity], list[Relationship]]:
        entities = self._entity_pipeline.invoke(text)
        events = self._event_pipeline.invoke(text)
        sentiment = self._sentiment_pipeline.invoke(text)
        all_entities = self._deduplicate_entities(entities + events)
        for entity in all_entities:
            entity.properties["sentiment"] = sentiment

        relationships = self._relation_pipeline.invoke({"text": text, "entities": all_entities})
        return all_entities, relationships

    def _extract_entities(self, text: str) -> list[Entity]:
        lowered = text.lower()
        entities: list[Entity] = []

        for keyword, (name, entity_type) in KEYWORD_MAP.items():
            if keyword in lowered:
                entity_id = name.lower().replace(" ", "_")
                entities.append(Entity(id=entity_id, name=name, entity_type=entity_type, properties={}))

        if not entities:
            entities.append(
                Entity(
                    id="india",
                    name="India",
                    entity_type=EntityType.COUNTRY,
                    properties={},
                )
            )
        return self._deduplicate_entities(entities)

    def _extract_relationships(self, payload: dict) -> list[Relationship]:
        text = payload["text"].lower()
        entities: list[Entity] = payload["entities"]
        by_name = {entity.name.lower(): entity.id for entity in entities}
        relationships: list[Relationship] = []

        def exists(name: str) -> bool:
            return name in by_name

        if exists("reserve bank of india") and exists("repo rate decision"):
            relationships.append(
                Relationship(
                    source_id=by_name["repo rate decision"],
                    target_id=by_name["reserve bank of india"],
                    relation=RelationType.ANNOUNCED_BY.value,
                    evidence="Repo rate decisions are announced by RBI",
                )
            )
        if exists("repo rate decision") and exists("inflation"):
            relationships.append(
                Relationship(
                    source_id=by_name["repo rate decision"],
                    target_id=by_name["inflation"],
                    relation=RelationType.AFFECTS.value,
                    evidence="Policy rates influence inflation dynamics",
                )
            )
        if exists("inflation") and exists("nifty 50"):
            relationships.append(
                Relationship(
                    source_id=by_name["inflation"],
                    target_id=by_name["nifty 50"],
                    relation=RelationType.IMPACTS.value,
                    evidence="Inflation affects market valuation expectations",
                )
            )
        if exists("crude oil") and exists("inflation"):
            relationships.append(
                Relationship(
                    source_id=by_name["crude oil"],
                    target_id=by_name["inflation"],
                    relation=RelationType.CAUSES.value,
                    evidence="Oil prices feed into imported inflation",
                )
            )
        if exists("indian government bond yield") and exists("nifty 50"):
            relationships.append(
                Relationship(
                    source_id=by_name["indian government bond yield"],
                    target_id=by_name["nifty 50"],
                    relation=RelationType.CORRELATES_WITH.value,
                    evidence="Yield movements often correlate with equity repricing",
                )
            )

        if "risk" in text and exists("india") and exists("inflation"):
            relationships.append(
                Relationship(
                    source_id=by_name["inflation"],
                    target_id=by_name["india"],
                    relation=RelationType.AFFECTS.value,
                    evidence="Rising inflation is a macro risk to India",
                )
            )

        return relationships

    def _extract_events(self, text: str) -> list[Entity]:
        lowered = text.lower()
        events: list[Entity] = []
        event_triggers = {
            "increases": "Policy Tightening",
            "hike": "Policy Tightening",
            "falls": "Market Decline",
            "rose": "Commodity Price Shock",
            "climbed": "Commodity Price Shock",
            "risk": "Macro Risk Alert",
        }

        for keyword, name in event_triggers.items():
            if keyword in lowered:
                event_id = f"event_{name.lower().replace(' ', '_')}"
                events.append(
                    Entity(
                        id=event_id,
                        name=name,
                        entity_type=EntityType.EVENT,
                        properties={"trigger": keyword},
                    )
                )

        return self._deduplicate_entities(events)

    @staticmethod
    def _analyze_sentiment(text: str) -> str:
        lowered = text.lower()
        negative_markers = ["risk", "inflation", "fell", "decline", "tight"]
        positive_markers = ["growth", "rally", "improve", "easing"]

        negative_score = sum(marker in lowered for marker in negative_markers)
        positive_score = sum(marker in lowered for marker in positive_markers)

        if negative_score > positive_score:
            return "negative"
        if positive_score > negative_score:
            return "positive"
        return "neutral"

    @staticmethod
    def _deduplicate_entities(entities: Iterable[Entity]) -> list[Entity]:
        dedup: dict[str, Entity] = {}
        for entity in entities:
            dedup[entity.id] = entity
        return list(dedup.values())
