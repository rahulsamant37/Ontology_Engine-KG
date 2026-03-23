# Ontology Engine (KG) — Minimal README (Only Main-Flow Files)

This README documents **only the code paths that are executed/used from the main entry point** (`main.py`) and their direct dependencies.

---

## 1) Entry Point (App Startup)

### `main.py`
**Role:** Creates the FastAPI app, configures logging, and registers API routes.

**Uses:**
- `api/routes.py` (API endpoints)
- `utils/config.py` (settings)
- `utils/logging.py` (logging config)

---

## 2) API Layer (Routes + Dependency Injection)

### `api/routes.py`
**Role:** Defines the HTTP endpoints:
- `POST /ingest`
- `POST /ingest/public`
- `POST /query`
- `GET /insights`
- `GET /graph`

**Uses:**
- `api/deps.py` (dependency providers)
- `models/schemas.py` (request/response models)
- `services/ingestion_service.py`
- `services/public_data_service.py`
- `services/query_service.py`

### `api/deps.py`
**Role:** Creates and caches "singletons" for core services/repositories using `@lru_cache`.

**Builds and wires:**
- `VectorIndex` (vector store)
- `GraphRepository` (Neo4j or in-memory graph)
- `InsightRepository` (Postgres or SQLite)
- `ExtractionService`
- `ReasoningService`
- `InsightService`
- `FinancialWorkflow` (LangGraph pipeline)
- `IngestionService`
- `PublicDataService`
- `QueryService`

---

## 3) Services (Business Logic)

### `services/ingestion_service.py`
**Role:** Ingests raw payloads, normalizes them, converts to searchable text, and stores them in the vector store.

**Uses:**
- `db/vector_store.py` (`VectorIndex`, `VectorRecord`)
- `ingestion/normalizer.py` (`normalize_payload`)
- `models/schemas.py` (`RawIngestRequest`, `IngestResult`)
- `utils/logging.py`

---

### `services/public_data_service.py`
**Role:** Pulls macro indicators from the **World Bank API** and returns them in a structured event format suitable for ingestion.

**Used by endpoint:**
- `POST /ingest/public`

---

### `services/query_service.py`
**Role:** Answers a query by:
1. Retrieving similar docs from the vector store
2. Running the workflow (agents graph)
3. Persisting the final insight
4. Returning insight + reasoning logs

**Uses:**
- `agents/workflow.py` (`FinancialWorkflow`, `WorkflowState`)
- `db/vector_store.py`
- `db/postgres_client.py` (`InsightRepository`)
- `db/neo4j_client.py` (`GraphRepository`)
- `models/schemas.py` (`QueryRequest`, `Insight`)
- `utils/logging.py`

---

### `services/extraction_service.py`
**Role:** Extracts entities + relationships from the question text (keyword-based extraction + simple relationship rules).

**Uses:**
- `models/ontology.py` (entity/relation types)
- `models/schemas.py` (`Entity`, `Relationship`)

---

### `services/reasoning_service.py`
**Role:** Builds a driver chain (entity names, relationship strings, doc snippets) and computes a confidence score.

**Uses:**
- `models/schemas.py` (`Entity`, `Relationship`)

---

### `services/insight_service.py`
**Role:** Turns the workflow state into a final `Insight` object (text + confidence + drivers + impact).

**Uses:**
- `models/schemas.py` (`Insight`)

---

## 4) Agent Workflow (Pipeline Orchestration)

### `agents/workflow.py`
**Role:** Defines a LangGraph pipeline with the following nodes:

1. `IngestionAgent` (accepts context)
2. `ExtractionAgent` (extract entities/relationships)
3. `EntityLinkingAgent` (dedupe placeholder step)
4. `GraphUpdateAgent` (store entities + relationships)
5. `ReasoningAgent` (drivers + confidence)
6. `InsightAgent` (final response)

**Uses:**
- `services/extraction_service.py`
- `services/reasoning_service.py`
- `services/insight_service.py`
- `db/neo4j_client.py`
- `utils/logging.py`

---

## 5) Persistence / Storage

### `db/vector_store.py`
**Role:** Vector storage + similarity search (Chroma + embeddings).  
Used for retrieving context for questions.

**Uses:**
- `utils/config.py` (vector directory + top-k)

---

### `db/neo4j_client.py`
**Role:** Graph repository abstraction:
- Uses Neo4j if enabled by config
- Otherwise falls back to in-memory storage
Supports:
- `upsert_entities`
- `add_relationships`
- `snapshot`

**Uses:**
- `utils/config.py`
- `models/schemas.py` (`Entity`, `Relationship`, `GraphSnapshot`)
- `utils/logging.py`

---

### `db/postgres_client.py`
**Role:** Insight persistence:
- Uses Postgres if enabled
- Otherwise uses SQLite (`ontology.db`)
Supports:
- `save_insight`
- `list_insights`

**Uses:**
- `utils/config.py`
- `models/schemas.py` (`Insight`, `InsightRecord`)
- `utils/logging.py`

---

## 6) Models / Schemas

### `models/schemas.py`
**Role:** Pydantic models for:
- Ingest requests (`RawIngestRequest`, payload models)
- Query requests (`QueryRequest`)
- Ontology output (`Entity`, `Relationship`)
- Results (`Insight`, `GraphSnapshot`, `InsightRecord`, `IngestResult`)

### `models/ontology.py`
**Role:** Enum definitions for `EntityType` and allowed `RelationType`s + validator helper.

---

## 7) Ingestion Helpers

### `ingestion/normalizer.py`
**Role:** Normalizes incoming payloads into a consistent shape:
- Resolves payload type (structured vs unstructured)
- Validates with Pydantic models
- Uses transformer for unstructured text

**Uses:**
- `ingestion/text_transformer.py`
- `models/schemas.py`

### `ingestion/text_transformer.py`
**Role:** Lightweight text-to-structured transformer:
- Extracts entities (keyword rules)
- Extracts metrics (% / bps)
- Infers event type + sentiment
- Builds tags

---

## 8) Utilities

### `utils/config.py`
**Role:** Environment-based settings (Pydantic Settings):
- app name/env
- Neo4j enablement + credentials
- Postgres enablement + URL
- vector store directory + retrieval top-k
- OpenAI key/model fields (present, but not required by the current skeleton)

### `utils/logging.py`
**Role:** Logging setup + logger getter.

---

# Minimal Runtime File List (Main Flow Only)

If you want to show "only what runs", these are the files:

- `main.py`
- `api/routes.py`
- `api/deps.py`
- `services/ingestion_service.py`
- `services/public_data_service.py`
- `services/query_service.py`
- `services/extraction_service.py`
- `services/reasoning_service.py`
- `services/insight_service.py`
- `agents/workflow.py`
- `db/vector_store.py`
- `db/neo4j_client.py`
- `db/postgres_client.py`
- `ingestion/normalizer.py`
- `ingestion/text_transformer.py`
- `models/schemas.py`
- `models/ontology.py`
- `utils/config.py`
- `utils/logging.py`
