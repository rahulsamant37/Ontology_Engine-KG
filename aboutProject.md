# India-Centric Spatiotemporal Economic Knowledge Graph (ISTE-KG)

## Overview

This document defines the initial ontology, schema, and graph construction strategy for an India-centric spatiotemporal economic knowledge graph inspired by the research paper:

> *A spatiotemporal knowledge graph for driving factor analysis and growth prediction of regional economy in China* 

The goal of this project is to model India's economy as a dynamic interconnected system influenced by:

* internal economic indicators,
* temporal evolution,
* spatial interactions,
* and external geopolitical/economic factors.

Unlike traditional tabular datasets, the graph representation enables modeling of:

* nonlinear relationships,
* temporal dependencies,
* external influence propagation,
* and future economic reasoning.

---

# 1. Project Goal

The objective is to build a foundational economic knowledge graph for India that can later support:

* economic trend analysis,
* GDP prediction,
* external shock analysis,
* policy reasoning,
* graph embeddings,
* graph neural networks (R-GCN/GAT),
* and spatiotemporal economic inference.

---

# 2. Current Dataset

Currently available dataset: 

### Source

World Bank India Dataset

### Current Columns

```text
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
```

This dataset contains:

* one country (`India`)
* multiple economic indicators
* yearly economic observations

This is sufficient for constructing the **base economic knowledge graph layer**.

---

# 3. Why Convert Tabular Data into a Graph?

Traditional tables store isolated values.

Example:

| Country | Indicator  | 2020 |
| ------- | ---------- | ---- |
| India   | GDP Growth | 3.2  |

However, economies are interconnected systems.

Graph representation enables:

* explicit modeling of relationships,
* temporal connectivity,
* future reasoning,
* embedding learning,
* graph neural network training.

Instead of isolated rows, the economy becomes:

```text
India
   -> has_observation -> GDP_2020
GDP_2020
   -> at_time -> 2020
GDP_2020
   -> of_indicator -> GDP Growth
```

---

# 4. Initial Ontology Design

## 4.1 Core Entity Types

The initial ontology contains four primary entity classes.

---

## A. Country

Represents sovereign economic regions.

### Example

```text
India
USA
China
SaudiArabia
```

### Properties

| Property | Description      |
| -------- | ---------------- |
| name     | Country name     |
| iso_code | ISO country code |

---

## B. Indicator

Represents economic indicators.

### Example

```text
GDP Growth
Inflation
Population
FDI Inflow
Unemployment
```

### Properties

| Property       | Description               |
| -------------- | ------------------------- |
| indicator_name | Full indicator name       |
| indicator_code | World Bank indicator code |
| source         | Dataset source            |

---

## C. Year

Represents temporal entities.

### Example

```text
2015
2016
2020
2025
```

### Properties

| Property | Description  |
| -------- | ------------ |
| year     | Integer year |

---

## D. Observation

Represents one economic measurement.

This is the most important entity type.

Each observation corresponds to:

```text
(country, indicator, year, value)
```

### Example

```text
obs_india_gdp_2020
```

### Properties

| Property | Description               |
| -------- | ------------------------- |
| value    | Numerical indicator value |
| source   | Dataset source            |
| unit     | Measurement unit          |

---

# 5. Initial Relationship Types

---

## A. Country → Observation

### Relationship

```text
HAS_OBSERVATION
```

### Example

```text
India -> HAS_OBSERVATION -> obs_india_gdp_2020
```

---

## B. Observation → Indicator

### Relationship

```text
OF_INDICATOR
```

### Example

```text
obs_india_gdp_2020 -> OF_INDICATOR -> GDP Growth
```

---

## C. Observation → Year

### Relationship

```text
AT_YEAR
```

### Example

```text
obs_india_gdp_2020 -> AT_YEAR -> 2020
```

---

# 6. Why Use Observation Nodes?

Instead of directly connecting:

```text
India -> GDP -> 3.2
```

observation nodes provide:

* temporal clarity,
* scalability,
* metadata storage,
* future extensibility,
* and compatibility with graph learning algorithms.

This structure also aligns conceptually with the REST-KG design proposed in the referenced paper. 

---

# 7. Data Transformation Strategy

