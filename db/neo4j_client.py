from __future__ import annotations

import json
from dataclasses import dataclass, field

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

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
            try:
                self._driver = GraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                )
                self._driver.verify_connectivity()
                logger.info("Neo4j enabled at %s", settings.neo4j_uri)
            except (Neo4jError, Exception) as exc:
                logger.warning(
                    "Neo4j connection failed. Falling back to in-memory graph. uri=%s error=%s",
                    settings.neo4j_uri,
                    exc,
                )
                self._driver = None
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
                        SET e.name = $name, e.entity_type = $entity_type, e.properties_json = $properties_json
                        """,
                        id=entity.id,
                        name=entity.name,
                        entity_type=entity.entity_type.value,
                        properties_json=json.dumps(entity.properties or {}),
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
        if self._driver:
            with self._driver.session() as session:
                entities_result = session.run(
                    """
                    MATCH (e:Entity)
                    RETURN e.id AS id, e.name AS name, e.entity_type AS entity_type, e.properties_json AS properties_json
                    """
                )
                relationships_result = session.run(
                    """
                    MATCH (s:Entity)-[r:RELATED]->(t:Entity)
                    RETURN s.id AS source_id, t.id AS target_id, r.relation AS relation, r.evidence AS evidence
                    """
                )

                entities = [
                    Entity(
                        id=record["id"],
                        name=record["name"],
                        entity_type=record["entity_type"],
                        properties=(
                            json.loads(record["properties_json"])
                            if record["properties_json"]
                            else {}
                        ),
                    )
                    for record in entities_result
                ]
                relationships = [
                    Relationship(
                        source_id=record["source_id"],
                        target_id=record["target_id"],
                        relation=record["relation"],
                        evidence=record["evidence"],
                    )
                    for record in relationships_result
                ]

                return GraphSnapshot(entities=entities, relationships=relationships)

        return GraphSnapshot(
            entities=list(self._memory.entities.values()),
            relationships=self._memory.relationships,
        )
