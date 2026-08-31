import json
import logging
from flask import g, request, session
from db import get_connection

logger = logging.getLogger(__name__)

def get_current_admin_user_id():
    """Extracts the currently authenticated admin user ID from g or session."""
    if hasattr(g, 'admin_user') and g.admin_user:
        if isinstance(g.admin_user, dict):
            return g.admin_user.get('id') or g.admin_user.get('userid')
        return getattr(g.admin_user, 'id', None) or getattr(g.admin_user, 'userid', None)
    return session.get('admin_user_id') or session.get('user_id')

def get_client_ip():
    """Extracts client IP address safely from headers or remote_addr."""
    if request:
        return request.headers.get('X-Forwarded-For', request.remote_addr or '').split(',')[0].strip()
    return None

def get_user_agent():
    """Extracts user agent string safely from request."""
    if request and request.user_agent:
        return str(request.user_agent.string)[:500]
    return None

def log_activity(
    action: str,
    entity_type: str,
    entity_id: int,
    old_values: dict = None,
    new_values: dict = None,
    website_id: int = None,
    store_id: int = None,
    user_id: int = None
):
    """
    Records an immutable audit log entry into `activity_logs`.
    Logs user ID, IP address, user agent, website, store, action, and JSON diffs.
    """
    if user_id is None:
        user_id = get_current_admin_user_id()

    ip_address = get_client_ip()
    user_agent = get_user_agent()

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO activity_logs (
                    user_id, website_id, store_id, action, entity_type, entity_id,
                    old_values, new_values, ip_address, user_agent, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                user_id,
                website_id,
                store_id,
                action,
                entity_type,
                entity_id,
                json.dumps(old_values) if old_values is not None else None,
                json.dumps(new_values) if new_values is not None else None,
                ip_address,
                user_agent
            ))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Failed to log activity for {entity_type} #{entity_id}: {e}")
        return None
    finally:
        conn.close()

def get_activity_logs(
    entity_type: str = None,
    entity_id: int = None,
    user_id: int = None,
    action: str = None,
    website_id: int = None,
    store_id: int = None,
    limit: int = 50,
    offset: int = 0
):
    """Fetches activity logs with joined admin user names for audit grids."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    a.id, a.user_id, a.website_id, a.store_id, a.action,
                    a.entity_type, a.entity_id, a.old_values, a.new_values,
                    a.ip_address, a.user_agent, a.created_at,
                    u.name AS user_name, u.email AS user_email, u.role AS user_role,
                    w.name AS website_name, s.name AS store_name
                FROM activity_logs a
                LEFT JOIN admin_users u ON a.user_id = u.id
                LEFT JOIN websites w ON a.website_id = w.id
                LEFT JOIN stores s ON a.store_id = s.id
                WHERE 1=1
            """
            params = []
            if entity_type:
                query += " AND a.entity_type = %s"
                params.append(entity_type)
            if entity_id:
                query += " AND a.entity_id = %s"
                params.append(entity_id)
            if user_id:
                query += " AND a.user_id = %s"
                params.append(user_id)
            if action:
                query += " AND a.action = %s"
                params.append(action)
            if website_id:
                query += " AND a.website_id = %s"
                params.append(website_id)
            if store_id:
                query += " AND a.store_id = %s"
                params.append(store_id)

            query += " ORDER BY a.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            for r in rows:
                if r.get('old_values') and isinstance(r['old_values'], str):
                    try:
                        r['old_values'] = json.loads(r['old_values'])
                    except Exception:
                        pass
                if r.get('new_values') and isinstance(r['new_values'], str):
                    try:
                        r['new_values'] = json.loads(r['new_values'])
                    except Exception:
                        pass
            return rows
    finally:
        conn.close()
