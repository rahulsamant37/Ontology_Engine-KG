from __future__ import annotations

from dataclasses import dataclass, field

from neo4j import GraphDatabase

from models.schemas import Entity, GraphSnapshot, Relationship
from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class InMemoryGraph:
    entities: dict[str, Entity] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)


class GraphRepository:
    def __init__(self) -> None:
        self._memory = InMemoryGraph()
        self._driver = None

        if settings.use_neo4j:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            logger.info("Neo4j enabled at %s", settings.neo4j_uri)
        else:
            logger.info("Using in-memory graph repository")

    def upsert_entities(self, entities: list[Entity]) -> None:
        for entity in entities:
            self._memory.entities[entity.id] = entity

        if self._driver:
            with self._driver.session() as session:
                for entity in entities:
                    session.run(
                        """
                        MERGE (e:Entity {id: $id})
                        SET e.name = $name, e.entity_type = $entity_type, e.properties = $properties
                        """,
                        id=entity.id,
                        name=entity.name,
                        entity_type=entity.entity_type.value,
                        properties=entity.properties,
                    )

    def add_relationships(self, relationships: list[Relationship]) -> None:
        self._memory.relationships.extend(relationships)

        if self._driver:
            with self._driver.session() as session:
                for rel in relationships:
                    session.run(
                        """
                        MATCH (s:Entity {id: $source_id})
                        MATCH (t:Entity {id: $target_id})
                        MERGE (s)-[r:RELATED {relation: $relation}]->(t)
                        SET r.evidence = $evidence
                        """,
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        relation=rel.relation,
                        evidence=rel.evidence,
                    )

    def snapshot(self) -> GraphSnapshot:
        return GraphSnapshot(
            entities=list(self._memory.entities.values()),
            relationships=self._memory.relationships,
        )
