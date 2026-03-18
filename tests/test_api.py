from __future__ import annotations

from fastapi.testclient import TestClient

from api.deps import get_public_data_service
from main import app


def test_end_to_end_query_flow() -> None:
    client = TestClient(app)

    ingest_payload = {
        "source": "unit_test_news",
        "payload": {
            "text": "RBI sees inflation pressure as oil rises and NIFTY reacts to bond yield changes.",
            "metrics": {},
        },
    }
    ingest_resp = client.post("/ingest", json=ingest_payload)
    assert ingest_resp.status_code == 200

    query_resp = client.post(
        "/query",
        json={"question": "What macro risks are increasing in India right now?"},
    )
    assert query_resp.status_code == 200
    body = query_resp.json()

    assert "insight" in body
    assert "confidence" in body
    assert isinstance(body["drivers"], list)
    assert "reasoning_logs" in body

    graph_resp = client.get("/graph")
    assert graph_resp.status_code == 200
    graph_body = graph_resp.json()
    assert "entities" in graph_body
    assert "relationships" in graph_body


def test_unstructured_payload_ingests_successfully() -> None:
    client = TestClient(app)

    ingest_payload = {
        "source": "unit_test_unstructured",
        "payload_type": "unstructured",
        "payload": {
            "raw_text": "RBI signaled inflation risk while oil rose 3.2% and NIFTY fell.",
        },
    }
    ingest_resp = client.post("/ingest", json=ingest_payload)
    assert ingest_resp.status_code == 200


def test_structured_payload_validation_error() -> None:
    client = TestClient(app)

    invalid_payload = {
        "source": "unit_test_structured_invalid",
        "payload_type": "structured",
        "payload": {
            "text": "Missing required title and event_type.",
            "metrics": [{"name": "Inflation", "value": 5.2, "unit": "%"}],
        },
    }
    ingest_resp = client.post("/ingest", json=invalid_payload)
    assert ingest_resp.status_code == 422


def test_public_ingestion_endpoint() -> None:
    class FakePublicDataService:
        def fetch_structured_events(self, country_code: str, start_year: int, end_year: int, indicators=None):
            return [
                {
                    "source": "world_bank:FP.CPI.TOTL.ZG",
                    "payload_type": "structured",
                    "payload": {
                        "title": "Inflation update",
                        "text": "Inflation for IN was 5.1% in 2024.",
                        "event_type": "inflation_update",
                        "country": "IN",
                        "timestamp": "2024-12-31T00:00:00+00:00",
                        "metrics": [
                            {
                                "name": "Inflation (CPI, annual %)",
                                "value": 5.1,
                                "unit": "%",
                                "period": "2024",
                            }
                        ],
                        "tags": ["public_api", "world_bank"],
                        "entities": ["IN", "Inflation"],
                    },
                }
            ]

    app.dependency_overrides[get_public_data_service] = FakePublicDataService
    client = TestClient(app)

    response = client.post(
        "/ingest/public",
        json={"country_code": "IN", "start_year": 2023, "end_year": 2024},
    )
    assert response.status_code == 200
    assert response.json()["ingested_items"] == 1

    app.dependency_overrides.clear()
