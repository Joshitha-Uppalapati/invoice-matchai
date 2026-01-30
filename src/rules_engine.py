import pandas as pd

def apply_leakage_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    expected_total_col = "expected_total" if "expected_total" in df.columns else "expected_billed_total"
    actual_total_col = "actual_total_billed" if "actual_total_billed" in df.columns else "actual_billed_total"

    expected_fuel_col = "expected_fuel_surcharge" if "expected_fuel_surcharge" in df.columns else "fuel_surcharge_amount"
    actual_fuel_col = "actual_billed_fuel" if "actual_billed_fuel" in df.columns else "fuel_surcharge_amount"

    id_col = "invoice_id" if "invoice_id" in df.columns else "shipment_id"

    # Coerce numeric
    for c in [expected_total_col, actual_total_col, expected_fuel_col, actual_fuel_col]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # --- Core leakage calc ---
    df["underbilled_amount"] = (df[expected_total_col] - df[actual_total_col]).fillna(0.0)

    # Flag only if meaningful leakage (avoid rounding noise)
    # (both an absolute floor and a % floor)
    pct_floor = 0.05
    abs_floor = 5.0
    df["is_underbilled"] = df["underbilled_amount"] > (pct_floor * df[expected_total_col]).fillna(0.0)
    df["is_underbilled"] &= df["underbilled_amount"] > abs_floor

    # --- Fuel surcharge missing ---
    # If expected fuel > $1 but actual fuel nearly zero, flag it.
    df["is_missing_fuel"] = False
    if expected_fuel_col in df.columns and actual_fuel_col in df.columns:
        df["is_missing_fuel"] = (df[expected_fuel_col].fillna(0.0) > 1.0) & (df[actual_fuel_col].fillna(0.0) <= 0.01)

    df["is_liftgate_dropped"] = False
    if "accessorial_services" in df.columns and "expected_accessorials" in df.columns and "actual_billed_accessorials" in df.columns:
        wants_liftgate = df["accessorial_services"].fillna("").str.contains("liftgate", case=False, regex=False)
        expected_acc = pd.to_numeric(df["expected_accessorials"], errors="coerce").fillna(0.0)
        actual_acc = pd.to_numeric(df["actual_billed_accessorials"], errors="coerce").fillna(0.0)
        df["is_liftgate_dropped"] = wants_liftgate & ((expected_acc - actual_acc) > 5.0)

    # --- Duplicate id ---
    df["is_duplicate"] = df.duplicated(subset=[id_col], keep=False)

    # --- Build flag_reason (vectorized) ---
    df["flag_reason"] = ""
    df.loc[df["is_underbilled"], "flag_reason"] = "UNDERBILLED"
    df.loc[df["is_missing_fuel"], "flag_reason"] = df["flag_reason"].where(df["flag_reason"] == "", df["flag_reason"] + "; ") + "MISSING_FUEL_SURCHARGE"
    df.loc[df["is_liftgate_dropped"], "flag_reason"] = df["flag_reason"].where(df["flag_reason"] == "", df["flag_reason"] + "; ") + "LIFTGATE_NOT_CHARGED"
    df.loc[df["is_duplicate"], "flag_reason"] = df["flag_reason"].where(df["flag_reason"] == "", df["flag_reason"] + "; ") + "POSSIBLE_DUPLICATE"

    # column for reporting
    df["is_flagged"] = df["flag_reason"] != ""

    return df