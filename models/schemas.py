from __future__ import annotations

from datetime import datetime
from typing import Literal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic import model_validator

from models.ontology import EntityType, is_valid_relation


class RawIngestRequest(BaseModel):
    source: str = Field(..., description="Source identifier such as rbi_news or cpi_csv")
    payload_type: Literal["auto", "structured", "unstructured"] = "auto"
    payload: dict[str, Any] = Field(default_factory=dict)


class MetricPoint(BaseModel):
    name: str = Field(..., min_length=2)
    value: float
    unit: str | None = None
    period: str | None = None


class StructuredEventPayload(BaseModel):
    title: str = Field(..., min_length=3)
    text: str = ""
    event_type: str = Field(..., min_length=2)
    country: str = "India"
    timestamp: datetime | None = None
    metrics: list[MetricPoint] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)

    @field_validator("tags", "entities")
    @classmethod
    def _trim_values(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]


class UnstructuredTextPayload(BaseModel):
    title: str = ""
    text: str | None = None
    raw_text: str | None = None
    language: str = "en"
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_text(self) -> "UnstructuredTextPayload":
        if not (self.raw_text and self.raw_text.strip()) and not (self.text and self.text.strip()):
            msg = "Either 'raw_text' or 'text' must be provided for unstructured payloads"
            raise ValueError(msg)
        return self


class PublicDataIngestRequest(BaseModel):
    country_code: str = Field(default="IN", min_length=2, max_length=3)
    start_year: int = Field(default=2018, ge=1990, le=2100)
    end_year: int = Field(default=datetime.now().year, ge=1990, le=2100)
    indicators: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_date_range(self) -> "PublicDataIngestRequest":
        if self.start_year > self.end_year:
            msg = "start_year must be less than or equal to end_year"
            raise ValueError(msg)
        return self


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
