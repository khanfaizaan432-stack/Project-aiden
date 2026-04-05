from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

from backend.main import app


def _make_test_image_bytes() -> bytes:
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAAM0lEQVR4nO3OMQEAAAjDMML/0Vn4oA0mQK1m2gQBAAAAAAAAAAAAAAAAAAAAAADgB0x9AAGq6n0KAAAAAElFTkSuQmCC"
    )


def test_evaluate_endpoint_returns_ensemble_probabilities() -> None:
    image_bytes = _make_test_image_bytes()

    with TestClient(app) as client:
        response = client.post(
            "/api/evaluate",
            files={"image": ("sample.png", image_bytes, "image/png")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_name"] == "ensemble"
    assert payload["predicted"]
    assert len(payload["agent_names"]) >= 1
    assert sum(payload["probabilities"].values()) == pytest.approx(1.0, rel=1e-4)