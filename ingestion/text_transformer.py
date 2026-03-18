from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class EntityRule:
    keyword: str
    canonical_name: str


ENTITY_RULES: tuple[EntityRule, ...] = (
    EntityRule("rbi", "Reserve Bank of India"),
    EntityRule("repo rate", "Repo Rate Decision"),
    EntityRule("inflation", "Inflation"),
    EntityRule("cpi", "CPI"),
    EntityRule("bond yield", "Indian Government Bond Yield"),
    EntityRule("nifty", "NIFTY 50"),
    EntityRule("oil", "Crude Oil"),
    EntityRule("india", "India"),
)


class OntologyTextTransformer:
    """Lightweight NLP-style parser that maps raw macro text to structured ontology fields."""

    _percent_pattern = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s?%")
    _bps_pattern = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s?(?:bps|basis points)")

    def transform(self, text: str) -> dict:
        cleaned = self._clean(text)
        lowered = cleaned.lower()

        entities = self._extract_entities(lowered)
        metrics = self._extract_metrics(cleaned)
        event_type = self._infer_event_type(lowered)
        sentiment = self._infer_sentiment(lowered)
        tags = self._build_tags(event_type=event_type, sentiment=sentiment, entities=entities)

        return {
            "title": self._build_title(cleaned, event_type),
            "text": cleaned,
            "event_type": event_type,
            "country": "India",
            "metrics": metrics,
            "tags": tags,
            "entities": entities,
            "sentiment": sentiment,
        }

    @staticmethod
    def _clean(text: str) -> str:
        compact = " ".join(text.split())
        return compact.strip()

    def _extract_metrics(self, text: str) -> list[dict]:
        metrics: list[dict] = []

        for match in self._percent_pattern.finditer(text):
            value = float(match.group("value"))
            metrics.append(
                {
                    "name": "percentage_value",
                    "value": value,
                    "unit": "%",
                    "period": None,
                }
            )

        for match in self._bps_pattern.finditer(text.lower()):
            value = float(match.group("value"))
            metrics.append(
                {
                    "name": "basis_points",
                    "value": value,
                    "unit": "bps",
                    "period": None,
                }
            )

        return metrics

    @staticmethod
    def _infer_event_type(lowered: str) -> str:
        if "repo rate" in lowered or "policy" in lowered or "rbi" in lowered:
            return "monetary_policy"
        if "inflation" in lowered or "cpi" in lowered:
            return "inflation_update"
        if "nifty" in lowered or "market" in lowered:
            return "market_movement"
        if "oil" in lowered or "crude" in lowered:
            return "commodity_price_move"
        return "macro_update"

    @staticmethod
    def _infer_sentiment(lowered: str) -> str:
        negative_markers = ("risk", "inflation", "fell", "decline", "tight")
        positive_markers = ("rally", "growth", "easing", "improved")

        negative_score = sum(marker in lowered for marker in negative_markers)
        positive_score = sum(marker in lowered for marker in positive_markers)

        if negative_score > positive_score:
            return "negative"
        if positive_score > negative_score:
            return "positive"
        return "neutral"

    @staticmethod
    def _build_title(text: str, event_type: str) -> str:
        if not text:
            return event_type.replace("_", " ").title()
        if len(text) <= 90:
            return text
        return f"{text[:87].rstrip()}..."

    @staticmethod
    def _deduplicate(items: Iterable[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    def _extract_entities(self, lowered: str) -> list[str]:
        entities = [rule.canonical_name for rule in ENTITY_RULES if rule.keyword in lowered]
        if not entities:
            entities.append("India")
        return self._deduplicate(entities)

    def _build_tags(self, event_type: str, sentiment: str, entities: list[str]) -> list[str]:
        tags = [event_type, f"sentiment:{sentiment}"]
        tags.extend(entity.lower().replace(" ", "_") for entity in entities[:4])
        return self._deduplicate(tags)
