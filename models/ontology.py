from __future__ import annotations

from enum import Enum


class EntityType(str, Enum):
    COUNTRY = "Country"
    INSTITUTION = "Institution"
    ASSET = "Asset"
    ECONOMIC_INDICATOR = "EconomicIndicator"
    EVENT = "Event"


class RelationType(str, Enum):
    AFFECTS = "affects"
    CAUSES = "causes"
    CORRELATES_WITH = "correlates_with"
    ANNOUNCED_BY = "announced_by"
    IMPACTS = "impacts"


VALID_RELATION_TYPES = {
    RelationType.AFFECTS,
    RelationType.CAUSES,
    RelationType.CORRELATES_WITH,
    RelationType.ANNOUNCED_BY,
    RelationType.IMPACTS,
}


def is_valid_relation(value: str) -> bool:
    return value in {rel.value for rel in VALID_RELATION_TYPES}
