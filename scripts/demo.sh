cat > scripts/demo.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

python3 data/generators/synthetic_invoice_generator.py --out data/freight_invoices_1k.csv --seed 42 --n 1000
rm -rf reports && mkdir -p reports
PYTHONPATH=. python3 -m src.run_pipeline --data data/freight_invoices_1k.csv

echo
echo "Outputs:"
ls -la reports
SH
