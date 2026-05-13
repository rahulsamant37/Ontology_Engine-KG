from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Dict, Iterable, List

import pandas as pd
from neo4j import GraphDatabase


DEFAULT_LABELS = ["Country", "Indicator", "Year", "Observation"]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"").strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_env(*keys: str, default: str | None = None, required: bool = False) -> str:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    if required:
        raise ValueError(f"Missing required env var: {keys}")
    return default or ""


def chunked(items: List[Dict[str, object]], size: int) -> Iterable[List[Dict[str, object]]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.where(df.notna(), None)


def build_node_rows(df: pd.DataFrame) -> Dict[str, List[Dict[str, object]]]:
    if ":ID" not in df.columns:
        raise ValueError("Node CSV missing :ID column")

    label = None
    if ":LABEL" in df.columns:
        labels = df[":LABEL"].dropna().unique().tolist()
        if labels:
            label = labels[0]

    if not label:
        raise ValueError("Node CSV missing :LABEL column or label value")

    rows: List[Dict[str, object]] = []
    prop_columns = [col for col in df.columns if col not in [":ID", ":LABEL"]]

    for _, row in df.iterrows():
        props = {col: row[col] for col in prop_columns if row[col] is not None}
        rows.append({"id": row[":ID"], "props": props})

    return {label: rows}


def build_rel_rows(df: pd.DataFrame) -> Dict[str, List[Dict[str, object]]]:
    required = [":START_ID", ":END_ID", ":TYPE"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Relationship CSV missing columns: {missing}")

    rel_type = df[":TYPE"].dropna().unique().tolist()[0]
    prop_columns = [col for col in df.columns if col not in required]

    rows: List[Dict[str, object]] = []
    for _, row in df.iterrows():
        props = {col: row[col] for col in prop_columns if row[col] is not None}
        rows.append(
            {
                "start_id": row[":START_ID"],
                "end_id": row[":END_ID"],
                "props": props,
            }
        )

    return {rel_type: rows}


def ensure_constraints(session) -> None:
    for label in DEFAULT_LABELS:
        session.run(
            f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
            f"FOR (n:`{label}`) REQUIRE n.id IS UNIQUE"
        )


def load_nodes(session, nodes_dir: Path, batch_size: int) -> None:
    for csv_path in sorted(nodes_dir.glob("*.csv")):
        df = normalize_df(pd.read_csv(csv_path))
        grouped = build_node_rows(df)

        for label, rows in grouped.items():
            query = (
                f"UNWIND $rows AS row "
                f"MERGE (n:`{label}` {{id: row.id}}) "
                f"SET n += row.props"
            )
            for batch in chunked(rows, batch_size):
                session.run(query, rows=batch)

        logging.info("Loaded nodes from %s", csv_path.name)


def load_relationships(session, rels_dir: Path, batch_size: int) -> None:
    for csv_path in sorted(rels_dir.glob("*.csv")):
        df = normalize_df(pd.read_csv(csv_path))
        grouped = build_rel_rows(df)

        for rel_type, rows in grouped.items():
            query = (
                f"UNWIND $rows AS row "
                f"MATCH (start {{id: row.start_id}}) "
                f"MATCH (end {{id: row.end_id}}) "
                f"MERGE (start)-[r:`{rel_type}`]->(end) "
                f"SET r += row.props"
            )
            for batch in chunked(rows, batch_size):
                session.run(query, rows=batch)

        logging.info("Loaded relationships from %s", csv_path.name)


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Phase 1 CSVs into Neo4j")
    parser.add_argument(
        "--env",
        default=os.path.join(os.getcwd(), ".env"),
        help="Path to .env with Neo4j credentials",
    )
    parser.add_argument(
        "--outputs",
        default=os.path.join(os.getcwd(), "phase1", "outputs"),
        help="Phase 1 outputs directory",
    )
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument(
        "--skip-constraints",
        action="store_true",
        help="Skip creating uniqueness constraints",
    )
    return parser.parse_args()


def main() -> None:
    setup_logging()
    args = build_args()

    load_dotenv(args.env)

    uri = get_env("NEO4J_URI", required=True)
    user = get_env("NEO4J_USERNAME", "NEO4J_USER", required=True)
    password = get_env("NEO4J_PASSWORD", required=True)
    database = get_env("NEO4J_DATABASE", default="neo4j")

    outputs_dir = Path(args.outputs)
    nodes_dir = outputs_dir / "nodes"
    rels_dir = outputs_dir / "rels"

    if not nodes_dir.exists() or not rels_dir.exists():
        raise FileNotFoundError("Expected outputs/nodes and outputs/rels directories")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session(database=database) as session:
            if not args.skip_constraints:
                ensure_constraints(session)
            load_nodes(session, nodes_dir, args.batch_size)
            load_relationships(session, rels_dir, args.batch_size)
    finally:
        driver.close()

    logging.info("Neo4j load complete")


if __name__ == "__main__":
    main()
