import pandas as pd

def _distance_band(miles: float) -> str:
    if miles <= 300:
        return "local"
    elif miles <= 1000:
        return "regional"
    else:
        return "longhaul"

def _class_multiplier(freight_class: float) -> float:
    if freight_class <= 60:
        return 1.00
    elif freight_class <= 70:
        return 1.10
    elif freight_class <= 85:
        return 1.20
    else:
        return 1.35

def _lane_rate_per_lb(distance_band: str) -> float:
    if distance_band == "local":
        return 0.20
    elif distance_band == "regional":
        return 0.32
    else:
        return 0.48

def compute_expected_billing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    est_linehaul = []
    for _, row in df.iterrows():
        band = _distance_band(row["distance_miles"])
        per_lb = _lane_rate_per_lb(band)
        class_mult = _class_multiplier(row["freight_class"])
        linehaul_est = per_lb * class_mult * row["weight_lb"]
        est_linehaul.append(linehaul_est)

    df["expected_linehaul_amount"] = est_linehaul

    expected_fuel = []
    for _, row in df.iterrows():
        band = _distance_band(row["distance_miles"])
        if band == "local":
            pct = 0.05
        elif band == "regional":
            pct = 0.10
        else:
            pct = 0.15
        fuel_est = row["expected_linehaul_amount"] * pct
        expected_fuel.append(fuel_est)

    df["expected_fuel_amount"] = expected_fuel

    # flat fee if liftgate required
    df["expected_liftgate_fee"] = df["liftgate_required"].apply(
        lambda need: 75.0 if need else 0.0
    )

    df["expected_billed_total"] = (
        df["expected_linehaul_amount"]
        + df["expected_fuel_amount"]
        + df["expected_liftgate_fee"]
    )

    return df
