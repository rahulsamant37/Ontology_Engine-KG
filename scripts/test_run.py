from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from main import app


def main() -> None:
    client = TestClient(app)
    sample_file = Path("data/sample_events.json")
    events = json.loads(sample_file.read_text())

    for event in events:
        response = client.post("/ingest", json=event)
        response.raise_for_status()

    query_payload = {
        "question": "Why did the Indian stock market move today?",
    }
    query_response = client.post("/query", json=query_payload)
    query_response.raise_for_status()

    print("=== Query Result ===")
    print(json.dumps(query_response.json(), indent=2))

    graph_response = client.get("/graph")
    graph_response.raise_for_status()
    print("=== Graph Snapshot ===")
    print(json.dumps(graph_response.json(), indent=2))


if __name__ == "__main__":
    main()
