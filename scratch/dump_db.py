import sys
import os
import datetime
import decimal

# Add app to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app'))
from db import get_connection

def sql_escape_val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return '1' if v else '0'
    if isinstance(v, (int, float, decimal.Decimal)):
        return str(v)
    if isinstance(v, bytes):
        return str(int.from_bytes(v, 'big'))
    if isinstance(v, datetime.datetime):
        return f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(v, datetime.date):
        return f"'{v.strftime('%Y-%m-%d')}'"
    s = str(v)
    s = s.replace('\\', '\\\\').replace("'", "\\'").replace('\r', '\\r').replace('\n', '\\n')
    return f"'{s}'"

def main():
    conn = get_connection()
    cursor = conn.cursor()

    sql_lines = []
    sql_lines.append('-- ========================================================')
    sql_lines.append('-- TyresCart Scraping — Complete MySQL Database Dump & Seed')
    sql_lines.append(f'-- Export Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    sql_lines.append('-- ========================================================\n')
    sql_lines.append('SET NAMES utf8mb4;')
    sql_lines.append('SET FOREIGN_KEY_CHECKS = 0;\n')

    tables = [
        ('userTbl', 'userid'),
        ('fileTbl', 'file_id'),
        ('logTbl', 'id'),
    ]

    total_counts = {}

    for table_name, pk in tables:
        sql_lines.append('-- --------------------------------------------------------')
        sql_lines.append(f'-- Table structure and data for: {table_name}')
        sql_lines.append('-- --------------------------------------------------------')
        
        # Get CREATE TABLE statement directly from MySQL
        cursor.execute(f'SHOW CREATE TABLE `{table_name}`')
        create_stmt = cursor.fetchone()
        create_sql = list(create_stmt.values())[1]
        sql_lines.append(f'DROP TABLE IF EXISTS `{table_name}`;')
        sql_lines.append(create_sql + ';\n')

        # Get rows
        cursor.execute(f'SELECT * FROM `{table_name}` ORDER BY `{pk}` ASC')
        rows = cursor.fetchall()
        total_counts[table_name] = len(rows)

        if rows:
            cols = list(rows[0].keys())
            col_str = ', '.join([f'`{c}`' for c in cols])
            sql_lines.append(f'INSERT INTO `{table_name}` ({col_str}) VALUES')
            val_rows = []
            for r in rows:
                row_vals = [sql_escape_val(r[c]) for c in cols]
                val_rows.append('  (' + ', '.join(row_vals) + ')')
            sql_lines.append(',\n'.join(val_rows) + ';\n')

    sql_lines.append('SET FOREIGN_KEY_CHECKS = 1;')

    dump_sql = '\n'.join(sql_lines)
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database_dump.sql')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(dump_sql)

    print(f'Successfully generated {out_file} ({len(dump_sql)} bytes)')
    for t, c in total_counts.items():
        print(f'  - {t}: {c} rows')
    conn.close()

if __name__ == '__main__':
    main()
