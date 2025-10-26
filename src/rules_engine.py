import pandas as pd

def apply_leakage_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["underbilled_amount"] = df["expected_billed_total"] - df["actual_billed_total"]
    df["is_underbilled"] = df["underbilled_amount"] > (0.05 * df["expected_billed_total"])

    df["is_missing_fuel"] = (
        (df["distance_miles"] > 200) &
        (df["fuel_surcharge_amount"] <= 0.01)
    )

    df["is_liftgate_dropped"] = (
        (df["liftgate_required"] == True) &
        (df["liftgate_fee_charged"] <= 0.01)
    )

    # duplicate shipment id
    df["is_duplicate"] = df.duplicated(subset=["shipment_id"], keep=False)

    reasons = []
    for _, row in df.iterrows():
        r = []
        if row["is_underbilled"]:
            r.append("UNDERBILLED")
        if row["is_missing_fuel"]:
            r.append("MISSING_FUEL_SURCHARGE")
        if row["is_liftgate_dropped"]:
            r.append("LIFTGATE_NOT_CHARGED")
        if row["is_duplicate"]:
            r.append("POSSIBLE_DUPLICATE")
        reasons.append("; ".join(r) if r else "")
    df["flag_reason"] = reasons

    return df
