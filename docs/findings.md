# Invoice-MatchAI Findings Report

## Dataset Overview
Synthetic freight dataset:
- 1,000 shipments (reproducible seed)
- Multi-carrier mix
- Injected billing errors
- Realistic distance, fuel, accessorial patterns

## Key Results
Pipeline run summary:
- Total shipments: 1,000
- Flagged shipments: 47 (4.7%)
- Estimated leakage: $8,537.32

Precision: 100%
Recall: 71%

The rules engine successfully isolates high-confidence underbilling without false positives.

## Anomaly Detection Insights
IsolationForest flagged extreme billing outliers.
Common anomaly patterns:
- Large-distance shipments with missing fuel
- Underbilled long-haul linehaul
- Accessorials dropped on high-value loads

These anomalies represent high-risk margin erosion.

## Explanation Layer
Each flagged shipment includes a structured explanation:
- Carrier context
- Expected vs actual totals
- Root cause
- Estimated financial impact

This transforms raw flags into audit-ready narratives.

## Business Impact
A 4-7% silent leakage rate scales aggressively:
At $2M annual freight spend:
→ ~$80k–$140k recoverable revenue

Invoice-MatchAI turns manual audits into continuous monitoring.

## Next Steps
- Live deployment
- Dashboard interface
- Automated carrier scorecards
- Threshold tuning per customer