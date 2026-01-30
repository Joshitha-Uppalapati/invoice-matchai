import argparse
import json
import os

import pandas as pd

from src.ingest import load_invoice_data
from src.rate_engine import compute_expected_billing
from src.rules_engine import apply_leakage_rules
from src.reporting import summarize_leakage

try:
    from sklearn.ensemble import IsolationForest
except Exception:
    IsolationForest = None


def _write_anomaly_report(df: pd.DataFrame, out_path: str, seed: int) -> None:
    if IsolationForest is None:
        return

    df = df.copy()
    num_cols = [
        "distance_miles",
        "weight_lb",
        "base_linehaul_amount",
        "fuel_surcharge_amount",
        "actual_billed_total",
    ]
    for c in num_cols:
        if c not in df.columns:
            return

    X = df[num_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    model = IsolationForest(n_estimators=200, contamination=0.05, random_state=seed)
    pred = model.fit_predict(X)
    scores = model.score_samples(X)

    out = df.copy()
    out["anomaly_flag"] = (pred == -1)
    out["anomaly_score"] = scores

    cols = ["shipment_id", "carrier", "actual_billed_total", "anomaly_flag", "anomaly_score"]
    cols = [c for c in cols if c in out.columns]
    out.sort_values("anomaly_score", ascending=True)[cols].to_csv(out_path, index=False)


def run_pipeline(data_path: str, out_dir: str, seed: int) -> None:
    os.makedirs(out_dir, exist_ok=True)

    df = load_invoice_data(data_path)
    df = compute_expected_billing(df)
    df = apply_leakage_rules(df)

    leakage_report_path = os.path.join(out_dir, "leakage_report.csv")
    summary_metrics_path = os.path.join(out_dir, "summary_metrics.json")
    anomaly_report_path = os.path.join(out_dir, "anomaly_report.csv")

    flagged = df[df["flag_reason"].fillna("") != ""].copy()
    cols = ["shipment_id", "flag_reason", "underbilled_amount"]
    cols = [c for c in cols if c in flagged.columns]
    flagged[cols].to_csv(leakage_report_path, index=False)

    summary = summarize_leakage(df)
    with open(summary_metrics_path, "w") as f:
        json.dump(summary, f, indent=2)

    _write_anomaly_report(df, anomaly_report_path, seed)

    print("=== PIPELINE SUMMARY ===")
    print(f"Total shipments: {summary['total_shipments']}")
    print(
        f"Flagged shipments: {summary['flagged_shipments']} ({summary['flag_rate_pct']}%)"
    )
    print(f"Est. leakage $: {summary['estimated_revenue_leakage_usd']}")
    print(f"Leakage report written to: {leakage_report_path}")
    print(f"Summary metrics written to: {summary_metrics_path}")
    if os.path.exists(anomaly_report_path):
        print(f"Anomaly report written to: {anomaly_report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default="data/freight_invoices_1k.csv",
        help="Path to input CSV",
    )
    parser.add_argument(
        "--outdir",
        default="reports",
        help="Output directory",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (anomaly model)",
    )
    args = parser.parse_args()
    run_pipeline(args.data, args.outdir, args.seed)


if __name__ == "__main__":
    main()