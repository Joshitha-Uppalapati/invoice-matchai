import argparse
import os

from src.ingest import load_invoice_data
from src.rate_engine import compute_expected_billing
from src.rules_engine import apply_leakage_rules
from src.reporting import write_leakage_report, write_summary_metrics
from src.anomaly import run_anomaly_detection


def run_pipeline(
    data_path: str,
    reports_dir: str,
    contamination: float,
) -> None:
    df = load_invoice_data(data_path)

    if "expected_total" not in df.columns:
        df = compute_expected_billing(df)

    flagged = apply_leakage_rules(df)

    os.makedirs(reports_dir, exist_ok=True)

    leakage_report_path = os.path.join(reports_dir, "leakage_report.csv")
    summary_metrics_path = os.path.join(reports_dir, "summary_metrics.json")
    anomaly_report_path = os.path.join(reports_dir, "anomaly_report.csv")

    write_leakage_report(flagged, leakage_report_path)
    write_summary_metrics(flagged, summary_metrics_path)

    adf = run_anomaly_detection(df, contamination=contamination)
    top = adf[adf["anomaly_flag"]].copy()

    cols = [
        "invoice_id",
        "carrier",
        "distance_miles",
        "weight_lbs",
        "expected_total",
        "actual_total_billed",
        "leakage_amount",
        "error_injected",
        "anomaly_score",
    ]
    cols = [c for c in cols if c in top.columns]
    top = top.sort_values("anomaly_score").head(200)[cols]
    top.to_csv(anomaly_report_path, index=False)

    total = len(df)
    flagged_n = int((flagged["flag_reason"].fillna("") != "").sum())
    leakage = float(flagged["underbilled_amount"].clip(lower=0).sum())

    print("=== PIPELINE SUMMARY ===")
    print(f"Total shipments: {total}")
    print(f"Flagged shipments: {flagged_n} ({flagged_n/total*100:.1f}%)")
    print(f"Est. leakage $: {leakage:.2f}")
    print(f"Leakage report written to: {leakage_report_path}")
    print(f"Summary metrics written to: {summary_metrics_path}")
    print(f"Anomaly report written to: {anomaly_report_path}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/freight_invoices_1k.csv")
    p.add_argument("--reports-dir", default="reports")
    p.add_argument("--contamination", type=float, default=0.06)
    args = p.parse_args()

    run_pipeline(
        data_path=args.data,
        reports_dir=args.reports_dir,
        contamination=args.contamination,
    )


if __name__ == "__main__":
    main()