import os
import re


def parse_status_line(line):
    if not line:
        return None

    text = line.strip()
    if text.startswith('URL_STATUS|'):
        parts = text.split('|', 4)
        if len(parts) < 3:
            return None

        return {
            'url': parts[1].strip(),
            'status': parts[2].strip().lower(),
            'parent': parts[3].strip() if len(parts) > 3 else '',
            'type': parts[4].strip().lower() if len(parts) > 4 else '',
        }

    match = re.search(r'Ignoring response <403\s+(https?://\S+)>', text)
    if match:
        return {
            'url': match.group(1).strip(),
            'status': 'blocked',
            'parent': '',
            'type': '',
        }

    return None


def build_status_summary(statuses):
    summary = {'pending': 0, 'running': 0, 'done': 0, 'blocked': 0}

    for item in statuses or []:
        status = str(item.get('status', 'pending') or 'pending').strip().lower()
        if status in summary:
            summary[status] += 1
        else:
            summary['pending'] += 1

    return summary


def get_xlsx_info(file_path):
    """Returns (row_count, set_of_source_urls) for an XLSX file."""
    if not file_path or not os.path.exists(file_path):
        return 0, set()
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet = wb.active
        source_idx = None
        urls = set()
        count = 0
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i == 0:
                for idx, col in enumerate(row):
                    if col and str(col).strip().lower() in ('source', 'source_url', 'url', 'product_url', 'product url'):
                        source_idx = idx
                        break
                continue
            if not row or not any(row):
                continue
            count += 1
            if source_idx is not None and len(row) > source_idx and row[source_idx]:
                urls.add(str(row[source_idx]).strip())
        wb.close()
        return count, urls
    except Exception:
        return 0, set()

