import pandas as pd
from .schema import REQUIRED_COLUMNS

SYNTHETIC_TO_PIPELINE_MAP = {
    "invoice_id": "shipment_id",
    "shipment_date": "ship_date",
    "dest_zip": "destination_zip",
    "weight_lbs": "weight_lb",
    "expected_linehaul": "base_linehaul_amount",
    "expected_fuel_surcharge": "fuel_surcharge_amount",
    "actual_total_billed": "actual_billed_total",
}

def load_invoice_data(csv_path: str) -> pd.DataFrame:
    """Load invoice CSV, accept either pipeline schema or synthetic generator schema, and normalize types."""
    df = pd.read_csv(csv_path)

    if "invoice_id" in df.columns and "shipment_id" not in df.columns:
        df = df.rename(columns=SYNTHETIC_TO_PIPELINE_MAP)

    if "customer_id" not in df.columns:
        df["customer_id"] = df["shipment_id"].astype(str).str[-6:].radd("CUST_")

    if "freight_class" not in df.columns:
        df["freight_class"] = 70  

    if "liftgate_required" not in df.columns:
        if "accessorial_services" in df.columns:
            s = df["accessorial_services"].fillna("").astype(str).str.lower()
            df["liftgate_required"] = s.str.contains("liftgate")
        else:
            df["liftgate_required"] = False

    if "liftgate_fee_charged" not in df.columns:
        if "actual_billed_accessorials" in df.columns:
            df["liftgate_fee_charged"] = pd.to_numeric(df["actual_billed_accessorials"], errors="coerce").fillna(0.0)
        else:
            df["liftgate_fee_charged"] = 0.0

    # Validate after mapping
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize booleans
    df["liftgate_required"] = (
        df["liftgate_required"]
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes", "y"])
        if df["liftgate_required"].dtype != bool
        else df["liftgate_required"]
    )

    # Normalize numerics
    numeric_cols = [
        "distance_miles",
        "weight_lb",
        "liftgate_fee_charged",
        "fuel_surcharge_amount",
        "base_linehaul_amount",
        "actual_billed_total",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize date
    if "ship_date" in df.columns:
        df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")

    # Cleanup ids
    df["shipment_id"] = df["shipment_id"].astype(str).str.strip()
    df["customer_id"] = df["customer_id"].astype(str).str.strip()

    return df
