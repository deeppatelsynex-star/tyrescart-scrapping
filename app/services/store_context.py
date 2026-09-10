import logging
from flask import g, request, session, has_app_context, has_request_context
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
    def get_all_store_views(store_id=None, website_id=None, include_inactive=False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, store_id, website_id, code, name, locale, currency_code, is_active, sort_order FROM store_views WHERE deleted_at IS NULL"
                params = []
                if not include_inactive:
                    sql += " AND is_active = 1"
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
    def get_stores_table_rows(filter_website=None, filter_store=None, filter_view=None):
        """
        Returns hierarchical rows matching Magento 'All Stores' view:
        Web Site | Store | Store View
        """
        import json
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        w.id AS website_id, w.name AS website_name, w.code AS website_code, w.sort_order AS website_sort_order, w.domain AS website_domain,
                        s.id AS store_id, s.name AS store_name, s.code AS store_code, s.root_category_id, s.default_store_view_id, s.sort_order AS store_sort_order,
                        v.id AS store_view_id, v.name AS store_view_name, v.code AS store_view_code, v.locale AS store_view_locale,
                        v.is_active AS store_view_is_active, v.sort_order AS store_view_sort_order
                    FROM websites w
                    LEFT JOIN stores s ON s.website_id = w.id AND s.deleted_at IS NULL
                    LEFT JOIN store_views v ON v.store_id = s.id AND v.deleted_at IS NULL
                    WHERE w.deleted_at IS NULL
                """
                params = []
                if filter_website:
                    sql += " AND (LOWER(w.name) LIKE %s OR LOWER(w.code) LIKE %s)"
                    kw = f"%{filter_website.lower().strip()}%"
                    params.extend([kw, kw])
                if filter_store:
                    sql += " AND (LOWER(s.name) LIKE %s OR LOWER(s.code) LIKE %s)"
                    kw = f"%{filter_store.lower().strip()}%"
                    params.extend([kw, kw])
                if filter_view:
                    sql += " AND (LOWER(v.name) LIKE %s OR LOWER(v.code) LIKE %s)"
                    kw = f"%{filter_view.lower().strip()}%"
                    params.extend([kw, kw])

                sql += " ORDER BY w.sort_order ASC, w.id ASC, s.sort_order ASC, s.id ASC, v.sort_order ASC, v.id ASC"
                cursor.execute(sql, params)
                rows = cursor.fetchall() or []
                for r in rows:
                    if r.get('store_name'):
                        try:
                            val = r['store_name']
                            if isinstance(val, str) and val.startswith('{'):
                                parsed = json.loads(val)
                                r['store_display_name'] = parsed.get('en') or next(iter(parsed.values()), val)
                            elif isinstance(val, dict):
                                r['store_display_name'] = val.get('en') or next(iter(val.values()), '')
                            else:
                                r['store_display_name'] = str(val)
                        except Exception:
                            r['store_display_name'] = str(r['store_name'])
                    else:
                        r['store_display_name'] = ''
                return rows
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
        Binds to Flask `g.current_website`, `g.current_store`, `g.current_store_view`,
        `g.current_language`, `g.current_direction`.
        """
        # 1. Check Headers / Query params
        req_web_id = None
        req_store_id = None
        req_view_id = None

        if has_request_context():
            req_web_id = request.headers.get('X-Website-Id') or request.args.get('website_id')
            req_store_id = request.headers.get('X-Store-Id') or request.args.get('store_id')
            req_view_id = request.headers.get('X-Store-View-Id') or request.args.get('store_view_id')

            # 2. Check Session (Admin switcher selection)
            if not req_web_id and 'admin_active_website_id' in session:
                req_web_id = session['admin_active_website_id']
            if not req_store_id and 'admin_active_store_id' in session:
                req_store_id = session['admin_active_store_id']
            if not req_view_id and 'admin_active_store_view_id' in session:
                req_view_id = session['admin_active_store_view_id']

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # If store_view_id is specified, fetch the view first to infer store/website if needed
                current_view = None
                if req_view_id and str(req_view_id).isdigit():
                    cursor.execute("SELECT * FROM store_views WHERE id = %s AND deleted_at IS NULL AND is_active = 1", (int(req_view_id),))
                    current_view = cursor.fetchone()
                    if current_view:
                        if not req_store_id:
                            req_store_id = current_view.get('store_id')
                        if not req_web_id:
                            req_web_id = current_view.get('website_id')
                    else:
                        # Stale or inactive view in session - clear it
                        if has_request_context() and 'admin_active_store_view_id' in session:
                            session.pop('admin_active_store_view_id', None)
                            session['admin_active_scope_name'] = 'All Store Views'

                # Resolve Website
                if req_web_id and str(req_web_id).isdigit():
                    cursor.execute("SELECT * FROM websites WHERE id = %s AND deleted_at IS NULL", (int(req_web_id),))
                    current_web = cursor.fetchone()
                else:
                    cursor.execute("SELECT * FROM websites WHERE is_default = 1 AND deleted_at IS NULL LIMIT 1")
                    current_web = cursor.fetchone()
                    if not current_web:
                        cursor.execute("SELECT * FROM websites WHERE deleted_at IS NULL ORDER BY sort_order ASC, id ASC LIMIT 1")
                        current_web = cursor.fetchone()

                # Resolve Store
                if req_store_id and str(req_store_id).isdigit():
                    cursor.execute("SELECT * FROM stores WHERE id = %s AND deleted_at IS NULL", (int(req_store_id),))
                    current_store = cursor.fetchone()
                else:
                    web_id = current_web['id'] if current_web else 1
                    cursor.execute("SELECT * FROM stores WHERE website_id = %s AND deleted_at IS NULL ORDER BY sort_order ASC, id ASC LIMIT 1", (web_id,))
                    current_store = cursor.fetchone()

                # Resolve Store View / Locale if not already resolved
                if not current_view:
                    if current_store and current_store.get('default_store_view_id'):
                        cursor.execute("SELECT * FROM store_views WHERE id = %s AND deleted_at IS NULL AND is_active = 1", (int(current_store['default_store_view_id']),))
                        current_view = cursor.fetchone()
                    if not current_view and current_store:
                        cursor.execute("SELECT * FROM store_views WHERE store_id = %s AND deleted_at IS NULL AND is_active = 1 ORDER BY sort_order ASC, id ASC LIMIT 1", (current_store['id'],))
                        current_view = cursor.fetchone()
                    if not current_view and current_web:
                        cursor.execute("SELECT * FROM store_views WHERE website_id = %s AND deleted_at IS NULL AND is_active = 1 ORDER BY sort_order ASC, id ASC LIMIT 1", (current_web['id'],))
                        current_view = cursor.fetchone()

                if has_app_context():
                    g.current_website = current_web
                    g.current_store = current_store
                    g.current_store_view = current_view
                    g.current_language = StoreContext.get_current_language()
                    g.current_direction = StoreContext.get_current_direction()
                    res_lang = g.current_language
                    res_dir = g.current_direction
                else:
                    res_lang = (current_view.get('locale') or current_view.get('code') or 'en') if current_view else 'en'
                    res_dir = 'rtl' if res_lang.split('-')[0].lower() in {'ar', 'fa', 'ur', 'he', 'ps', 'sd'} else 'ltr'

                return {
                    'website': current_web,
                    'store': current_store,
                    'store_view': current_view,
                    'language': res_lang,
                    'direction': res_dir
                }
        finally:
            conn.close()

    @classmethod
    def get_current_store(cls):
        """Returns the active Store record for the current request."""
        if has_app_context() and hasattr(g, 'current_store') and g.current_store is not None:
            return g.current_store
        ctx = cls.resolve_current_context()
        return ctx.get('store')

    @classmethod
    def get_current_store_view(cls):
        """Returns the active Store View record for the current request."""
        if has_app_context() and hasattr(g, 'current_store_view') and g.current_store_view is not None:
            return g.current_store_view
        ctx = cls.resolve_current_context()
        return ctx.get('store_view')

    @classmethod
    def get_current_website(cls):
        """Returns the active Website record for the current request."""
        if has_app_context() and hasattr(g, 'current_website') and g.current_website is not None:
            return g.current_website
        ctx = cls.resolve_current_context()
        return ctx.get('website')

    @classmethod
    def get_current_language(cls, fallback: str = "en") -> str:
        """
        Returns the active language code determined by the Store Context.
        1. Explicit g.current_language override if set
        2. Store View locale / code from active scope
        3. Query param ?locale=... / ?lang=...
        4. Session site_locale or cookie
        5. Fallback default ('en')
        """
        if has_app_context():
            # 0. Explicit g override
            g_lang = getattr(g, 'current_language', None)
            if g_lang and str(g_lang).strip():
                return str(g_lang).strip().lower()

            # 1. Active Store View
            view = getattr(g, 'current_store_view', None)
            if isinstance(view, dict):
                lang = view.get('locale') or view.get('code')
                if lang and str(lang).strip():
                    return str(lang).strip().lower()

        # 2. Session / Query / Cookie fallback
        if has_request_context():
            try:
                req_lang = (request.args.get('locale') or request.args.get('lang') or '').strip().lower()
                if req_lang:
                    return req_lang
                if 'site_locale' in session:
                    sess_lang = str(session['site_locale']).strip().lower()
                    if sess_lang:
                        return sess_lang
                cookie_lang = (request.cookies.get('site_locale') or '').strip().lower()
                if cookie_lang:
                    return cookie_lang
            except Exception:
                pass

        return (fallback or "en").strip().lower()

    @classmethod
    def get_current_direction(cls) -> str:
        """Returns 'rtl' if current language is Right-to-Left, otherwise 'ltr'."""
        if has_app_context() and hasattr(g, 'current_direction') and g.current_direction:
            return g.current_direction
        lang = cls.get_current_language()
        rtl_langs = {'ar', 'fa', 'ur', 'he', 'ps', 'sd'}
        base_lang = lang.split('-')[0].lower()
        return 'rtl' if base_lang in rtl_langs else 'ltr'

