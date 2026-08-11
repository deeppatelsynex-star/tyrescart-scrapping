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
