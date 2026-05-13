from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from phase1.utils.ids import country_id, indicator_id, year_id, observation_id


@dataclass(frozen=True)
class Country:
    name: str
    code: str

    def to_node(self) -> Dict[str, object]:
        return {
            "id": country_id(self.code),
            "name": self.name,
            "code": self.code,
        }


@dataclass(frozen=True)
class Indicator:
    name: str
    code: str

    def to_node(self) -> Dict[str, object]:
        return {
            "id": indicator_id(self.code),
            "name": self.name,
            "code": self.code,
        }


@dataclass(frozen=True)
class Year:
    value: int

    def to_node(self) -> Dict[str, object]:
        return {
            "id": year_id(self.value),
            "value": self.value,
        }


@dataclass(frozen=True)
class Observation:
    country_code: str
    indicator_code: str
    year: int
    value: float

    def to_node(self) -> Dict[str, object]:
        return {
            "id": observation_id(self.country_code, self.indicator_code, self.year),
            "value": self.value,
        }
