from src.ingest import load_invoice_data
from src.rate_engine import compute_expected_billing
from src.rules_engine import apply_leakage_rules
from src.reporting import summarize_leakage
import pandas as pd
import os
import json

def run_pipeline():
    data_path = "data/sample_invoices.csv"
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)

    leakage_csv_path = os.path.join(output_dir, "leakage_report.csv")
    summary_json_path = os.path.join(output_dir, "summary_metrics.json")

    df = load_invoice_data(data_path)
    df = compute_expected_billing(df)
    df = apply_leakage_rules(df)

    df.to_csv(leakage_csv_path, index=False)

    summary = summarize_leakage(df)

    with open(summary_json_path, "w") as f:
        json.dump(summary, f, indent=2)

    flagged = df[df["flag_reason"] != ""]
    print("=== PIPELINE SUMMARY ===")
    print("Total shipments:", summary["total_shipments"])
    print("Flagged shipments:", summary["flagged_shipments"], f"({summary['flag_rate_pct']}%)")
    print("Est. leakage $:", summary["estimated_revenue_leakage_usd"])
    print("Leakage report written to:", leakage_csv_path)
    print("Summary metrics written to:", summary_json_path)
    print("\nFlagged rows:")
    print(flagged[["shipment_id", "flag_reason", "underbilled_amount"]])

if __name__ == "__main__":
    run_pipeline()
