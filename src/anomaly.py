import pandas as pd
from sklearn.ensemble import IsolationForest


def run_anomaly_detection(
    df: pd.DataFrame,
    contamination: float = 0.06,
    random_state: int = 42,
) -> pd.DataFrame:
    x = df[
        [
            "distance_miles",
            "weight_lbs",
            "expected_linehaul",
            "expected_fuel_surcharge",
            "expected_accessorials",
            "expected_total",
            "actual_total_billed",
        ]
    ].copy()

    x = x.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    model = IsolationForest(
        n_estimators=250,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    pred = model.fit_predict(x)
    score = model.decision_function(x)

    out = df.copy()
    out["anomaly_flag"] = (pred == -1)
    out["anomaly_score"] = score
    return out
