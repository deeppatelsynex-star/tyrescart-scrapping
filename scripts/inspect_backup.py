import re

def inspect_table_rows():
    tables = ['products', 'product_attribute_values', 'product_inventories', 'product_websites', 'product_categories', 'brands', 'categories']
    current_table = None
    
    with open('backups/db/predev-pk-20260909.sql', 'r', encoding='utf-16-le', errors='ignore') as f:
        for line in f:
            for t in tables:
                if line.startswith(f'INSERT INTO `{t}`'):
                    # Count values by finding occurrences of '),(' or similar
                    count = len(re.findall(r'\),\s*\(', line)) + 1
                    print(f'{t}: {count} rows in this statement')

if __name__ == '__main__':
    inspect_table_rows()
