import pandas as pd
from difflib import SequenceMatcher
import numpy as np
from pathlib import Path

def fuzzy_ratio(a: str, b: str) -> float:
    if pd.isna(a) or pd.isna(b):
        return 0.0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def match_lane(invoice_row: pd.Series, rate_table: pd.DataFrame):
    inv_lane = f"{invoice_row['origin']}->{invoice_row['destination']}".lower()
    rate_table = rate_table.copy()
    rate_table["lane_key"] = (rate_table["origin"] + "->" + rate_table["destination"]).str.lower()
    rate_table["lane_sim"] = rate_table["lane_key"].apply(lambda x: fuzzy_ratio(inv_lane, x))
    best_idx = rate_table["lane_sim"].idxmax()
    return rate_table.loc[best_idx], float(rate_table.loc[best_idx, "lane_sim"])

def reconcile_invoices(invoices_df: pd.DataFrame, rates_df: pd.DataFrame, rate_tolerance_pct: float = 2.0):
    results = []
    for _, inv in invoices_df.iterrows():
        best_contract, lane_score = match_lane(inv, rates_df)

        expected_rate = best_contract["contract_rate_per_mile"]
        expected_fuel_pct = best_contract["allowed_fuel_surcharge_pct"]
        expected_accessorial = best_contract["allowed_accessorial_desc"]
        expected_accessorial_cap = best_contract["allowed_accessorial_cap"]

        rate_diff_pct = ((inv["rate_billed_per_mile"] - expected_rate) / expected_rate) * 100
        fuel_diff_pct_points = inv["fuel_surcharge_pct"] - expected_fuel_pct
        accessorial_sim = fuzzy_ratio(inv["accessorial_desc"], expected_accessorial)
        accessorial_over_cap = inv["accessorial_amount"] - expected_accessorial_cap

        flags = []
        if rate_diff_pct > rate_tolerance_pct:
            flags.append("RATE_OVER_CONTRACT")
        if inv["fuel_surcharge_pct"] > expected_fuel_pct:
            flags.append("FUEL_SURCHARGE_OVER_CONTRACT")
        if accessorial_sim < 0.75:
            flags.append("UNRECOGNIZED_ACCESSORIAL_DESC")
        if accessorial_over_cap > 0:
            flags.append("ACCESSORIAL_OVER_CAP")

        confidence_score = np.mean([lane_score, accessorial_sim])

        per_mile_over = max(0, inv["rate_billed_per_mile"] - expected_rate) * inv["miles_billed"]
        fuel_base = expected_rate * inv["miles_billed"]
        fuel_over = 0
        if inv["fuel_surcharge_pct"] > expected_fuel_pct:
            fuel_over = fuel_base * ((inv["fuel_surcharge_pct"] - expected_fuel_pct) / 100)
        accessorial_over = max(0, accessorial_over_cap)
        recoverable_amount = per_mile_over + fuel_over + accessorial_over

        results.append({
            "invoice_id": inv["invoice_id"],
            "load_id": inv["load_id"],
            "origin": inv["origin"],
            "destination": inv["destination"],
            "rate_diff_pct": round(rate_diff_pct, 2),
            "fuel_diff_pct_points": round(fuel_diff_pct_points, 2),
            "accessorial_similarity": round(accessorial_sim, 3),
            "flags": ";".join(flags) if flags else "OK",
            "confidence_score": round(confidence_score, 3),
            "recoverable_amount_est": round(recoverable_amount, 2),
        })

    df = pd.DataFrame(results)
    summary = {
        "total_invoices": len(df),
        "pct_flagged": round((df["flags"] != "OK").sum() / len(df) * 100, 2) if len(df) else 0,
        "total_recoverable_usd": round(df["recoverable_amount_est"].sum(), 2),
    }
    return df, summary

def main():
    root = Path(__file__).resolve().parents[1]
    invoices = pd.read_csv(root / "data" / "invoices_sample.csv")
    rates = pd.read_csv(root / "data" / "rates_sample.csv")

    results, summary = reconcile_invoices(invoices, rates)

    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    results.to_csv(reports / "reconciliation_report.csv", index=False)
    pd.Series(summary).to_json(reports / "summary_metrics.json", indent=2)
    print("Reconciliation complete.")
    print("Summary:\n", summary)

if __name__ == "__main__":
    main()
