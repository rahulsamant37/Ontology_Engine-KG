from __future__ import annotations

import logging
import os
from typing import Dict

import pandas as pd

from phase1.config import Phase1Config
from phase1.graph_builder.builder import build_graph
from phase1.graph_builder.export import export_graph
from phase1.graph_builder.transform import wide_to_long
from phase1.graph_builder.validation import validate_graph
from phase1.utils.io import ensure_dir, write_json
from phase1.utils.logging import setup_logging


def run_pipeline(config: Phase1Config) -> None:
    setup_logging()
    logging.info("Loading CSV: %s", config.input_csv)
    df = pd.read_csv(config.input_csv)

    logging.info("Transforming data")
    long_df = wide_to_long(df, config.id_columns)

    logging.info("Building graph")
    nodes, rels = build_graph(long_df)

    logging.info("Validating graph")
    issues = validate_graph(nodes, rels)
    if issues:
        for issue in issues:
            logging.error(issue)
        raise ValueError("Graph validation failed")

    logging.info("Exporting graph")
    ensure_dir(config.output_dir)
    export_graph(nodes, rels, config.output_dir)

    stats = build_stats(long_df, nodes, rels)
    stats_path = os.path.join(config.output_dir, "stats.json")
    write_json(stats_path, stats)
    logging.info("Done")


def build_stats(
    long_df: pd.DataFrame,
    nodes: Dict[str, pd.DataFrame],
    rels: Dict[str, pd.DataFrame],
) -> Dict[str, int]:
    return {
        "records": int(len(long_df)),
        "nodes": int(sum(len(df) for df in nodes.values())),
        "relationships": int(sum(len(df) for df in rels.values())),
    }
