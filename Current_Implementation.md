
# Prompt: Implement Phase-1 India Economic Knowledge Graph from World Bank Dataset given in repositery

I am building Phase-1 of India-centric spatiotemporal economic knowledge graph inspired by the paper:

"A spatiotemporal knowledge graph for driving factor analysis and growth prediction of regional economy in China"

I already have a partially cleaned World Bank India CSV dataset with columns like:

[
 'Country Name',
 'Country Code',
 'Indicator Name',
 'Indicator Code',
 '2015',
 '2016',
 '2017',
 '2018',
 '2019',
 '2020',
 '2021',
 '2022',
 '2023',
 '2024',
 '2025'
]


Rows with null values across all years have already been removed.

dataset is in path /data/india_filtered_indicators.csv

---

# Goal

Implement ONLY Phase 1 of the knowledge graph system.

The task is NOT:

* building the full research pipeline (for now),
* training ML/GNN models,
* adding external datasets,
* or creating a production system.

The task IS:

1. transform the current CSV into graph-friendly structure,
2. design entities and relationships inspired by REST-KG,
3. and construct the foundational knowledge graph programmatically.

---

# Important Requirements

Focus ONLY on:

* ontology implementation,
* entity generation,
* relationship generation,
* graph construction,
* graph schema,
* data transformation,
* and graph storage.

---

# What I Need

Provide a COMPLETE implementation-oriented plan with code structure and logic for the following:

---

# 1. Data Transformation

Explain and implement:

* conversion from wide format to long format,
* handling yearly columns,
* preserving indicator semantics,
* handling missing values,
* and generating graph-ready records.

The transformed format should conceptually become:

| Country | Indicator | Year | Value |

Provide Python/Pandas implementation examples.

---

# 2. Ontology Implementation

Implement a minimal ontology inspired by the REST-KG paper.

Create node/entity definitions for:

* Country
* Indicator
* Year
* Observation

Explain:

* why each node exists,
* node identifiers,
* node properties,
* and how they map from CSV rows.

---

# 3. Relationship Implementation

Implement graph relationships such as:

* Country -> HAS_OBSERVATION -> Observation
* Observation -> OF_INDICATOR -> Indicator
* Observation -> AT_YEAR -> Year

Only include relationships that are semantically valid from the dataset.

Explain:

* edge direction,
* edge meaning,
* and implementation logic.

---

# 4. Observation Node Strategy

Implement the graph using separate Observation nodes instead of storing yearly values directly as properties.

Explain and implement:

* observation node naming,
* unique IDs,
* property assignment,
* and relationship attachment.

---

# 5. Graph Construction Pipeline

Provide a detailed implementation pipeline for:

1. loading CSV,
2. transforming data,
3. creating nodes,
4. creating edges,
5. deduplicating entities,
6. exporting graph structure.

---

# 6. Suggested Graph Technology

Neo4j for Phase 1 only.


Then implement the graph construction using the recommended framework.

---

# 7. Code Structure

Provide a clean modular project structure such as:

```text
project/
│
├── data/
├── ontology/
├── graph_builder/
├── utils/
├── outputs/
```

Explain responsibility of each module.

---

# 8. Graph Export

Implement exporting the graph into useful formats such as:

* Neo4j CSV import format

---

# 9. Validation

Implement validation checks for:

* duplicate nodes,
* missing relationships,
* inconsistent identifiers,
* and malformed observations.

---

# 10. Final Deliverable

The final response should include:

* implementation strategy,
* ontology mapping logic,
* graph-building workflow,
* Python code examples,
* modular architecture,
* and graph construction best practices.

The response should feel like:

* an implementation blueprint for Phase-1 REST-KG-inspired economic graph construction,


