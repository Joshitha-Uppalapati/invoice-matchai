from src.ingest import load_invoice_data
from src.rate_engine import compute_expected_billing
from src.rules_engine import apply_leakage_rules
import pandas as pd
import os

def run_pipeline():
    data_path = "data/sample_invoices.csv"
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "leakage_report.csv")

    df = load_invoice_data(data_path)
    df = compute_expected_billing(df)
    df = apply_leakage_rules(df)

    df.to_csv(output_path, index=False)

    flagged = df[df["flag_reason"] != ""]
    print("=== PIPELINE SUMMARY ===")
    print("Total shipments:", len(df))
    print("Flagged shipments:", len(flagged))
    print("Leakage report written to:", output_path)
    print(flagged[["shipment_id", "flag_reason", "underbilled_amount"]])

if __name__ == "__main__":
    run_pipeline()
