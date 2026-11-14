"""Train the fraud model. Run from backend/:  uv run python -m ml.train"""
from __future__ import annotations

import datetime
import json
import time
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, log_loss, precision_recall_curve, roc_auc_score
from sklearn.model_selection import StratifiedKFold

from app.features import FEATURE_COLS, build_category_levels, build_features

BACKEND = Path(__file__).resolve().parents[1]
DATA = BACKEND / "data"
ART = BACKEND / "ml" / "artifacts"
TARGET = "is_fraud"

PARAMS = dict(
    num_leaves=4, max_depth=2, min_child_samples=253, reg_lambda=1.34, reg_alpha=0.138,
    colsample_bytree=0.473, subsample=0.926, subsample_freq=1, cat_smooth=34,
    learning_rate=0.05, n_jobs=-1, verbose=-1,
)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    train = pd.read_csv(DATA / "train.csv")
    test = pd.read_csv(DATA / "test.csv")
    train[TARGET] = train[TARGET].astype(int)

    cats = build_category_levels(train, test)
    X = build_features(train, cats)
    y = train[TARGET].to_numpy()

    # ---- 5-fold CV ----
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof = np.zeros(len(X))
    iters = []
    t0 = time.time()
    for fold, (tr, va) in enumerate(skf.split(X, y), 1):
        m = lgb.LGBMClassifier(**PARAMS, n_estimators=6000, random_state=42 + fold)
        m.fit(
            X.iloc[tr], y[tr],
            eval_set=[(X.iloc[va], y[va])], eval_metric="auc",
            callbacks=[lgb.early_stopping(200, verbose=False)],
        )
        oof[va] = m.predict_proba(X.iloc[va])[:, 1]
        iters.append(m.best_iteration_)
        print(f"fold {fold}: AUC {roc_auc_score(y[va], oof[va]):.5f} | "
              f"iters {m.best_iteration_} | {time.time() - t0:.0f}s", flush=True)

    auc = roc_auc_score(y, oof)
    pr = average_precision_score(y, oof)
    ll = log_loss(y, oof)
    print(f"\nOOF ROC AUC {auc:.5f} | PR AUC {pr:.5f} | LogLoss {ll:.5f}")

    # ---- threshold from OOF (max F1) ----
    prec, rec, thr = precision_recall_curve(y, oof)
    f1 = 2 * prec[:-1] * rec[:-1] / (prec[:-1] + rec[:-1] + 1e-12)
    k = int(np.argmax(f1))
    threshold = float(thr[k])
    print(f"Best-F1 threshold {threshold:.4f} | precision {prec[k]:.3f} | recall {rec[k]:.3f}")

    table = {}
    for t in [0.05, 0.1, 0.2, 0.3, 0.5]:
        pred = oof >= t
        tp = int((pred & (y == 1)).sum())
        table[str(t)] = {
            "precision": round(tp / max(int(pred.sum()), 1), 4),
            "recall": round(tp / int((y == 1).sum()), 4),
        }

    # ---- final model on all rows ----
    n_final = int(np.mean(iters) * 1.15)
    final = lgb.LGBMClassifier(**PARAMS, n_estimators=n_final, random_state=42)
    final.fit(X, y)
    final.booster_.save_model(str(ART / "model.txt"))

    # ---- artifacts ----
    (ART / "categories.json").write_text(json.dumps(cats, indent=2))
    (ART / "feature_list.json").write_text(json.dumps(FEATURE_COLS, indent=2))
    metrics = {
        "oof_roc_auc": round(auc, 5), "oof_pr_auc": round(pr, 5), "oof_logloss": round(ll, 5),
        "threshold": threshold,
        "threshold_precision": round(float(prec[k]), 4),
        "threshold_recall": round(float(rec[k]), 4),
        "precision_recall_by_threshold": table,
        "n_estimators": n_final,
        "train_rows": len(train), "test_rows": len(test),
        "trained_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    (ART / "metrics.json").write_text(json.dumps(metrics, indent=2))
    sample = json.loads(train.loc[train[TARGET] == 1, FEATURE_COLS].iloc[[0]].to_json(orient="records"))[0]
    (ART / "sample_request.json").write_text(json.dumps(sample, indent=2))

    # ---- sanity check: reload and predict ----
    booster = lgb.Booster(model_file=str(ART / "model.txt"))
    idx = np.random.RandomState(0).choice(len(X), 20000, replace=False)
    mean_pred = float(booster.predict(X.iloc[idx]).mean())
    assert abs(mean_pred - y.mean()) < 0.01, f"mean prediction {mean_pred:.4f} vs rate {y.mean():.4f}"
    print(f"Sanity OK: mean prediction {mean_pred:.4f} vs fraud rate {y.mean():.4f}")
    print(f"Artifacts saved in {ART}")


if __name__ == "__main__":
    main()