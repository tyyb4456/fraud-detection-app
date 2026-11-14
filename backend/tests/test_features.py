import pandas as pd
import pytest

from app.features import BOOL_COLS, CAT_COLS, FEATURE_COLS, NUM_COLS, build_features

CATS = {c: ["a", "b", "c"] for c in CAT_COLS}


def make_df() -> pd.DataFrame:
    row = {c: 1.0 for c in NUM_COLS}
    row.update({c: "a" for c in CAT_COLS})
    row.update({c: True for c in BOOL_COLS})
    return pd.DataFrame([row])


def test_column_order():
    df = make_df()
    out = build_features(df[df.columns[::-1]], CATS)   # shuffled input
    assert list(out.columns) == FEATURE_COLS


def test_bools_become_ints():
    out = build_features(make_df(), CATS)
    assert all(out[c].dtype.kind in "iu" for c in BOOL_COLS)


def test_categories_fixed_levels():
    out = build_features(make_df(), CATS)
    assert all(list(out[c].cat.categories) == CATS[c] for c in CAT_COLS)


def test_unseen_category_raises():
    df = make_df()
    df.loc[0, "channel"] = "zzz"
    with pytest.raises(ValueError):
        build_features(df, CATS)


def test_missing_column_raises():
    with pytest.raises(ValueError):
        build_features(make_df().drop(columns=["amount_usd"]), CATS)