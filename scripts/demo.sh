#!/usr/bin/env bash
set -euo pipefail

echo "Generating dataset..."
python3 data/generators/synthetic_invoice_generator.py --out data/freight_invoices_1k.csv --seed 42 --n 1000

echo "Running pipeline..."
rm -rf reports && mkdir -p reports
PYTHONPATH=. python3 -m src.run_pipeline

echo "Done. Reports in ./reports"
