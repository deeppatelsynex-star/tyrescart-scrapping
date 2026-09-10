import sys
import os
import time

sys.path.insert(0, 'app')
from services.product_importer import ProductImporter

csv_path = r'C:\Users\admin\Downloads\PSA-New-22-08.csv'
if not os.path.exists(csv_path):
    print(f"Error: CSV file not found at {csv_path}")
    sys.exit(1)

print(f"Starting import from {csv_path}...")
t0 = time.time()
with open(csv_path, 'rb') as f:
    res = ProductImporter.import_csv(f.read(), user_id=1)
elapsed = time.time() - t0

print("="*60)
print(f"Import finished in {elapsed:.2f} seconds.")
print(f"Success: {res.get('success')}")
print(f"Total Rows: {res.get('total_rows')}")
print(f"Products Created: {res.get('imported')}")
print(f"Products Updated: {res.get('updated')}")
print(f"Errors ({len(res.get('errors', []))}):")
for err in res.get('errors', [])[:10]:
    print("  ", err)
print("="*60)
