"""Shared feature preprocessing: used by training AND the API so they never drift apart."""
from __future__ import annotations

import pandas as pd

NUM_COLS = [
    "amount_usd", "hours_since_last_txn", "txn_count_last_24h", "distance_from_home_km",
    "card_age_months", "customer_age", "account_balance_usd", "cvv_retry_count",
    "velocity_score", "time_of_day_hour", "day_of_week", "merchant_risk_score",
    "prior_disputes",
]
CAT_COLS = ["merchant_category", "card_type", "auth_method", "channel", "device_type"]
BOOL_COLS = [
    "is_foreign_transaction", "is_new_merchant", "used_vpn", "ip_country_mismatch",
    "billing_shipping_mismatch", "is_ai_generated_scam_attempt",
]
FEATURE_COLS = NUM_COLS + CAT_COLS + BOOL_COLS


def build_category_levels(*dfs: pd.DataFrame) -> dict[str, list[str]]:
    """Sorted union of each categorical column's values across the given frames."""
    return {
        c: sorted(set().union(*[set(d[c].astype(str)) for d in dfs]))
        for c in CAT_COLS
    }


def build_features(df: pd.DataFrame, categories: dict[str, list[str]]) -> pd.DataFrame:
    """Raw records -> model input: fixed column order, bools as int, fixed category levels."""
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    out = df[FEATURE_COLS].copy()
    for c in BOOL_COLS:
        out[c] = out[c].astype(int)
    for c in CAT_COLS:
        vals = out[c].astype(str)
        unseen = set(vals) - set(categories[c])
        if unseen:
            raise ValueError(f"Unseen values in '{c}': {sorted(unseen)}")
        out[c] = pd.Categorical(vals, categories=categories[c])
    return out