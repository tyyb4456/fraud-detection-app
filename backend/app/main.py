"""FastAPI fraud-scoring service. Run from backend/:  uv run uvicorn app.main:app --reload"""
from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path

import lightgbm as lgb
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.features import FEATURE_COLS, build_features
from app.schemas import BatchRequest, BatchResponse, Prediction, Reason, Transaction

ART = Path(__file__).resolve().parents[1] / "ml" / "artifacts"
state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["booster"] = lgb.Booster(model_file=str(ART / "model.txt"))
    state["cats"] = json.loads((ART / "categories.json").read_text())
    state["metrics"] = json.loads((ART / "metrics.json").read_text())
    state["threshold"] = state["metrics"]["threshold"]
    yield
    state.clear()


app = FastAPI(title="Fraud Scoring API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


def score(rows: list[dict]) -> list[Prediction]:
    try:
        X = build_features(pd.DataFrame(rows), state["cats"])
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    booster = state["booster"]
    probs = booster.predict(X)
    contrib = booster.predict(X, pred_contrib=True)   # last column is the bias term

    out = []
    for i, p in enumerate(probs):
        pairs = sorted(zip(FEATURE_COLS, contrib[i][:-1]), key=lambda kv: -abs(kv[1]))[:5]
        reasons = [Reason(feature=f, value=rows[i][f], impact=round(float(v), 3)) for f, v in pairs]
        out.append(Prediction(
            fraud_probability=round(float(p), 5),
            flagged=bool(p >= state["threshold"]),
            threshold=state["threshold"],
            top_reasons=reasons,
        ))
    return out


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "booster" in state}


@app.get("/model-info")
def model_info():
    return state["metrics"]


@app.post("/predict", response_model=Prediction)
def predict(t: Transaction):
    return score([t.model_dump()])[0]


@app.post("/predict/batch", response_model=BatchResponse)
def predict_batch(req: BatchRequest):
    return BatchResponse(predictions=score([t.model_dump() for t in req.transactions]))


@app.get("/categories")
def categories():
    return state["cats"]


@app.get("/sample")
def sample():
    return json.loads((ART / "sample_request.json").read_text())