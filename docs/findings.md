# Invoice-MatchAI Findings Report

## Overview
This project simulates a freight invoice audit pipeline that reconciles billed
shipments against contracted rate expectations and flags recoverable leakage.

The dataset contains 1,000 synthetic but realistic freight invoices designed to
mirror common billing structures in LTL and parcel logistics:
linehaul charges, fuel surcharges, accessorials, and liftgate fees.

The goal is not model accuracy in an ML benchmark sense. The goal is operational:
identify billing inconsistencies that a real logistics audit team could recover
as revenue.

---

## Key Results
- Total shipments analyzed: **1,000**
- Shipments flagged: **47**
- Flag rate: **4.7%**
- Estimated recoverable leakage: **$8,537.32**

This means roughly 1 in 20 shipments contained a detectable billing issue.
At scale, a carrier or shipper processing millions of shipments annually would
see material financial impact from a leakage rate in this range.

---

## Types of Leakage Detected

### 1. Underbilling
The majority of flagged invoices were categorized as **UNDERBILLED**.

These occur when the actual billed total is lower than the expected contractual
rate calculated from:

- distance
- weight
- base linehaul pricing
- expected surcharges

This can represent:

- rating engine errors
- missed tariff updates
- incorrect rate tables
- manual overrides

Underbilling is often invisible without automated reconciliation because each
invoice looks reasonable in isolation.

---

### 2. Missing Fuel Surcharge
Several shipments were flagged with:

`UNDERBILLED; MISSING_FUEL_SURCHARGE`

Fuel surcharges are dynamic and tied to distance and market indices. When
missing or incorrectly applied, the error compounds across large shipment
volumes.

Patterns observed:

- long-distance shipments disproportionately affected
- fuel present in invoice schema but zero or mismatched in value

This reflects a common real-world failure mode where surcharge logic breaks
during system migrations or contract updates.

---

### 3. Liftgate Not Charged
Liftgate-required shipments without billed liftgate fees were detected.

These are operational leakage events tied to:

- accessorial capture failures
- driver handheld data not syncing
- incorrect service codes

Accessorial leakage is one of the most frequent audit findings in real freight
operations because it depends on field execution, not just pricing logic.

---

## Anomaly Detection Layer
Beyond deterministic rule-based checks, the system applies Isolation Forest to detect statistical outliers across key billing features:

- distance_miles
- weight_lb
- base_linehaul_amount
- fuel_surcharge_amount
- actual_billed_total

This adds a second detection layer focused on pattern deviation rather than predefined thresholds.

### Anomaly Results
- 5% contamination threshold (~50 shipments flagged)
- 23 anomalies overlapped with rule-based leakage flags
- 27 shipments passed rule checks but showed abnormal pricing structure

Common anomaly patterns included:
- unusually high fuel-to-linehaul ratios
- extreme weight-to-price combinations
- distance-to-cost mismatches
- edge cases near rule thresholds

This demonstrates a hybrid detection advantage:

Rules catch known billing errors.  
Isolation Forest surfaces suspicious edge cases rules cannot express cleanly.

In real logistics auditing, these edge cases often represent:
- pricing drift
- contract misconfiguration
- carrier-specific billing quirks
- silent leakage not visible to static rules

The anomaly layer acts as an early warning system rather than a final verdict.

---

## Accuracy Perspective
Because this dataset is synthetic, the “ground truth” is known. The rule engine
is intentionally deterministic and designed to recover injected leakage.

This pipeline is not a predictive ML model competing for benchmark accuracy.
It is a **deterministic audit engine** with anomaly detection layered on top
to surface unknown unknowns.

In real logistics environments, explainability and traceability matter more than
black-box model scores. Each flagged invoice includes a clear explanation of:

- what rule triggered
- expected vs billed values
- estimated financial impact

That transparency is critical for recovery workflows and customer disputes.

---

## Business Impact Interpretation
Even at small scale:

- 4.7% leakage rate
- ~$8.5K recovered from 1K shipments

Extrapolated to 1M shipments annually:

- ~47,000 problematic invoices
- ~$8.5M potential recovery

Real freight audit vendors operate at this scale. Automated reconciliation is
not a nice-to-have; it is core revenue protection infrastructure.

This project demonstrates the mechanics behind those systems:

- deterministic rate validation
- accessorial enforcement
- anomaly surfacing
- explainable audit trails

---

## Conclusion
Invoice-MatchAI is a prototype freight audit engine that models how logistics
companies detect billing leakage in production.

The pipeline shows that:

- small percentage errors accumulate into meaningful revenue loss
- rule engines catch structured failures
- anomaly detection highlights edge cases
- explainable output enables operational recovery

The system is intentionally simple, reproducible, and transparent so the logic
can be inspected end-to-end. The emphasis is reliability and interpretability,
not model complexity.

This mirrors real-world logistics audit priorities.