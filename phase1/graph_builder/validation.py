from __future__ import annotations

from typing import Dict, List, Set

import pandas as pd


def _collect_ids(nodes: Dict[str, pd.DataFrame]) -> Set[str]:
    all_ids: Set[str] = set()
    for df in nodes.values():
        all_ids.update(df["id"].astype(str).tolist())
    return all_ids


def validate_nodes(nodes: Dict[str, pd.DataFrame]) -> List[str]:
    issues: List[str] = []
    for label, df in nodes.items():
        duplicate_ids = df["id"][df["id"].duplicated()].unique().tolist()
        if duplicate_ids:
            issues.append(f"Duplicate IDs in {label}: {len(duplicate_ids)}")
    return issues


def validate_relationships(
    nodes: Dict[str, pd.DataFrame], rels: Dict[str, pd.DataFrame]
) -> List[str]:
    issues: List[str] = []
    all_ids = _collect_ids(nodes)

    for rel_type, df in rels.items():
        missing_starts = df[~df["start_id"].isin(all_ids)]
        missing_ends = df[~df["end_id"].isin(all_ids)]

        if not missing_starts.empty:
            issues.append(f"Missing start IDs in {rel_type}: {len(missing_starts)}")
        if not missing_ends.empty:
            issues.append(f"Missing end IDs in {rel_type}: {len(missing_ends)}")

    return issues


def validate_graph(nodes: Dict[str, pd.DataFrame], rels: Dict[str, pd.DataFrame]) -> List[str]:
    issues = []
    issues.extend(validate_nodes(nodes))
    issues.extend(validate_relationships(nodes, rels))
    return issues
