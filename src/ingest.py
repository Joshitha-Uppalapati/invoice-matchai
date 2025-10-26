import pandas as pd
from .schema import REQUIRED_COLUMNS  # <-- this line is important

def load_invoice_data(csv_path: str) -> pd.DataFrame:
    """Load invoice CSV, validate schema, and normalize datatypes."""
    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Booleans
    if "liftgate_required" in df.columns:
        df["liftgate_required"] = (
            df["liftgate_required"]
            .astype(str)
            .str.lower()
            .isin(["true","1","yes","y"])
        )

    # Numerics
    numeric_cols = [
        "distance_miles","weight_lb","liftgate_fee_charged",
        "fuel_surcharge_amount","base_linehaul_amount","actual_billed_total"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Dates
    if "ship_date" in df.columns:
        df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")

    # Cleanup
    df["shipment_id"] = df["shipment_id"].astype(str).str.strip()
    df["customer_id"] = df["customer_id"].astype(str).str.strip()

    return df