The current dataset is in **wide format**.

## Current Format

| Indicator | 2015 | 2016 | 2017 |
| --------- | ---- | ---- | ---- |

This format is not suitable for graph construction.

---

## Required Format (Long Format)

| Country | Indicator | Year | Value |
| ------- | --------- | ---- | ----- |

Example:

| Country | Indicator  | Year | Value |
| ------- | ---------- | ---- | ----- |
| India   | GDP Growth | 2020 | 3.2   |

---

# 8. Initial Indicators to Keep

The graph should initially include only economically meaningful indicators.

## Recommended Initial Indicators

| Indicator      | Reason                       |
| -------------- | ---------------------------- |
| GDP Growth     | Core target variable         |
| GDP Per Capita | Economic productivity        |
| Inflation      | Purchasing power             |
| Population     | Labor force proxy            |
| Unemployment   | Economic health              |
| FDI Inflow     | External investment          |
| Trade Openness | Global connectivity          |
| Remittances    | External economic dependence |

---

# 9. What Should NOT Be Added Initially

The following relationships should NOT yet be manually defined:

```text
CAUSES
PROMOTES
INHIBITS
DRIVES
```

Reason:

The current dataset contains observations, not causal evidence.

Causal or influence relationships should only be added after:

* statistical analysis,
* correlation analysis,
* literature validation,
* or graph embedding inference.

---

# 10. Future Expansion Plan

After the base graph is constructed, the following layers can be added.

---

## A. State-Level Spatial Layer

### New Entity Type

```text
State
```

### Relationships

```text
NEIGHBORING_STATE
BELONGS_TO_COUNTRY
```

---

## B. External Country Influence Layer

### Example Relationships

```text
India -> IMPORTS_FROM -> China
India -> OIL_DEPENDENCY_ON -> SaudiArabia
USA -> INVESTS_IN -> India
```

### Possible Data Sources

* IMF
* UN Comtrade
* RBI
* World Bank
* MOSPI

---

## C. Night-Time Light Layer

Inspired by the referenced paper. 

Night-time lights can act as:

* GDP proxy,
* urbanization signal,
* industrial activity measure.

Possible source:

* NASA VIIRS
* Google Earth Engine

---

# 11. Future Machine Learning Pipeline

After graph construction:

---

## Step 1 — Knowledge Graph Embedding

Possible methods:

* TransE
* DistMult
* Node2Vec
* R-GCN

---

## Step 2 — Spatiotemporal Learning

Possible models:

* R-GCN
* GAT
* Temporal GNN
* ST-GCN

---

## Step 3 — Economic Prediction

Possible targets:

* GDP growth
* inflation forecasting
* economic shock propagation
* state-level economic disparity

---

# 12. Conceptual Difference from Traditional Databases

Traditional Database:

```text
India | GDP | 2020 | 3.2
```

Knowledge Graph:

```text
India
   -> HAS_OBSERVATION -> GDP_2020
GDP_2020
   -> OF_INDICATOR -> GDP Growth
GDP_2020
   -> AT_YEAR -> 2020
```

The graph structure preserves semantic meaning and enables reasoning.

---

# 13. Initial Graph Construction Workflow

## Phase 1

### Data Processing

* clean null values
* normalize indicator names
* reshape to long format

---

### Graph Construction

Create:

* country nodes
* indicator nodes
* year nodes
* observation nodes

---

### Graph Relationships

Create:

* HAS_OBSERVATION
* OF_INDICATOR
* AT_YEAR

---

## Phase 2

Add:

* state-level data,
* trade relations,
* FDI,
* oil dependencies,
* remittances,
* geopolitical links.

---

## Phase 3

Train:

* embeddings,
* graph neural networks,
* economic prediction models.

---

# 14. Final Conceptual Vision

The long-term goal is to transform India's economy from:

```text
isolated tables of economic numbers
```

into:

```text
a dynamic interconnected spatiotemporal economic system
```

capable of:

* reasoning,
* forecasting,
* influence analysis,
* and policy intelligence.

This project extends the conceptual direction of REST-KG by introducing:

* India-centric modeling,
* external geopolitical influence,
* and future cross-country economic interaction analysis.
