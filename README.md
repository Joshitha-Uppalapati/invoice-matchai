# Invoice-MatchAI — Smart Reconciliation of Freight Invoices vs. Rate Tables

![Python](https://img.shields.io/badge/Made%20with-Python-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Production--Ready-success)


## Overview
Invoice-MatchAI is a Python-based audit engine that validates carrier freight invoices against negotiated contract rate tables.

This project:
- Matches each invoice line (lane, mileage, accessorial fees) to the closest contract lane using fuzzy text similarity.
- Verifies billed rate-per-mile, fuel surcharge %, and accessorial charges against the contracted values and caps.
- Flags overbilling, duplicate / off-contract accessorials, and fuel surcharges above the agreed threshold.
- Estimates potential recoverable dollars and produces an audit-ready summary.

This simulates how revenue assurance teams detect billing leakage in transportation and logistics.

---

## Why this matters
In high-volume freight environments, even small per-load overbilling (e.g. $5–$20 in fuel surcharge or accessorials) quietly accumulates into millions of dollars annually if it’s not caught and disputed.

This tool automates:
- Rate validation
- Fuel surcharge compliance
- Accessorial enforcement
- Overcharge recovery estimation

This is core to controls like invoice reconciliation, revenue assurance, and contract compliance.

---

## How it works

### 1. Inputs
`data/invoices_sample.csv`  
Realistic invoice lines, including:
- `rate_billed_per_mile`
- `fuel_surcharge_pct`
- `accessorial_desc`
- `accessorial_amount`

`data/rates_sample.csv`  
Contract terms for each lane, including:
- `contract_rate_per_mile`
- `allowed_fuel_surcharge_pct`
- allowed accessorial descriptions and caps

### 2. Matching logic
Because invoice text is messy (“Liftgate svc” vs “Lift Gate Service”), the engine:
- Uses fuzzy similarity (SequenceMatcher / Levenshtein-style ratio) to match lanes and accessorial descriptions.
- Scores match confidence from 0.0 – 1.0 for audit defensibility.

### 3. Rule checks per invoice line
- `RATE_OVER_CONTRACT`: billed rate-per-mile exceeds contract by more than tolerance (default 2%).
- `FUEL_SURCHARGE_OVER_CONTRACT`: billed fuel surcharge % is above negotiated cap.
- `ACCESSORIAL_OVER_CAP`: accessorial billed above the max allowed dollar cap.
- `UNRECOGNIZED_ACCESSORIAL_DESC`: accessorial text does not match anything in the contract with high enough confidence.

### 4. Output
Running:
```bash
python3 src/reconciliation.py
```