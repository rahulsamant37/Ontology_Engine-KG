from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@dataclass(frozen=True)
class Phase1Config:
    input_csv: str
    output_dir: str
    id_columns: List[str]


DEFAULT_CONFIG = Phase1Config(
    input_csv=os.path.join(REPO_ROOT, "data", "india_filtered_indicators.csv"),
    output_dir=os.path.join(REPO_ROOT, "phase1", "outputs"),
    id_columns=[
        "Country Name",
        "Country Code",
        "Indicator Name",
        "Indicator Code",
    ],
)
