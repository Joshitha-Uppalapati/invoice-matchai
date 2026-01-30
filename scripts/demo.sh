#!/usr/bin/env bash
set -euo pipefail

rm -rf reports
mkdir -p reports

PYTHONPATH=. python3 -m src.run_pipeline --data data/freight_invoices_1k.csv

echo ""
echo "Wrote:"
ls -la reports | sed -n '1,20p'