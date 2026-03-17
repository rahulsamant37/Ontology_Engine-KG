from __future__ import annotations

from fastapi.testclient import TestClient

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
