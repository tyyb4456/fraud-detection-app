import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

ART = Path(__file__).resolve().parents[1] / "ml" / "artifacts"
SAMPLE = json.loads((ART / "sample_request.json").read_text())


def test_health():
    with TestClient(app) as c:
        assert c.get("/health").json()["model_loaded"] is True


def test_predict_returns_probability_and_reasons():
    with TestClient(app) as c:
        r = c.post("/predict", json=SAMPLE)
        assert r.status_code == 200
        body = r.json()
        assert 0 <= body["fraud_probability"] <= 1
        assert len(body["top_reasons"]) == 5


def test_unseen_category_is_422():
    with TestClient(app) as c:
        r = c.post("/predict", json={**SAMPLE, "channel": "zzz"})
        assert r.status_code == 422


def test_missing_field_is_422():
    bad = {k: v for k, v in SAMPLE.items() if k != "amount_usd"}
    with TestClient(app) as c:
        assert c.post("/predict", json=bad).status_code == 422


def test_batch():
    with TestClient(app) as c:
        r = c.post("/predict/batch", json={"transactions": [SAMPLE, SAMPLE]})
        assert r.status_code == 200
        assert len(r.json()["predictions"]) == 2