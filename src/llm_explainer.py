from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class Explanation:
    shipment_id: str
    explanation: str
    model: str
    used_llm: bool


def build_rule_explanation(row: pd.Series) -> str:
    carrier = str(row.get("carrier", "")).strip()

    actual_total = float(row.get("actual_billed_total", row.get("actual_total_billed", 0.0)) or 0.0)
    expected_total = float(row.get("expected_billed_total", row.get("expected_total", 0.0)) or 0.0)
    underbilled = float(row.get("underbilled_amount", 0.0) or 0.0)

    parts = []
    if carrier:
        parts.append(f"Carrier: {carrier}.")
    parts.append(f"Actual billed total: ${actual_total:,.2f}. Expected total: ${expected_total:,.2f}.")

    reasons = str(row.get("flag_reason", "")).strip()
    if reasons:
        parts.append(f"Flags: {reasons}.")

    if underbilled > 0:
        parts.append(f"Estimated underbilling: ${underbilled:,.2f}.")
    else:
        parts.append("No positive underbilling amount calculated.")

    if "MISSING_FUEL_SURCHARGE" in reasons:
        fuel_amt = float(row.get("fuel_surcharge_amount", row.get("actual_billed_fuel", 0.0)) or 0.0)
        exp_fuel = float(row.get("expected_fuel_surcharge", 0.0) or 0.0)
        dist = float(row.get("distance_miles", 0.0) or 0.0)
        parts.append(
            f"Fuel looks missing for a {dist:,.0f} mile move "
            f"(billed fuel: ${fuel_amt:,.2f}, expected fuel: ${exp_fuel:,.2f})."
        )

    if "LIFTGATE_NOT_CHARGED" in reasons:
        lg_req = bool(row.get("liftgate_required", False))
        lg_fee = float(row.get("liftgate_fee_charged", 0.0) or 0.0)
        parts.append(f"Liftgate required: {lg_req}. Liftgate fee billed: ${lg_fee:,.2f}.")

    return " ".join(parts).strip()


def llm_explain(text: str, model: str, api_key: Optional[str]) -> Optional[str]:
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        resp = client.responses.create(
            model=model,
            input=f"Rewrite this as a short professional logistics audit explanation:\n\n{text}",
            max_output_tokens=120,
        )
        out = (resp.output_text or "").strip()
        return out or None

    except Exception as e:
        print(f"[LLM disabled] {type(e).__name__}")
        return None
