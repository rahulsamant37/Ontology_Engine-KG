# Phase 1 Knowledge Graph Builder

This folder contains a clean, self-contained Phase 1 implementation for building an India-centric economic knowledge graph from the World Bank CSV dataset.

## What it does

- Transforms the wide CSV into a long, graph-ready table.
- Builds nodes for Country, Indicator, Year, Observation.
- Builds relationships between nodes.
- Validates identifiers and relationships.
- Exports Neo4j bulk-import CSVs.

## Quick start

1. Ensure dependencies are installed:

```bash
pip install pandas
```

2. Run the pipeline:

```bash
python phase1/run_phase1.py
```

## Outputs

The pipeline writes to:

```
phase1/outputs/
  nodes/
  rels/
  stats.json
```

## Data source

The default input file is:

```
/data/india_filtered_indicators.csv
```

Update `phase1/config.py` if your path differs.
