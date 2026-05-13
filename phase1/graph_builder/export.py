from __future__ import annotations

import os
from typing import Dict

import pandas as pd

from phase1.utils.io import ensure_dir


def export_nodes(nodes: Dict[str, pd.DataFrame], output_dir: str) -> None:
    nodes_dir = os.path.join(output_dir, "nodes")
    ensure_dir(nodes_dir)

    for label, df in nodes.items():
        export_df = df.copy()
        export_df = export_df.rename(columns={"id": ":ID", "label": ":LABEL"})
        path = os.path.join(nodes_dir, f"{label}.csv")
        export_df.to_csv(path, index=False)


def export_relationships(rels: Dict[str, pd.DataFrame], output_dir: str) -> None:
    rels_dir = os.path.join(output_dir, "rels")
    ensure_dir(rels_dir)

    for rel_type, df in rels.items():
        export_df = df.copy()
        export_df[":TYPE"] = rel_type
        export_df = export_df.rename(
            columns={"start_id": ":START_ID", "end_id": ":END_ID"}
        )
        path = os.path.join(rels_dir, f"{rel_type}.csv")
        export_df.to_csv(path, index=False)


def export_graph(nodes: Dict[str, pd.DataFrame], rels: Dict[str, pd.DataFrame], output_dir: str) -> None:
    export_nodes(nodes, output_dir)
    export_relationships(rels, output_dir)
