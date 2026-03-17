# Ontology Engine KG (India Macro MVP)

Production-style AI-powered Economic and Financial Ontology Engine focused on India macro signals:

- RBI policy
- Inflation (CPI)
- Bond yields
- NIFTY 50
- Oil prices

The system ingests structured/unstructured input, extracts entities and causal links, updates a knowledge graph, and answers natural-language macro questions with explainable reasoning logs.

## Tech Stack

- Python 3.12+
- Dependency manager: `uv`
- API: FastAPI
- LLM orchestration primitives: LangChain runnables
- Agent workflow: LangGraph
- Vector store: Chroma
- Graph store: Neo4j (optional in MVP, in-memory fallback available)
- Relational store: PostgreSQL (optional in MVP, SQLite fallback available)

## Setup (Required: uv)

```bash
uv venv
source .venv/bin/activate
uv sync
```

## Run API

```bash
uv run uvicorn main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## API Endpoints

- `POST /ingest`
- `POST /query`
- `GET /insights`
- `GET /graph`

### Example: ingest

```bash
curl -X POST http://127.0.0.1:8000/ingest \
	-H "content-type: application/json" \
	-d '{
		"source": "macro_news",
		"payload": {
			"text": "RBI warned on inflation as oil rose and NIFTY reacted to yields."
		}
	}'
```

### Example: query

```bash
curl -X POST http://127.0.0.1:8000/query \
	-H "content-type: application/json" \
	-d '{"question":"Why did the Indian stock market move today?"}'
```

Insight format:

```json
{
	"insight": "...",
	"confidence": 0.0,
	"drivers": ["..."],
	"explanation": "...",
	"impact": ["..."],
	"reasoning_logs": ["..."]
}
```

## Architecture

Project layout:

- `api/`: FastAPI routes and dependency wiring
- `agents/`: LangGraph workflow (`IngestionAgent -> ExtractionAgent -> EntityLinkingAgent -> GraphUpdateAgent -> ReasoningAgent -> InsightAgent`)
- `services/`: extraction, ingestion, reasoning, and insight synthesis
- `db/`: Neo4j, PostgreSQL, and Chroma adapters
- `models/`: strict ontology and request/response schemas
- `ingestion/`: data normalization
- `data/`: sample events
- `scripts/`: demo run script
- `tests/`: API tests

## Ontology

Entities:

- Country
- Institution
- Asset
- EconomicIndicator
- Event

Relationships (strict whitelist):

- affects
- causes
- correlates_with
- announced_by
- impacts

## Demo Run

Load sample events and run query+graph snapshot:

```bash
uv run python scripts/test_run.py
```

## Tests

```bash
uv run pytest -q
```

## Configuration

Environment settings are in `utils/config.py` and can be overridden via `.env`.
Use `.env.example` as a starting point.

- `USE_NEO4J=true` to enable Neo4j connection
- `USE_POSTGRES=true` to enable PostgreSQL connection

If disabled, safe local fallbacks are used so the MVP runs without external infrastructure.

## Sample Query Outputs

See `Sample_Queries_Output.md` for example prompts and output shape.
