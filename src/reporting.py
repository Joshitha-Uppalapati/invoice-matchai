import pandas as pd

def summarize_leakage(df: pd.DataFrame) -> dict:
    flagged = df[df["flag_reason"] != ""].copy()

    total_shipments = len(df)
    flagged_shipments = len(flagged)

    leakage_series = flagged["underbilled_amount"].clip(lower=0)
    total_leakage_usd = round(float(leakage_series.sum()), 2)

    if "customer_id" in df.columns:
        top_customers = (
            flagged.groupby("customer_id")["underbilled_amount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        ).to_dict()
    else:
        top_customers = {}

    return {
        "total_shipments": total_shipments,
        "flagged_shipments": flagged_shipments,
        "flag_rate_pct": round((flagged_shipments / total_shipments) * 100.0, 2),
        "estimated_revenue_leakage_usd": total_leakage_usd,
        "top_customers_by_leakage_usd": top_customers
    }
