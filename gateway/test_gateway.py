#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "skills" / "fortior-knowledge-contributor" / "examples" / "experience-example.json"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["FORTIOR_GATEWAY_MODE"] = "open"
        os.environ["FORTIOR_GATEWAY_SINK"] = "mock"
        os.environ["FORTIOR_GATEWAY_MOCK_LOG"] = str(Path(tmp) / "submissions.jsonl")
        os.environ["FORTIOR_GATEWAY_RATE_LIMIT_PER_HOUR"] = "100"

        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

        import gateway.app as gateway_app
        importlib.reload(gateway_app)

        from fastapi.testclient import TestClient

        client = TestClient(gateway_app.app)
        health = client.get("/health")
        assert health.status_code == 200, health.text
        assert health.json()["sink"] == "mock"

        payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        body = {
            "type": "experience",
            "payload": payload,
            "client_metadata": {
                "client_version": "test",
                "client_instance_id": "integration-test-instance",
            },
        }

        first = client.post("/v1/contributions", json=body)
        assert first.status_code == 200, first.text
        first_json = first.json()
        assert first_json["ok"] is True
        assert first_json["duplicate"] is False
        assert str(first_json["record_id"]).startswith("mock-")

        second = client.post("/v1/contributions", json=body)
        assert second.status_code == 200, second.text
        assert second.json()["duplicate"] is True

        bad = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        bad["contributor"]["username"] = ""
        bad_resp = client.post(
            "/v1/contributions",
            json={"type": "experience", "payload": bad, "client_metadata": {}},
        )
        assert bad_resp.status_code == 400, bad_resp.text

        log_path = Path(os.environ["FORTIOR_GATEWAY_MOCK_LOG"])
        lines = log_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
        stored = json.loads(lines[0])
        assert stored["payload"]["contributor"]["username"] == payload["contributor"]["username"]

    print("Gateway mock tests: PASS")


if __name__ == "__main__":
    main()
