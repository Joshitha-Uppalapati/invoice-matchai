# Development Notes
This project was built iteratively to simulate how a logistics audit engine
might evolve in a real environment rather than being designed top-down.

## Phase 1 — Core reconciliation
The first version only compared expected vs billed totals using deterministic
rate logic. The goal was correctness and explainability, not ML.

Key decision:
- prefer transparent rules over predictive modeling
- every flagged invoice must be explainable in plain English

This mirrors real freight audit workflows where disputes require traceable logic.

## Phase 2 — Synthetic dataset design
The dataset generator was expanded to inject realistic failure modes:

- missing fuel surcharges
- dropped accessorial fees
- underbilling within tolerance bands
- noisy but plausible invoice distributions

A fixed seed guarantees reproducibility. Every run produces identical results,
which makes debugging and benchmarking possible.

## Phase 3 — Anomaly detection
Isolation Forest was added as a secondary signal layer.

The goal was not prediction accuracy but edge-case discovery:
cases that pass deterministic rules but look statistically unusual.

This reflects how audit teams use heuristics plus statistical review,
not ML alone.

## Phase 4 — Explanation layer
Rule-based explanations were added first.
LLM explanations are optional and degrade gracefully when no API key is present.

This was intentional:
the pipeline must never depend on an external service to function.

## Constraints
The system favors:
- deterministic behavior
- reproducibility
- inspectable outputs
- low operational complexity

This is closer to real financial audit tooling than typical ML demos.

## Future directions
- configurable rule thresholds
- historical drift analysis
- dashboard visualization
- batch audit simulation at larger scale
