import io
import json

import pytest

from api import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "datasets").mkdir()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_preview_rejects_unknown_category(client):
    response = client.get("/api/preview/unknown")

    assert response.status_code == 400
    assert "Invalid category" in response.get_json()["error"]


def test_generate_dataset_returns_expected_metadata(client):
    response = client.post(
        "/api/generate",
        json={"size": 6, "seed": 123, "filename": "test_dataset.jsonl"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["samples_generated"] == 6
    assert body["filename"] == "test_dataset.jsonl"


def test_validate_dataset_accepts_valid_jsonl(client):
    sample = {
        "id": "test-1",
        "instruction": "Identify a breakout pattern",
        "response": "Breakout detected",
        "pattern_type": "price_action",
    }
    response = client.post(
        "/api/validate",
        data={"file": (io.BytesIO((json.dumps(sample) + "\n").encode()), "sample.jsonl")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["valid"] is True
    assert body["valid_count"] == 1
    assert body["error_count"] == 0


def test_validate_dataset_reports_invalid_rows(client):
    response = client.post(
        "/api/validate",
        data={"file": (io.BytesIO(b"{not-valid-json}\n"), "invalid.jsonl")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["valid"] is False
    assert body["error_count"] == 1
