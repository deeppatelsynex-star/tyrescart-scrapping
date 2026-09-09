"""
app/migrations_restore_pks.py - Restores PRIMARY KEY and AUTO_INCREMENT on tables.

Safe to re-run: only selects base tables currently lacking a PRIMARY KEY.
Preserves existing column types and signedness from information_schema.
Safeguards data by checking for duplicates or NULLs before applying.

Usage:
  venv/bin/python app/migrations_restore_pks.py          # Dry run -- prints DDL only
  venv/bin/python app/migrations_restore_pks.py --apply  # Execute migration
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

# Known pivot and cache tables without an 'id' column, mapped to their canonical primary keys
NON_ID_TABLE_PKS = {
    'cache': ['`key`'],
    'cache_locks': ['`key`'],
    'password_reset_tokens': ['`email`'],
    'role_has_permissions': ['`permission_id`', '`role_id`'],
    'model_has_permissions': ['`permission_id`', '`model_id`', '`model_type`'],
    'model_has_roles': ['`role_id`', '`model_id`', '`model_type`'],
    'cart_price_rule_customer_groups': ['`cart_price_rule_id`', '`customer_group_id`'],
    'inventory_stock_source_links': ['`stock_id`', '`source_code`'],
    'inventory_salable_qty_cache': ['`stock_id`', '`sku`'],
}

# Tables with non-auto-increment 'id' (e.g. string surrogate ID)
NO_AUTO_INCREMENT_ID_TABLES = {
    'job_batches',
}


def get_tables_without_pk(conn):
    """Fetches all base tables in the current database that lack a PRIMARY KEY constraint."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.TABLE_NAME
            FROM information_schema.TABLES t
            LEFT JOIN information_schema.TABLE_CONSTRAINTS k
                   ON k.TABLE_SCHEMA = t.TABLE_SCHEMA
                  AND k.TABLE_NAME   = t.TABLE_NAME
                  AND k.CONSTRAINT_TYPE = 'PRIMARY KEY'
            WHERE t.TABLE_SCHEMA = DATABASE()
              AND t.TABLE_TYPE = 'BASE TABLE'
              AND k.CONSTRAINT_NAME IS NULL
            ORDER BY t.TABLE_NAME;
        """)
        return [r['TABLE_NAME'] for r in cur.fetchall()]


def get_column_info(conn, table_name, column_name):
    """Fetches COLUMN_TYPE and IS_NULLABLE from information_schema.COLUMNS."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COLUMN_TYPE, IS_NULLABLE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
        """, (table_name, column_name))
        return cur.fetchone()


def check_table_data_validity(conn, table_name, key_columns):
    """
    Checks whether key_columns contain NULLs or duplicates in existing data.
    Returns (is_valid, total_rows, distinct_rows, reason_msg).
    """
    cols_joined = ", ".join(key_columns)
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM `{table_name}`")
        total = cur.fetchone()['total']
        if total == 0:
            return True, 0, 0, ""

        null_conditions = " OR ".join([f"{col} IS NULL" for col in key_columns])
        cur.execute(f"SELECT COUNT(*) AS null_count FROM `{table_name}` WHERE {null_conditions}")
        null_count = cur.fetchone()['null_count']

        cur.execute(f"SELECT COUNT(DISTINCT {cols_joined}) AS distinct_count FROM `{table_name}`")
        distinct_count = cur.fetchone()['distinct_count']

        if null_count > 0 or distinct_count < total:
            msg = f"id has duplicates or NULLs ({total} rows, {distinct_count} distinct)"
            return False, total, distinct_count, msg

        return True, total, distinct_count, ""


def build_migration_plan(conn):
    """
    Inspects all tables lacking PKs and builds the DDL statements.
    Returns list of dicts: {'table': str, 'ddl': str, 'skip': bool, 'reason': str}
    """
    tables = get_tables_without_pk(conn)
    plan = []

    for tbl in tables:
        if tbl in NON_ID_TABLE_PKS:
            key_cols = NON_ID_TABLE_PKS[tbl]
            valid, total, distinct_cnt, reason = check_table_data_validity(conn, tbl, key_cols)
            if not valid:
                plan.append({
                    'table': tbl,
                    'ddl': '',
                    'skip': True,
                    'reason': reason
                })
                continue

            cols_sql = ", ".join(key_cols)
            ddl = f"ALTER TABLE `{tbl}` ADD PRIMARY KEY ({cols_sql});"
            plan.append({
                'table': tbl,
                'ddl': ddl,
                'skip': False,
                'reason': ''
            })

        elif tbl in NO_AUTO_INCREMENT_ID_TABLES:
            valid, total, distinct_cnt, reason = check_table_data_validity(conn, tbl, ['`id`'])
            if not valid:
                plan.append({
                    'table': tbl,
                    'ddl': '',
                    'skip': True,
                    'reason': reason
                })
                continue

            ddl = f"ALTER TABLE `{tbl}` ADD PRIMARY KEY (`id`);"
            plan.append({
                'table': tbl,
                'ddl': ddl,
                'skip': False,
                'reason': ''
            })

        else:
            col_info = get_column_info(conn, tbl, 'id')
            if not col_info:
                plan.append({
                    'table': tbl,
                    'ddl': '',
                    'skip': True,
                    'reason': "table has no 'id' column and is not in non-id mapping"
                })
                continue

            col_type = col_info['COLUMN_TYPE']
            valid, total, distinct_cnt, reason = check_table_data_validity(conn, tbl, ['`id`'])
            if not valid:
                plan.append({
                    'table': tbl,
                    'ddl': '',
                    'skip': True,
                    'reason': reason
                })
                continue

            ddl = f"ALTER TABLE `{tbl}` ADD PRIMARY KEY (`id`), MODIFY COLUMN `id` {col_type} NOT NULL AUTO_INCREMENT;"
            plan.append({
                'table': tbl,
                'ddl': ddl,
                'skip': False,
                'reason': ''
            })

    return plan


def run_verification(conn):
    """Runs the two verification queries specified in the prompt."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) AS tables_without_pk
            FROM information_schema.TABLES t
            LEFT JOIN information_schema.TABLE_CONSTRAINTS k
                   ON k.TABLE_SCHEMA = t.TABLE_SCHEMA
                  AND k.TABLE_NAME   = t.TABLE_NAME
                  AND k.CONSTRAINT_TYPE = 'PRIMARY KEY'
            WHERE t.TABLE_SCHEMA = DATABASE()
              AND t.TABLE_TYPE = 'BASE TABLE'
              AND k.CONSTRAINT_NAME IS NULL;
        """)
        no_pk = cur.fetchone()['tables_without_pk']

        cur.execute("""
            SELECT COUNT(*) AS auto_increment_columns
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND EXTRA LIKE '%auto_increment%';
        """)
        ai_cols = cur.fetchone()['auto_increment_columns']

    return no_pk, ai_cols


def main():
    parser = argparse.ArgumentParser(description="Restore PRIMARY KEY and AUTO_INCREMENT on tables")
    parser.add_argument('--apply', action='store_true', help="Execute the generated DDL statements")
    args = parser.parse_args()

    conn = get_connection()
    try:
        no_pk_initial, ai_initial = run_verification(conn)
        print("=" * 70)
        print(f"DATABASE KEY STATUS: {no_pk_initial} tables without PK, {ai_initial} auto_increment columns")
        print("=" * 70)

        plan = build_migration_plan(conn)
        if not plan:
            print("No tables found that lack a PRIMARY KEY. Everything is up to date!")
            return

        applied = 0
        failed = 0
        skipped = 0

        if not args.apply:
            print("\n[DRY RUN - DDL STATEMENTS]\n")
            for item in plan:
                if item['skip']:
                    print(f"-- SKIP {item['table']}: {item['reason']}")
                    skipped += 1
                else:
                    print(item['ddl'])
                    applied += 1

            print("\n" + "=" * 70)
            print(f"Dry run complete. {applied} statements generated, {skipped} skipped.")
            print("Run with --apply to execute the statements against the database.")
            print("=" * 70)

        else:
            print("\n[APPLYING DDL STATEMENTS]\n")
            with conn.cursor() as cur:
                for item in plan:
                    if item['skip']:
                        print(f"-- SKIP {item['table']}: {item['reason']}")
                        skipped += 1
                        continue

                    tbl = item['table']
                    ddl = item['ddl']
                    try:
                        print(f"Applying: {ddl}")
                        cur.execute(ddl)
                        conn.commit()
                        applied += 1
                    except Exception as e:
                        print(f"FAILED on `{tbl}`: {e}")
                        failed += 1

            no_pk_final, ai_final = run_verification(conn)
            print("\n" + "=" * 70)
            print(f"MIGRATION COMPLETE: {applied} applied, {failed} failed, {skipped} skipped.")
            print(f"tables_without_pk: {no_pk_initial} -> {no_pk_final}")
            print(f"auto_increment_columns: {ai_initial} -> {ai_final}")
            print("=" * 70)

            if no_pk_final == 0:
                print("SUCCESS: 0 tables without PRIMARY KEY remaining.")
            else:
                print(f"WARNING: {no_pk_final} tables still lack a PRIMARY KEY.")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
