"""
app/index_products_es.py - CLI tool to index active products from MySQL into Elasticsearch.

Usage:
    venv\\Scripts\\python.exe app/index_products_es.py --check
    venv\\Scripts\\python.exe app/index_products_es.py --recreate --batch-size 500
    venv\\Scripts\\python.exe app/index_products_es.py --product-id 1042
    venv\\Scripts\\python.exe app/index_products_es.py --search "Michelin 225/45R17"
"""

import os
import sys
import time
import argparse
import logging

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from services.es_service import es_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("es_indexer")


def check_status():
    print("\n--- Elasticsearch Connection & Index Status ---")
    status = es_service.check_connection()
    print(f"URL:          {status.get('url')}")
    print(f"Connected:    {'YES' if status.get('connected') else 'NO'}")
    if not status.get("connected"):
        print(f"Error:        {status.get('error')}")
        return False

    print(f"Cluster:      {status.get('cluster_name')}")
    print(f"ES Version:   {status.get('version')}")
    print(f"Index Name:   {status.get('index_name')}")
    print(f"Index Exists: {'YES' if status.get('index_exists') else 'NO'}")
    print(f"Doc Count:    {status.get('doc_count')}")
    print("-----------------------------------------------\n")
    return True


def run_indexing(recreate: bool = False, batch_size: int = 500, only_active: bool = False):
    target = "active products" if only_active else "all products"
    print(f"\nStarting Elasticsearch bulk indexing for {target}...")
    print(f"Target Index: {es_service.index_name}")
    print(f"Recreate:     {recreate}")
    print(f"Batch Size:   {batch_size}")
    print(f"Only Active:  {only_active}")

    start_time = time.time()
    res = es_service.index_all_products(batch_size=batch_size, recreate=recreate, only_active=only_active)
    elapsed = time.time() - start_time

    if res.get("success"):
        print(f"\n[SUCCESS] {res.get('message')}")
        print(f"Indexed:  {res.get('indexed')} documents")
        print(f"Failed:   {res.get('failed')} documents")
        print(f"Batches:  {res.get('batches')}")
        print(f"Time:     {elapsed:.2f} seconds")
    else:
        print(f"\n[ERROR] Indexing failed: {res.get('error')}")
        if res.get("indexed"):
            print(f"Partially indexed: {res.get('indexed')} documents")


def index_single(product_id: int):
    print(f"\nIndexing single product #{product_id} into Elasticsearch...")
    success = es_service.index_single_product(product_id)
    if success:
        print(f"[SUCCESS] Product #{product_id} synchronized with Elasticsearch.")
    else:
        print(f"[ERROR] Failed to synchronize product #{product_id} with Elasticsearch.")


def search_test(query: str):
    print(f"\nSearching products for '{query}'...")
    res = es_service.search_products(query=query, page=1, per_page=5)
    if not res.get("success"):
        print(f"[ERROR] Search failed: {res.get('error')}")
        return

    print(f"Total Matches: {res.get('total')}")
    items = res.get("items", [])
    for idx, item in enumerate(items, 1):
        print(f"  {idx}. [{item.get('sku')}] {item.get('name')} | Brand: {item.get('brand_name')} | Status: {item.get('status')} | Price: AED {item.get('effective_price')} | Stock: {item.get('stock_qty')}")


def main():
    parser = argparse.ArgumentParser(description="Elasticsearch Products Indexer")
    parser.add_argument("--check", action="store_true", help="Check Elasticsearch connection and index health")
    parser.add_argument("--recreate", action="store_true", help="Recreate the index mapping before indexing")
    parser.add_argument("--only-active", action="store_true", help="Index only active products (skip inactive)")
    parser.add_argument("--batch-size", type=int, default=500, help="Bulk indexing batch size (default: 500)")
    parser.add_argument("--product-id", type=int, help="Index or update a single product by ID")
    parser.add_argument("--search", type=str, help="Execute a test search query")

    args = parser.parse_args()

    if args.check:
        check_status()
    elif args.product_id:
        index_single(args.product_id)
    elif args.search:
        search_test(args.search)
    else:
        run_indexing(recreate=args.recreate, batch_size=args.batch_size, only_active=args.only_active)


if __name__ == "__main__":
    main()
