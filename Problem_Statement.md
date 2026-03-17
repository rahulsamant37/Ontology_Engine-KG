You are a senior AI systems architect and engineer. Design and implement a production-ready AI-powered financial intelligence system with the following specifications.

## OBJECTIVE

Build an AI-powered Economic & Financial Ontology Engine that ingests structured data, unstructured text, and real-time feeds to construct a dynamic knowledge graph. The system must generate explainable insights, detect macroeconomic risks, and answer natural language queries such as:

* “Why did the Indian stock market move today?”
* “What are the key drivers of inflation in India right now?”
* “What macro risks are increasing?”

---

## TECH STACK (MANDATORY)

* Python (latest stable)
* Dependency management: uv (NOT pip)
* Backend API: FastAPI
* LLM orchestration: LangChain
* Agent workflow orchestration: LangGraph
* Vector database: FAISS or Chroma
* Graph database: Neo4j
* Relational database: PostgreSQL

Environment setup must use:

* `uv venv`
* activation via: `source .venv/bin/activate`

---

## SCOPE (MVP)

Focus ONLY on India:

* RBI policy
* Inflation (CPI)
* Bond yields
* NIFTY 50 market movements
* Oil prices (as external driver)

---

## DATA SOURCES

### Structured Data

* Inflation (CPI) datasets
* Interest rates (RBI)
* Bond yields
* Market data (NIFTY)

### Unstructured Data

* Financial news articles
* RBI speeches/statements
* Economic reports (PDF/text)

### Real-Time Signals (optional for MVP)

* News API (e.g., NewsAPI or GDELT)

---

## ONTOLOGY DESIGN

Define a strict ontology schema:

### Entities

* Country
* Institution
* Asset
* EconomicIndicator
* Event

### Relationships

* affects
* causes
* correlates_with
* announced_by
* impacts

### Example

RBI → increases → InterestRate
InterestRate → affects → Inflation
Inflation → impacts → StockMarket

---

## SYSTEM ARCHITECTURE

### 1. Ingestion Layer

* Fetch structured + unstructured data
* Normalize into unified schema

### 2. Processing Layer

* Use LangChain for:

  * Entity extraction
  * Event detection
  * Sentiment analysis

### 3. Knowledge Graph Layer

* Store entities + relationships in Neo4j
* Implement entity resolution

### 4. Vector Layer

* Store embeddings for semantic search

### 5. Reasoning Layer (LangGraph)

Define agents:

* IngestionAgent
* ExtractionAgent
* EntityLinkingAgent
* GraphUpdateAgent
* ReasoningAgent
* InsightAgent

Define workflow:
Input → Ingest → Extract → Link → Update Graph → Reason → Generate Insight

---

## API DESIGN (FastAPI)

Implement endpoints:

* POST /query
  Input: natural language question
  Output: structured insight

* POST /ingest
  Input: raw data
  Output: ingestion status

* GET /insights
  Output: latest macro insights

* GET /graph
  Output: knowledge graph snapshot

---

## OUTPUT FORMAT

All insights must follow:

{
"insight": "...",
"confidence": 0.0-1.0,
"drivers": ["..."],
"explanation": "...",
"impact": ["..."]
}

---

## FEATURES

* Natural language querying over economic data
* Explainable reasoning (NOT black-box answers)
* Real-time graph updates
* Cause-effect chain generation
* Risk detection signals

---

## CONSTRAINTS

* No vague pseudocode — provide working, modular code
* Follow clean architecture principles
* Ensure scalability and extensibility
* Avoid hallucinated relationships — rely on extracted data
* Log all reasoning steps for transparency

---

## PROJECT STRUCTURE

Design a clean modular structure:

* /api (FastAPI routes)
* /agents (LangGraph agents)
* /services (business logic)
* /db (database connections)
* /models (schemas)
* /ingestion (data pipelines)
* /utils

---

## DELIVERABLES

Provide:

1. Complete project structure
2. Environment setup using uv
3. FastAPI app implementation
4. LangGraph workflow definition
5. LangChain pipelines for extraction
6. Neo4j integration
7. Example dataset + test run
8. Sample queries with outputs

---

## GOAL

The final system should behave like a financial intelligence assistant that:

* Connects macroeconomic signals
* Explains market movements
* Surfaces hidden risks
* Supports decision-making with structured reasoning

Build this step-by-step with working code, not just explanations.
