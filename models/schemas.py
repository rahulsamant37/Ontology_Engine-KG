from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.ontology import EntityType, is_valid_relation


class RawIngestRequest(BaseModel):
    source: str = Field(..., description="Source identifier such as rbi_news or cpi_csv")
    payload: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=5)


class Entity(BaseModel):
    id: str
    name: str
    entity_type: EntityType
    properties: dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    source_id: str
    target_id: str
    relation: str
    evidence: str | None = None

    @field_validator("relation")
    @classmethod
    def validate_relation(cls, value: str) -> str:
        if not is_valid_relation(value):
            msg = f"Unsupported relation type: {value}"
            raise ValueError(msg)
        return value


class Insight(BaseModel):
    insight: str
    confidence: float = Field(ge=0.0, le=1.0)
    drivers: list[str] = Field(default_factory=list)
    explanation: str
    impact: list[str] = Field(default_factory=list)


class GraphSnapshot(BaseModel):
    entities: list[Entity] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)


class InsightRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question: str
    insight: str
    confidence: float
    created_at: datetime


class IngestResult(BaseModel):
    status: str
    ingested_items: int
    message: str
