import logging
from flask import g, request, session
from db import get_connection

logger = logging.getLogger(__name__)

class StoreContext:
    """
    Manages multi-website and multi-store resolution across HTTP requests.
    Identifies active Website, Store, and Store View (Locale) from:
    1. Query Params / Headers (e.g. `X-Website-Id: 1`, `X-Store-Id: 2`)
    2. Session Scope (Admin topbar selector)
    3. Host Domain / URL Route
    4. System Default Fallback
    """

    @staticmethod
    def get_all_websites(include_inactive=False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, code, name, domain, default_store_id, is_default, status, sort_order FROM websites"
                if not include_inactive:
                    sql += " WHERE status = 'active' AND deleted_at IS NULL"
                sql += " ORDER BY sort_order ASC, id ASC"
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_all_stores(website_id=None, include_inactive=False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, website_id, code, name, emirate, phone, email, is_active, sort_order FROM stores WHERE deleted_at IS NULL"
                params = []
                if not include_inactive:
                    sql += " AND is_active = 1"
                if website_id:
                    sql += " AND website_id = %s"
                    params.append(website_id)
                sql += " ORDER BY sort_order ASC, id ASC"
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_all_store_views(store_id=None, website_id=None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, store_id, website_id, code, name, locale, currency_code, is_active, sort_order FROM store_views WHERE deleted_at IS NULL AND is_active = 1"
                params = []
                if store_id:
                    sql += " AND store_id = %s"
                    params.append(store_id)
                if website_id:
                    sql += " AND website_id = %s"
                    params.append(website_id)
                sql += " ORDER BY sort_order ASC, id ASC"
                cursor.execute(sql, params)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_scope_tree():
        """
        Returns full hierarchy tree for Admin Topbar Scope Switcher:
        Global -> Websites -> Stores -> Store Views
        """
        websites = StoreContext.get_all_websites(include_inactive=True)
        stores = StoreContext.get_all_stores(include_inactive=True)
        store_views = StoreContext.get_all_store_views()

        # Map stores to websites
        stores_by_website = {}
        for s in stores:
            w_id = s.get('website_id') or 1
            stores_by_website.setdefault(w_id, []).append(s)

        # Map views to stores
        views_by_store = {}
        for v in store_views:
            s_id = v.get('store_id')
            views_by_store.setdefault(s_id, []).append(v)

        for s in stores:
            s['views'] = views_by_store.get(s['id'], [])

        for w in websites:
            w['stores'] = stores_by_website.get(w['id'], [])

        return {
            'global': {'id': None, 'name': 'Global (Master Defaults)'},
            'websites': websites
        }

    @staticmethod
    def resolve_current_context():
        """
        Resolves active Website, Store, and Store View for current request.
        Binds to Flask `g.current_website`, `g.current_store`, `g.current_store_view`.
        """
        # 1. Check Headers / Query params
        req_web_id = request.headers.get('X-Website-Id') or request.args.get('website_id')
        req_store_id = request.headers.get('X-Store-Id') or request.args.get('store_id')
        req_view_id = request.headers.get('X-Store-View-Id') or request.args.get('store_view_id')

        # 2. Check Session (Admin switcher selection)
        if not req_web_id and 'admin_active_website_id' in session:
            req_web_id = session['admin_active_website_id']
        if not req_store_id and 'admin_active_store_id' in session:
            req_store_id = session['admin_active_store_id']

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Resolve Website
                if req_web_id and str(req_web_id).isdigit():
                    cursor.execute("SELECT * FROM websites WHERE id = %s AND deleted_at IS NULL", (int(req_web_id),))
                    current_web = cursor.fetchone()
                else:
                    cursor.execute("SELECT * FROM websites WHERE is_default = 1 AND deleted_at IS NULL LIMIT 1")
                    current_web = cursor.fetchone()

                # Resolve Store
                if req_store_id and str(req_store_id).isdigit():
                    cursor.execute("SELECT * FROM stores WHERE id = %s AND deleted_at IS NULL", (int(req_store_id),))
                    current_store = cursor.fetchone()
                else:
                    web_id = current_web['id'] if current_web else 1
                    cursor.execute("SELECT * FROM stores WHERE website_id = %s AND deleted_at IS NULL ORDER BY sort_order ASC LIMIT 1", (web_id,))
                    current_store = cursor.fetchone()

                # Resolve Store View / Locale
                current_view = None
                if req_view_id and str(req_view_id).isdigit():
                    cursor.execute("SELECT * FROM store_views WHERE id = %s AND deleted_at IS NULL", (int(req_view_id),))
                    current_view = cursor.fetchone()
                elif current_store:
                    cursor.execute("SELECT * FROM store_views WHERE store_id = %s AND deleted_at IS NULL ORDER BY sort_order ASC LIMIT 1", (current_store['id'],))
                    current_view = cursor.fetchone()

                g.current_website = current_web
                g.current_store = current_store
                g.current_store_view = current_view

                return {
                    'website': current_web,
                    'store': current_store,
                    'store_view': current_view
                }
        finally:
            conn.close()
