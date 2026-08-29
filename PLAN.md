
> Complete micro-step implementation blueprint
> **Migrated from:** `TYRESCART_LARAVEL_PLAN.md` (Laravel 13 + Next.js). This is a stack-for-stack
> translation — same scope, same phases, same database schema, same feature set. No Laravel/PHP/
> Blade/Livewire/Composer/Artisan remain anywhere below except where explicitly named for context.
> **Frontend decision (deviates from the Laravel/Next.js original):** the customer-facing site is
> now a second Flask Blueprint (`site`) rendering Jinja2 templates — no Next.js, no separate
> deployable, no React. It shares the app/DB/Redis/ES with the admin panel. Dynamic, stateful
> interactions (cart, checkout, live search, tyre-finder cascades) still call the Flask JSON API
> (Phase 7, `@jwt_required()`) via `fetch()`/Alpine.js from the page, the same pattern Next.js used —
> just same-origin now. See Phase 8 for the full page-by-page mapping.
>
> **Backend (API):**   Flask 3.x (application factory + Blueprints) · Flask-JWT-Extended
>                      Gunicorn (gevent workers) behind Nginx · Elasticsearch 8 · Redis 7
>                      MySQL 8 · SQLAlchemy 2.x + Alembic (Flask-Migrate) · Celery + Redis broker + Flower
>
> **Admin Panel:**     Flask Blueprint (`admin`) · Jinja2 templates · Alpine.js v3 · TailAdmin theme
>                      (HTML/Tailwind assets adapted into Jinja2 includes/macros) · Tailwind CSS v4
>                      Vite · ApexCharts · Flatpickr · Flask-Login (session auth) · WTForms
>
> **Customer Frontend:** Flask Blueprint (`site`) · Jinja2 templates · Alpine.js v3 · Tailwind CSS v4
>                        Vite · Flask-Babel (EN/AR) · Flask-Login (session auth, customer-scoped)
>                        JSON API (Phase 7) consumed same-origin for cart/checkout/search/tyre-finder
>
> **NOTE:** Livewire is not applicable in this stack (Flask has no equivalent and none is needed) —
>           both the admin panel and the customer site use plain Jinja2 + Alpine.js, exactly as the
>           Laravel version used plain Blade + Alpine.js (no Livewire there either).

---

## LEGEND
- [ ] = Step not started
- [x] = Step completed
- Each step is one focused action — one migration, one component, one service, etc.
- All steps below are reset to **not started** — this is a fresh plan for a new stack;
  none of the Laravel implementation progress carries over.

---

## PHASE 0 — Project Layout (new — makes the rest of the plan concrete)

```
tyrescart-flask/
├── app/
│   ├── __init__.py                # create_app() application factory
│   ├── extensions.py               # db, migrate, jwt, login_manager, cors, celery, cache, limiter, mail
│   ├── config.py                   # Config / DevConfig / ProdConfig classes (reads .env via python-dotenv)
│   ├── models/                     # SQLAlchemy models, one module per domain (catalog.py, orders.py, ...)
│   ├── mixins/                     # SlugMixin, SoftDeleteMixin, TimestampMixin, SearchableMixin
│   ├── blueprints/
│   │   ├── admin/                  # Flask-Login session auth, Jinja2 views — mirrors Laravel Phase 6
│   │   │   ├── __init__.py
│   │   │   ├── auth.py, dashboard.py, products.py, orders.py, enquiries.py, customers.py,
│   │   │   │   brands.py, categories.py, coupons.py, banners.py, special_offers.py, blogs.py,
│   │   │   │   faqs.py, stores.py, purchase_orders.py, reports.py, settings.py, admin_users.py
│   │   ├── api/                    # Flask-JWT-Extended, JSON only — mirrors Laravel Phase 7
│   │   │   ├── __init__.py
│   │   │   ├── auth.py, products.py, search.py, brands.py, categories.py, tyre_finder.py,
│   │   │   │   cart.py, checkout.py, orders.py, account.py, addresses.py, reward_points.py,
│   │   │   │   content.py, blogs.py, payments/, quick_pay.py, enquiries.py
│   │   └── site/                   # Flask-Login session auth (customer), Jinja2 views — Phase 8
│   │       ├── __init__.py
│   │       ├── pages.py, catalog.py, tyre_finder.py, search.py, cart.py, checkout.py,
│   │       │   auth.py, account.py, content.py, blog.py
│   ├── services/                   # plain Python service classes — mirrors Laravel Phase 4
│   │   ├── cart_service.py, shipping_service.py, order_service.py, payment/, search_service.py,
│   │   │   tyre_finder_service.py, coupon_service.py, reward_points_service.py, email_service.py,
│   │   │   abandoned_cart_service.py, media_service.py, sitemap_service.py
│   ├── search/                     # Elasticsearch index definitions — mirrors Laravel app/Search
│   │   └── indexes/ (product_index.py, brand_index.py, blog_index.py, faq_index.py)
│   ├── tasks/                      # Celery tasks — mirrors Laravel app/Jobs
│   │   ├── mail_tasks.py, index_tasks.py, cron_tasks.py
│   ├── schemas/                    # Marshmallow schemas — mirrors Laravel Http/Resources
│   ├── forms/                      # WTForms — admin panel forms
│   ├── templates/
│   │   ├── admin/ (layouts/, auth/, dashboard.html, products/, orders/, ...)
│   │   ├── site/ (layouts/, partials/, home.html, tyres/, brands/, categories/, cart/,
│   │   │   checkout/, auth/, account/, blog/, ...)                           # Phase 8
│   │   └── emails/
│   ├── static/                     # admin.css, admin.js, site.css, site.js (Vite-built)
│   └── cli.py                      # Flask CLI commands (`flask elastic create-indexes`, etc.)
├── migrations/                     # Alembic (via Flask-Migrate)
├── tests/                          # pytest
├── celery_worker.py                # Celery app entrypoint
├── wsgi.py                         # Gunicorn entrypoint
├── vite.config.js
├── package.json
├── pyproject.toml                  # or requirements.txt + requirements-dev.txt
├── .env
└── Procfile                        # web (gunicorn), worker (celery), beat (celery beat), flower
```

- [ ] 0.1  Scaffold the directory layout above
- [ ] 0.2  Create `pyproject.toml` with core deps: flask, sqlalchemy, flask-sqlalchemy, flask-migrate,
          flask-jwt-extended, flask-login, flask-cors, flask-mail, flask-limiter, flask-caching,
          celery, redis, elasticsearch, pillow, python-slugify, authlib, marshmallow, wtforms,
          python-dotenv, gunicorn, gevent, mysqlclient (or pymysql), boto3 (optional S3), pytest
- [ ] 0.3  Create `app/config.py` with `Config`, `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`

---

## PHASE 1 — Foundation & Infrastructure

### 1.1 Project Bootstrap
- [ ] 1.1.1  Create new Flask project: `mkdir tyrescart-flask && cd tyrescart-flask && python -m venv .venv`
- [ ] 1.1.2  Pin Python version constraint to `^3.12` in `pyproject.toml`
- [ ] 1.1.3  Configure `.env`: APP_NAME, APP_URL, FLASK_ENV, SECRET_KEY (replaces APP_KEY)
- [ ] 1.1.4  Configure `.env`: DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD
          (assembled into `SQLALCHEMY_DATABASE_URI = mysql+pymysql://...` in config.py)
- [ ] 1.1.5  Configure `.env`: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
- [ ] 1.1.6  Configure `.env`: CACHE_TYPE=RedisCache, SESSION_TYPE=redis, CELERY_BROKER_URL=redis://...,
          CELERY_RESULT_BACKEND=redis://...
- [ ] 1.1.7  Configure `.env`: ELASTICSEARCH_HOST, ELASTICSEARCH_PORT, ELASTICSEARCH_INDEX_PREFIX
- [ ] 1.1.8  Generate `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] 1.1.9  Create `app/__init__.py` with `create_app()` factory; no boilerplate routes to remove
          (Flask ships with none — register blueprints here instead)
- [ ] 1.1.10 Set `BABEL_DEFAULT_LOCALE='en'`, `BABEL_SUPPORTED_LOCALES=['en', 'ar']` in config
          (used by both the admin panel locale switch and the customer `site` blueprint's
          `/en/...` `/ar/...` routes, see Phase 8)

### 1.2 Install Core Packages
- [ ] 1.2.1  Install Flask: `pip install "flask>=3.0"`
- [ ] 1.2.2  Install Gunicorn + gevent worker: `pip install gunicorn gevent`
          (replaces Laravel Octane/FrankenPHP — persistent worker processes, no per-request bootstrap)
- [ ] 1.2.3  Install Celery + Flower: `pip install celery flower` (replaces Laravel Horizon)
- [ ] 1.2.4  Install Elasticsearch Python client: `pip install "elasticsearch>=8,<9"`
          (replaces Laravel Scout — no Scout-equivalent package needed; a thin `SearchService`
          wraps the client directly, see 4.4.1)
- [ ] 1.2.5  Install Flask-SQLAlchemy + Flask-Migrate + PyMySQL/mysqlclient:
          `pip install flask-sqlalchemy flask-migrate pymysql`
- [ ] 1.2.6  Install Alembic (bundled with Flask-Migrate, no separate install needed)
- [ ] 1.2.7  Install Pillow for image processing: `pip install pillow`
          (replaces Spatie Media Library's image-conversion layer + Intervention Image)
- [ ] 1.2.8  Install python-slugify: `pip install python-slugify`
          (replaces Spatie Sluggable)
- [ ] 1.2.9  Install Flask-Login (admin session auth) + Flask-JWT-Extended (API token auth):
          `pip install flask-login flask-jwt-extended`
- [ ] 1.2.10 Install python-slugify-based mixin dependencies already covered in 1.2.8; install
          `boto3` only if S3-backed media storage is required (optional)
- [ ] 1.2.11 Install Authlib: `pip install authlib` (replaces Laravel Socialite for Google/Facebook OAuth)
- [ ] 1.2.12 Install redis-py: `pip install redis` (replaces Predis — same purpose, Python-native client)
- [ ] 1.2.13 Install Flask-Mail: `pip install flask-mail` (replaces Laravel Mail)
- [ ] 1.2.14 Install Flask-CORS, Flask-Limiter, Flask-Caching:
          `pip install flask-cors flask-limiter flask-caching`
- [ ] 1.2.15 Install Marshmallow (API schemas) + WTForms (admin forms):
          `pip install marshmallow wtforms flask-wtf`
- [ ] 1.2.16 Freeze all top-level configs into `app/extensions.py`: instantiate `db`, `migrate`, `jwt`,
          `login_manager`, `cors`, `cache`, `limiter`, `mail`, `celery` as module-level singletons,
          bind each to the app inside `create_app()`
- [ ] 1.2.17 Create `app/session_interface.py::DualCookieSessionInterface(SecureCookieSessionInterface)`
          Overrides `get_cookie_name(app)` (or `open_session`/`save_session` on older Flask) to
          return `app.config['ADMIN_SESSION_COOKIE_NAME']` (e.g. `admin_session`) when
          `request.path.startswith('/admin')`, else the default site cookie name — giving the
          `admin` and `site` blueprints two independent session cookies under one Flask app.
          Register via `app.session_interface = DualCookieSessionInterface()` in `create_app()`.
          Register a single `login_manager.user_loader` that queries `AdminUser` when
          `request.blueprint == 'admin'` (or path starts with `/admin`), else `User` — this is
          the mechanism `AdminUser` (3.7.14) and `User` (3.2.1) both rely on for session auth,
          replacing Laravel's separate `admin`/`web` guards with two cookies + one loader.

### 1.3 Install Frontend Packages (admin panel assets — unchanged tooling, still Vite/npm-based)
- [ ] 1.3.1  Install Tailwind CSS v4: `npm install tailwindcss @tailwindcss/vite`
- [ ] 1.3.2  Install Alpine.js v3: `npm install alpinejs`
- [ ] 1.3.3  Install Alpine.js plugins: `@alpinejs/focus @alpinejs/intersect @alpinejs/persist`
- [ ] 1.3.4  Install Tailwind typography plugin: `npm install @tailwindcss/typography`
- [ ] 1.3.5  Install Tailwind forms plugin: `npm install @tailwindcss/forms`
- [ ] 1.3.6  Install ApexCharts: `npm install apexcharts` (TailAdmin dashboard charts)
- [ ] 1.3.7  Install Flatpickr: `npm install flatpickr` (date pickers in admin forms)
- [ ] 1.3.8  Install jsvectormap: `npm install jsvectormap` (TailAdmin map widget)
- [ ] 1.3.9  Configure `vite.config.js`: input entrypoints (`app/static/src/site.js`, `site.css`,
          `admin.js`, `admin.css`); output manifest read by a small Jinja2 `vite_asset()` helper
          function (registered via `app.jinja_env.globals`) that replaces Laravel's `@vite` directive
- [ ] 1.3.10 Configure `app/static/src/site.css`: Tailwind v4 `@import` setup for the customer-facing
          `site` blueprint (Phase 8) — this is the full storefront's stylesheet, not a marginal
          marketing-page afterthought, since Flask now serves every customer-facing page
- [ ] 1.3.11 Configure `app/static/src/admin.css`: import TailAdmin styles + Tailwind v4
- [ ] 1.3.12 Configure `app/static/src/site.js`: Alpine.js init + site-wide stores (`cart`, `auth`)
          + `apiFetch()` helper for same-origin calls to `/api/v1/*` (see 8.1.5, 8.2)
- [ ] 1.3.13 Configure `app/static/src/admin.js`: Alpine.js + ApexCharts + Flatpickr + jsvectormap init
          Copy/adapt from `tailadmin-laravel-main/resources/js/app.js` and chart JS files —
          these are plain JS, framework-agnostic, so the port is a straight copy
- [ ] 1.3.14 Set up RTL support: `app/static/src/rtl.css` with Tailwind RTL overrides, shared by
          both the admin locale switch and the `site` blueprint's `ar` locale (Phase 8)
- [ ] 1.3.15 Run `npm install && npm run build` — verify manifest.json emitted and `vite_asset()` resolves it

### 1.4 Configure Application Server (Gunicorn — replaces Laravel Octane/FrankenPHP)
- [ ] 1.4.1  Install Gunicorn + gevent (done in 1.2.2); no separate binary to fetch (pure pip package)
- [ ] 1.4.2  Create `wsgi.py`: `from app import create_app; app = create_app()`
- [ ] 1.4.3  Set worker count in `gunicorn.conf.py`: `workers = (2 * cpu_count()) + 1`, `worker_class = "gevent"`
- [ ] 1.4.4  Configure `max_requests` / `max_requests_jitter` in `gunicorn.conf.py` to recycle workers
          periodically (guards against memory growth — the Python analogue of Octane's worker restarts)
- [ ] 1.4.5  Ensure `CartService`/`PaymentServiceFactory` are stateless plain classes instantiated
          per-request (no in-process singletons to worry about — Gunicorn workers are pre-fork,
          not persistent-in-memory-app like Octane, so no Octane-safe-singleton concern applies;
          instead rely on SQLAlchemy connection pooling and a shared redis-py connection pool)
- [ ] 1.4.6  Create `Procfile` for process management:
          `web: gunicorn -c gunicorn.conf.py wsgi:app`
          `worker: celery -A celery_worker.celery worker -Q default,mail,search,payments --loglevel=info`
          `beat: celery -A celery_worker.celery beat --loglevel=info`
          `flower: celery -A celery_worker.celery flower --port=5555`
- [ ] 1.4.7  Test: `gunicorn -c gunicorn.conf.py wsgi:app`

### 1.5 Configure Elasticsearch
> No third-party Scout driver package — `elasticsearch-py` is used directly via a thin `SearchService`.
> Config: `app/config.py` reads `ELASTICSEARCH_HOST` / `ELASTICSEARCH_INDEX_PREFIX` from `.env`.
> Index prefix: ELASTICSEARCH_INDEX_PREFIX=tyreslaravel (kept identical to the Laravel version for
> continuity, configurable in .env)
> Index names: {prefix}_products, {prefix}_brands, {prefix}_blogs, {prefix}_faqs
> Single source of truth: each `*Index` class's `index_name()` reads
> `current_app.config['ELASTICSEARCH_INDEX_PREFIX']` — no hardcoded strings anywhere

- [ ] 1.5.1  Create `app/extensions.py` ES client factory:
          `es_client = Elasticsearch(hosts=[app.config['ELASTICSEARCH_HOST']])`, bound in `create_app()`
- [ ] 1.5.2  Add to `.env`: `ELASTICSEARCH_HOST=http://127.0.0.1:9200`,
          `ELASTICSEARCH_INDEX_PREFIX=tyreslaravel`
- [ ] 1.5.3  Create `app/search/indexes/product_index.py`
          `index_name()` → `f"{current_app.config['ELASTICSEARCH_INDEX_PREFIX']}_products"`
          `mapping()` — dict of all flat field mappings (returns the ES mapping body)
          `settings()` — dict with Arabic analyzer + tyre synonym filter
- [ ] 1.5.4  Create `app/search/indexes/brand_index.py`
          `index_name()` → prefix + `_brands`, mapping: name, description_en/ar, country
- [ ] 1.5.5  Create `app/search/indexes/blog_index.py`
          `index_name()` → prefix + `_blogs`, mapping: title_en/ar, content_en/ar, excerpt
- [ ] 1.5.6  Create `app/search/indexes/faq_index.py`
          `index_name()` → prefix + `_faqs`, mapping: question_en/ar, answer_en/ar
- [ ] 1.5.7  Add Arabic analyzer to `ProductIndex.settings()`:
          analyzer 'arabic_standard': tokenizer=standard, filter=[lowercase, arabic_normalization, arabic_stemmer]
          Apply to name_ar, description_ar fields via analyzer parameter
- [ ] 1.5.8  Add synonym filter to `ProductIndex.settings()`:
          filter 'tyre_synonyms': type=synonym, synonyms=[tire=>tyre, suv=>4x4, alloy=>rim, etc.]
          Apply to name_en field via analyzer 'english_tyres' (standard + lowercase + tyre_synonyms)
- [ ] 1.5.9  Create Flask CLI command `flask elastic create-indexes` in `app/cli.py`
          Uses `es_client.indices.create(index=idx.index_name(), mappings=idx.mapping(), settings=idx.settings())`
          for each of the 4 Index classes, skipping any that already exist
          Register via `app.cli.add_command`
- [ ] 1.5.10 Test ES connection: `flask elastic create-indexes`
          Verify: tyreslaravel_products, tyreslaravel_brands, tyreslaravel_blogs, tyreslaravel_faqs created

### 1.6 Configure Celery + Flower (replaces Laravel Horizon)
- [ ] 1.6.1  Create `celery_worker.py`: builds a Celery app bound to the Flask app context
          (`ContextTask` pattern so tasks run with `app.app_context()` active)
- [ ] 1.6.2  Configure queues in `celery_worker.py` / `app/config.py`:
          `task_routes` mapping tasks to queues: `default`, `mail`, `search`, `payments`
- [ ] 1.6.3  Route all search-indexing tasks (`app/tasks/index_tasks.py`) to the `search` queue
          (high throughput)
- [ ] 1.6.4  Route all payment-webhook-processing tasks to the `payments` queue (isolated)
- [ ] 1.6.5  Route all email tasks (`app/tasks/mail_tasks.py`) to the `mail` queue
- [ ] 1.6.6  Protect the Flower dashboard: run behind Nginx basic-auth or `--basic_auth=user:pass`
          flag (Flower has no built-in app-level gate the way Horizon's `HorizonServiceProvider`
          does — the equivalent is reverse-proxy auth or restricting to an internal network)

---

## PHASE 2 — Database Migrations (All 35 Tables)
> Migrations are now Alembic revisions generated via Flask-Migrate (`flask db migrate -m "..."`,
> `flask db upgrade`) instead of Laravel migration classes. Column types map as:
> `DECIMAL(p,s)` → `db.Numeric(p, s)` · `ENUM(...)` → `db.Enum(...)` · `JSON` → `db.JSON` ·
> `BOOLEAN` → `db.Boolean` · `TIMESTAMP`/`DATETIME` → `db.DateTime` · `LONGTEXT`/`TEXT` → `db.Text` ·
> Soft deletes → a nullable `deleted_at` column + a `SoftDeleteMixin` that filters `deleted_at IS NULL`
> into every query via a SQLAlchemy `with_loader_criteria` event, instead of Laravel's `SoftDeletes` trait.
> Table/column names, ENUM values, and index definitions below are unchanged from the original schema.

### 2.1 Catalog Tables
- [ ] 2.1.1  Create Alembic revision: `create_categories_table`
          Columns: id, name_en, name_ar, slug, parent_id (nullable), image, description_en,
          description_ar, sort_order, status(active/inactive), meta_title_en, meta_title_ar,
          meta_desc_en, meta_desc_ar, created_at, updated_at, deleted_at
          Indexes: slug(unique), parent_id, status

- [ ] 2.1.2  Create Alembic revision: `create_brands_table`
          Columns: id, name, slug, logo, description_en, description_ar, country,
          sort_order, is_featured, status, meta_title_en, meta_desc_en, created_at, updated_at
          Indexes: slug(unique), is_featured, status

- [ ] 2.1.3  Create Alembic revision: `create_products_table`
          Columns:
          -- Identity
          id, sku VARCHAR(100) UNIQUE, name_en VARCHAR(500), name_ar VARCHAR(500),
          slug VARCHAR(600) UNIQUE, description_en LONGTEXT, description_ar LONGTEXT,
          short_desc_en TEXT, short_desc_ar TEXT
          -- Pricing
          price DECIMAL(10,3), sale_price DECIMAL(10,3) nullable,
          cost_price DECIMAL(10,3) nullable, currency CHAR(3) DEFAULT 'AED'
          -- Inventory
          stock_qty INT DEFAULT 0, stock_status ENUM(in_stock/out_of_stock/backorder),
          manage_stock BOOLEAN DEFAULT true, min_order_qty INT DEFAULT 1,
          max_order_qty INT DEFAULT 99
          -- Tire Dimensions (flat — no separate table)
          tire_width SMALLINT nullable, tire_height SMALLINT nullable,
          tire_rim DECIMAL(4,1) nullable, tire_size_label VARCHAR(30) nullable
          -- Tire Specs
          tire_speed_rating VARCHAR(5) nullable, tire_load_index VARCHAR(10) nullable,
          tire_type ENUM(summer/winter/all_season/all_terrain/mud_terrain) nullable,
          tire_pattern VARCHAR(100) nullable, run_flat BOOLEAN DEFAULT false,
          ev_rated BOOLEAN DEFAULT false, oem_approved BOOLEAN DEFAULT false,
          oem_brand VARCHAR(100) nullable
          -- EU Labels
          noise_level_db TINYINT nullable, fuel_efficiency CHAR(1) nullable,
          wet_grip CHAR(1) nullable
          -- Vehicle
          vehicle_type ENUM(car/bike/suv/van/ev/4x4) nullable
          -- Relations
          brand_id INT UNSIGNED nullable, category_id INT UNSIGNED nullable
          -- Media
          image_path VARCHAR(500) nullable, gallery_json JSON nullable
          -- Product Info
          weight DECIMAL(8,3) nullable, country_of_origin VARCHAR(100) nullable,
          warranty_months TINYINT nullable
          -- Flags
          is_featured BOOLEAN DEFAULT false, is_new BOOLEAN DEFAULT false,
          sort_order INT DEFAULT 0, status ENUM(active/inactive/draft) DEFAULT active,
          visibility ENUM(visible/not_visible/catalog/search) DEFAULT visible,
          pay_later_eligible BOOLEAN DEFAULT true
          -- SEO
          meta_title_en VARCHAR(255), meta_title_ar VARCHAR(255),
          meta_desc_en TEXT, meta_desc_ar TEXT, canonical_url VARCHAR(500) nullable
          -- Timestamps
          created_at, updated_at, deleted_at
          Indexes: sku(unique), slug(unique), brand_id, category_id,
          (tire_width, tire_height, tire_rim) composite, status+visibility composite,
          FULLTEXT(name_en, name_ar, sku, tire_size_label) — implemented as a MySQL FULLTEXT index
          via raw DDL in the Alembic revision (SQLAlchemy has no native FULLTEXT index construct,
          so use `op.execute("ALTER TABLE products ADD FULLTEXT INDEX ft_products (...)")`)

### 2.2 User Tables
- [x] 2.2.1  Create Alembic revision: `create_users_table` (`userTbl`)
          Columns: id, name, email(unique), phone, password_hash, locale CHAR(2) DEFAULT en,
          points_balance INT DEFAULT 0, social_provider nullable, social_id nullable,
          avatar nullable, status(active/inactive/banned) DEFAULT active,
          email_verified_at nullable, created_at, updated_at
          (no `remember_token` column — Flask-Login uses signed session cookies + optional
          "remember me" cookie, not a stored DB token; JWT refresh tokens for the API are
          tracked separately if refresh-token revocation is needed, see 5.3)

- [ ] 2.2.2  Create Alembic revision: `create_addresses_table`
          Columns: id, user_id, label(home/work/other), name, phone, line1, line2 nullable,
          city, area nullable, emirate, country DEFAULT AE, is_default BOOLEAN DEFAULT false,
          created_at, updated_at
          Indexes: user_id, (user_id, is_default)

### 2.3 Vehicles Table
- [ ] 2.3.1  Create Alembic revision: `create_vehicles_table`
          Columns: id, make, model, year_from SMALLINT nullable, year_to SMALLINT nullable,
          trim nullable, front_tire_size VARCHAR(30) nullable,
          rear_tire_size VARCHAR(30) nullable, active BOOLEAN DEFAULT true,
          created_at, updated_at
          Indexes: make, (make, model), active

### 2.4 Order Tables
- [ ] 2.4.1  Create Alembic revision: `create_orders_table`
          Columns: id, order_number VARCHAR(50) UNIQUE, user_id nullable,
          guest_email nullable, guest_phone nullable,
          subtotal DECIMAL(10,3), discount_amount DECIMAL(10,3) DEFAULT 0,
          coupon_code nullable, shipping_amount DECIMAL(10,3) DEFAULT 0,
          tax_amount DECIMAL(10,3) DEFAULT 0, total DECIMAL(10,3),
          currency CHAR(3) DEFAULT AED,
          status ENUM(pending/confirmed/processing/shipped/delivered/cancelled/refunded),
          payment_status ENUM(pending/paid/failed/refunded/partially_refunded),
          payment_method nullable, payment_ref nullable,
          delivery_type ENUM(delivery/pickup) DEFAULT delivery,
          delivery_date DATE nullable, time_slot nullable,
          pickup_store_id nullable, billing_address_json JSON,
          shipping_address_json JSON nullable, quick_payment_link TEXT nullable,
          quick_payment_response JSON nullable, salesperson_id nullable,
          notes TEXT nullable, created_at, updated_at
          Indexes: order_number(unique), user_id, status, payment_status, created_at

- [ ] 2.4.2  Create Alembic revision: `create_order_items_table`
          Columns: id, order_id, product_id nullable, sku, name_en, name_ar nullable,
          image nullable, price DECIMAL(10,3), qty INT, subtotal DECIMAL(10,3),
          tire_size_label nullable, created_at, updated_at
          Indexes: order_id, product_id

- [ ] 2.4.3  Create Alembic revision: `create_order_status_history_table`
          Columns: id, order_id, status, comment TEXT nullable,
          is_customer_visible BOOLEAN DEFAULT false, created_by nullable, created_at
          Indexes: order_id

### 2.5 Cart Tables
- [ ] 2.5.1  Create Alembic revision: `create_carts_table`
          Columns: id, session_id VARCHAR(100) nullable, user_id nullable,
          coupon_code nullable, discount_amount DECIMAL(10,3) DEFAULT 0,
          expires_at TIMESTAMP nullable, created_at, updated_at
          Indexes: session_id, user_id, expires_at

- [ ] 2.5.2  Create Alembic revision: `create_cart_items_table`
          Columns: id, cart_id, product_id, qty INT, price_snapshot DECIMAL(10,3),
          created_at, updated_at
          Indexes: cart_id, (cart_id, product_id) unique composite

### 2.6 Payment Tables
- [ ] 2.6.1  Create Alembic revision: `create_payments_table`
          Columns: id, order_id, gateway ENUM(tamara/tabby/stripe/totalpay/paytabs/cod),
          gateway_ref nullable, gateway_checkout_id nullable,
          amount DECIMAL(10,3), currency CHAR(3) DEFAULT AED,
          status ENUM(pending/paid/failed/refunded/partially_refunded),
          payload_json JSON nullable, created_at, updated_at
          Indexes: order_id, gateway_ref, status

- [ ] 2.6.2  Create Alembic revision: `create_payment_webhooks_table`
          Columns: id, gateway, event_type, payload_json JSON, processed_at nullable,
          error TEXT nullable, created_at
          Indexes: gateway, processed_at

### 2.7 Enquiries Table (Unified)
- [x] 2.7.1  Create Alembic revision: `create_enquiries_table` (`hdweb_enquiry`)
          Columns: id,
          form_type ENUM(contact/general/service_booking/callback/quote_request/insurance),
          -- Common
          name VARCHAR(200) nullable, email VARCHAR(200) nullable,
          phone VARCHAR(30) nullable, message TEXT nullable,
          status ENUM(new/in_progress/resolved/closed) DEFAULT new,
          source_page VARCHAR(500) nullable, locale CHAR(2) DEFAULT en,
          -- Service booking specific
          service_type VARCHAR(100) nullable, vehicle_make VARCHAR(100) nullable,
          vehicle_model VARCHAR(100) nullable, vehicle_year SMALLINT nullable,
          preferred_date DATE nullable, time_slot VARCHAR(50) nullable,
          store_id INT UNSIGNED nullable,
          -- Callback specific
          preferred_time VARCHAR(100) nullable,
          -- Quote request specific
          tire_size VARCHAR(30) nullable, qty TINYINT nullable,
          vehicle_type_req VARCHAR(50) nullable,
          -- Admin
          assigned_to INT UNSIGNED nullable,
          replied_at TIMESTAMP nullable, reply_notes TEXT nullable,
          created_at, updated_at
          Indexes: form_type, status, created_at

### 2.8 Content Tables
- [ ] 2.8.1  Create Alembic revision: `create_stores_table`
          Columns: id, name_en, name_ar, address_en, address_ar, city,
          emirate, lat DECIMAL(10,7) nullable, lng DECIMAL(10,7) nullable,
          phone nullable, email nullable, hours_json JSON nullable,
          services_json JSON nullable, is_active BOOLEAN DEFAULT true,
          sort_order INT DEFAULT 0, created_at, updated_at
          Indexes: is_active, emirate

- [ ] 2.8.2  Create Alembic revision: `create_banners_table`
          Columns: id, title, image_desktop, image_mobile nullable, link nullable,
          alt_text nullable, position VARCHAR(50) DEFAULT homepage_hero,
          sort_order INT DEFAULT 0, starts_at TIMESTAMP nullable,
          expires_at TIMESTAMP nullable, is_active BOOLEAN DEFAULT true,
          created_at, updated_at
          Indexes: position, is_active, (starts_at, expires_at)

- [ ] 2.8.3  Create Alembic revision: `create_special_offers_table`
          Columns: id, title_en, title_ar nullable, description_en TEXT nullable,
          description_ar TEXT nullable, image nullable, badge_text nullable,
          link_url nullable, discount_percent DECIMAL(5,2) nullable,
          starts_at TIMESTAMP nullable, expires_at TIMESTAMP nullable,
          is_active BOOLEAN DEFAULT true, sort_order INT DEFAULT 0,
          created_at, updated_at
          Indexes: is_active, (starts_at, expires_at)

- [x] 2.8.4  Create Alembic revision: `create_blog_categories_table`
          Columns: id, name_en, name_ar nullable, slug, sort_order INT DEFAULT 0,
          created_at, updated_at
          Indexes: slug(unique)

- [x] 2.8.5  Create Alembic revision: `create_blogs_table` (`hdweb_blogs`)
          Columns: id, title_en, title_ar nullable, slug UNIQUE, content_en LONGTEXT,
          content_ar LONGTEXT nullable, excerpt_en TEXT nullable,
          excerpt_ar TEXT nullable, image nullable, blog_category_id nullable,
          author_id nullable, status ENUM(draft/published/archived) DEFAULT draft,
          published_at TIMESTAMP nullable, meta_title_en nullable,
          meta_title_ar nullable, meta_desc_en TEXT nullable,
          meta_desc_ar TEXT nullable, created_at, updated_at, deleted_at
          Indexes: slug(unique), status, published_at, blog_category_id

- [ ] 2.8.6  Create Alembic revision: `create_faqs_table`
          Columns: id, question_en TEXT, question_ar TEXT nullable,
          answer_en TEXT, answer_ar TEXT nullable, category_tag VARCHAR(100) nullable,
          sort_order INT DEFAULT 0, is_active BOOLEAN DEFAULT true,
          created_at, updated_at
          Indexes: category_tag, is_active, sort_order

### 2.9 Promotions Tables
- [ ] 2.9.1  Create Alembic revision: `create_coupons_table`
          Columns: id, code VARCHAR(50) UNIQUE, type ENUM(percent/fixed/free_shipping),
          value DECIMAL(10,3), min_order_amount DECIMAL(10,3) DEFAULT 0,
          max_discount DECIMAL(10,3) nullable, uses_total INT nullable,
          uses_per_customer INT DEFAULT 1, used_count INT DEFAULT 0,
          starts_at TIMESTAMP nullable, expires_at TIMESTAMP nullable,
          is_active BOOLEAN DEFAULT true, created_at, updated_at
          Indexes: code(unique), is_active

- [ ] 2.9.2  Create Alembic revision: `create_coupon_uses_table`
          Columns: id, coupon_id, user_id nullable, order_id, discount_applied DECIMAL(10,3),
          used_at TIMESTAMP
          Indexes: coupon_id, user_id, order_id

### 2.10 Loyalty Tables
- [ ] 2.10.1 Create Alembic revision: `create_reward_points_table`
           Columns: id, user_id, points INT, type ENUM(earn/redeem/expire/adjust),
           order_id nullable, description nullable, created_at
           Indexes: user_id, type, created_at

- [ ] 2.10.2 Create Alembic revision: `create_reward_point_rules_table`
           Columns: id, action VARCHAR(100), points_value INT, description nullable,
           is_active BOOLEAN DEFAULT true, created_at, updated_at

### 2.11 Purchase Order Tables
- [ ] 2.11.1 Create Alembic revision: `create_vendors_table`
           Columns: id, name, email nullable, phone nullable, contact_person nullable,
           address TEXT nullable, notes TEXT nullable, is_active BOOLEAN DEFAULT true,
           created_at, updated_at

- [ ] 2.11.2 Create Alembic revision: `create_purchase_orders_table`
           Columns: id, vendor_id, po_number VARCHAR(50) UNIQUE, subtotal DECIMAL(10,3),
           tax DECIMAL(10,3) DEFAULT 0, total DECIMAL(10,3),
           status ENUM(draft/sent/confirmed/received/cancelled) DEFAULT draft,
           notes TEXT nullable, ordered_at DATE nullable, created_at, updated_at
           Indexes: vendor_id, status, po_number(unique)

- [ ] 2.11.3 Create Alembic revision: `create_purchase_order_items_table`
           Columns: id, po_id, product_id nullable, sku, name, qty INT,
           unit_price DECIMAL(10,3), subtotal DECIMAL(10,3), created_at, updated_at
           Indexes: po_id

- [ ] 2.11.4 Create Alembic revision: `create_salespersons_table`
           Columns: id, name, email nullable, phone nullable,
           commission_rate DECIMAL(5,2) DEFAULT 0, is_active BOOLEAN DEFAULT true,
           created_at, updated_at

### 2.12 Marketing Tables
- [ ] 2.12.1 Create Alembic revision: `create_abandoned_carts_table`
           Columns: id, user_id nullable, email nullable, phone nullable,
           cart_snapshot_json JSON, total_value DECIMAL(10,3) DEFAULT 0,
           notified_count TINYINT DEFAULT 0, last_notified_at TIMESTAMP nullable,
           recovered_at TIMESTAMP nullable, created_at, updated_at
           Indexes: email, user_id, last_notified_at, recovered_at

- [ ] 2.12.2 Create Alembic revision: `create_newsletter_subscribers_table`
           Columns: id, email UNIQUE, locale CHAR(2) DEFAULT en,
           status ENUM(subscribed/unsubscribed) DEFAULT subscribed,
           subscribed_at TIMESTAMP, created_at, updated_at
           Indexes: email(unique), status

### 2.13 Admin Tables
- [x] 2.13.1 Create Alembic revision: `create_admin_users_table` (`userTbl`)
           Columns: id, name, email UNIQUE, password_hash, role ENUM(super_admin/manager/support),
           is_active BOOLEAN DEFAULT true, last_login_at TIMESTAMP nullable,
           created_at, updated_at
           (no `remember_token` — Flask-Login's "remember me" is a signed cookie, not a stored value)
           Indexes: email(unique), role

- [ ] 2.13.2 Create Alembic revision: `create_activity_log_table`
           Columns: id, admin_user_id nullable, action VARCHAR(100),
           model_type VARCHAR(200) nullable, model_id nullable,
           old_values_json JSON nullable, new_values_json JSON nullable,
           ip VARCHAR(45) nullable, created_at
           Indexes: admin_user_id, model_type+model_id composite, created_at

### 2.14 Additional Core Tables
- [x] 2.14.1 `hdweb_pages` (Static Pages Studio CMS table)
- [x] 2.14.2 `hdweb_page_sections` (Dynamic Layout Component Builder table)
- [x] 2.14.3 `fileTbl` (Registered Python scrapers and URL JSON store)
- [x] 2.14.4 `password_reset_tbl` (Password reset token storage)

---

## PHASE 3 — Models (SQLAlchemy) & Mixins

> Traits become mixins (plain Python classes mixed into a SQLAlchemy declarative model).
> `HasSlug` → `SlugMixin` (uses `python-slugify`, generates on `before_insert` via an event listener)
> `SoftDeletes` → `SoftDeleteMixin` (`deleted_at` column + a global `with_loader_criteria` filter)
> `HasTranslations` → not needed; translated fields are already flat `_en`/`_ar` columns per 2.x schema
> `HasMedia` (Spatie) → `MediaMixin` (relationship to a lightweight `Media` table + `MediaService` helpers)
> `Searchable` (Scout) → `SearchableMixin` (`to_search_document()` method + `after_insert`/`after_update`/
>   `after_delete` SQLAlchemy events that dispatch a Celery reindex task, see 4.4/9.2)

### 3.1 Catalog Models
- [ ] 3.1.1  Create `app/models/category.py::Category`
           Mixins: SlugMixin, SoftDeleteMixin, TimestampMixin
           Relations: `parent` (self-referential FK), `children` (relationship), `products`
           Casts: `status` as `db.Enum('active', 'inactive')`
           Query helpers (classmethods or a custom `Query` subclass): `.active()`, `.roots()`

- [ ] 3.1.2  Create `app/models/brand.py::Brand`
           Mixins: SlugMixin, MediaMixin
           Relations: `products`
           Query helpers: `.active()`, `.featured()`
           Search: `SearchableMixin` → indexed into ES (`brand_index.py`)

- [ ] 3.1.3  Create `app/models/product.py::Product`
           Mixins: SlugMixin, SoftDeleteMixin, MediaMixin, SearchableMixin
           Relations: `brand`, `category`
           Casts: `gallery_json` (JSON), `stock_status`/`tire_type`/`vehicle_type`/`status`/`visibility`
                  as `db.Enum(...)`, `price`/`sale_price` as `db.Numeric(10,3)`
           Hybrid properties (SQLAlchemy `@hybrid_property`, replacing Eloquent Appends):
                  `current_price` (sale_price if set else price), `is_on_sale`, `formatted_tire_size`
           Query helpers: `.active()`, `.visible()`, `.in_stock()`, `.featured()`, `.by_brand()`,
                  `.by_category()`, `.by_tire_size(w, h, r)`, `.by_vehicle_type()`
           Event listener: `before_insert`/`before_update` auto-generates `tire_size_label` from
                  width/height/rim (SQLAlchemy `@event.listens_for(Product, 'before_insert')`)
           Search: `to_search_document()` returns all flat fields for ES indexing

### 3.2 User Models
- [ ] 3.2.1  Create `app/models/user.py::User` (implements Flask-Login's `UserMixin`)
           Columns: phone, locale, points_balance, social_provider, social_id, avatar, status
           Relations: `addresses`, `orders`, `reward_points`, `cart`
           Casts: `status` as `db.Enum(...)`, `points_balance` as `db.Integer`
           Methods: `get_default_address()`, `get_total_points()`
           Password: `password_hash` column, `set_password()`/`check_password()` using
                  `werkzeug.security.generate_password_hash` / `check_password_hash`

- [ ] 3.2.2  Create `app/models/address.py::Address`
           Relations: `user`
           Query helpers: `.default()`
           Methods: `to_order_dict()` — formats for order JSON storage

### 3.3 Vehicle Model
- [ ] 3.3.1  Create `app/models/vehicle.py::Vehicle`
           Relations: none (lookup table)
           Query helpers: `.active()`, `.by_make(make)`
           Static/class methods: `get_makes()`, `get_models_by_make(make)` — cached in Redis
                  via `flask_caching`'s `@cache.memoize()`

### 3.4 Order Models
- [ ] 3.4.1  Create `app/models/order.py::Order`
           Relations: `user`, `items`, `status_history`, `payment`, `salesperson`
           Casts: `status`/`payment_status`/`delivery_type` as `db.Enum(...)`,
                  `billing_address_json`/`shipping_address_json`/`quick_payment_response` as `db.JSON`,
                  `total` as `db.Numeric(10,3)`
           Hybrid properties: `status_label_en`, `status_label_ar`, `formatted_total`
           Query helpers: `.by_status()`, `.by_payment_status()`, `.recent()`, `.for_customer()`
           Event listener: `before_insert` auto-generates `order_number` (format `TC-YYYYMMDD-XXXX`)

- [ ] 3.4.2  Create `app/models/order_item.py::OrderItem`
           Relations: `order`, `product`
           Casts: `price`/`subtotal` as `db.Numeric(10,3)`

- [ ] 3.4.3  Create `app/models/order_status_history.py::OrderStatusHistory`
           Relations: `order`, `created_by_admin`

### 3.5 Cart Models
- [ ] 3.5.1  Create `app/models/cart.py::Cart`
           Relations: `items`
           Casts: `discount_amount` as `db.Numeric(10,3)`
           Methods: `total()`, `subtotal()`, `item_count()`, `is_empty()`

- [ ] 3.5.2  Create `app/models/cart_item.py::CartItem`
           Relations: `cart`, `product`
           Casts: `price_snapshot` as `db.Numeric(10,3)`
           Hybrid property: `line_total`

### 3.6 Payment Models
- [ ] 3.6.1  Create `app/models/payment.py::Payment`
           Relations: `order`
           Casts: `status` as `db.Enum(...)`, `payload_json` as `db.JSON`, `amount` as `db.Numeric(10,3)`

- [ ] 3.6.2  Create `app/models/payment_webhook.py::PaymentWebhook`
           Casts: `payload_json` as `db.JSON`
           Query helpers: `.unprocessed()`

### 3.7 Other Models
- [ ] 3.7.1  Create `app/models/enquiry.py::Enquiry`
           Casts: `form_type`/`status` as `db.Enum(...)`
           Query helpers: `.by_form_type()`, `.by_status()`, `.unassigned()`

- [ ] 3.7.2  Create `app/models/store.py::Store`
           Casts: `hours_json`/`services_json` as `db.JSON`
           Query helpers: `.active()`, `.by_emirate()`

- [ ] 3.7.3  Create `app/models/banner.py::Banner`
           Query helpers: `.active()`, `.by_position()`, `.currently_active()` (checks dates)

- [ ] 3.7.4  Create `app/models/special_offer.py::SpecialOffer`
           Query helpers: `.active()`, `.currently_active()`

- [ ] 3.7.5  Create `app/models/blog.py::Blog`
           Mixins: SlugMixin, SoftDeleteMixin, SearchableMixin
           Relations: `category`, `author`
           Query helpers: `.published()`, `.by_category()`
           Search: indexed into ES (`blog_index.py`)

- [ ] 3.7.6  Create `app/models/blog_category.py::BlogCategory`

- [ ] 3.7.7  Create `app/models/faq.py::Faq`
           Mixins: SearchableMixin
           Query helpers: `.active()`, `.by_category()`
           Search: indexed into ES (`faq_index.py`)

- [ ] 3.7.8  Create `app/models/coupon.py::Coupon`
           Methods: `is_valid()`, `apply_to_order(total)`, `is_expired()`, `has_uses_remaining()`
           Query helpers: `.active()`, `.by_code()`

- [ ] 3.7.9  Create `app/models/coupon_use.py::CouponUse`

- [ ] 3.7.10 Create `app/models/reward_point.py::RewardPoint`
           Relations: `user`, `order`
           Query helpers: `.by_user()`, `.earned()`, `.redeemed()`

- [ ] 3.7.11 Create `app/models/reward_point_rule.py::RewardPointRule`

- [ ] 3.7.12 Create `app/models/abandoned_cart.py::AbandonedCart`
           Query helpers: `.not_yet_notified()`, `.not_recovered()`, `.notified_less_than(count)`

- [ ] 3.7.13 Create `app/models/newsletter_subscriber.py::NewsletterSubscriber`

- [ ] 3.7.14 Create `app/models/admin_user.py::AdminUser` (implements Flask-Login's `UserMixin`)
           Casts: `role` as `db.Enum(...)`
           > **Correction:** Flask-Login supports only one `LoginManager`/`user_loader` per app —
           > "a separate login_manager instance scoped to the admin blueprint" (as an earlier draft
           > of this plan said) is not actually constructible; `current_user` always resolves via
           > the single `app.login_manager`. The real Python analogue of Laravel's separate
           > `admin` guard is: **one** `LoginManager` with **one** `user_loader` that branches on
           > `request.blueprint` (or path prefix `/admin`) to query `AdminUser` vs `User`, backed
           > by a custom `SessionInterface` that issues a distinct session cookie for `/admin/*`
           > requests (see 1.2.17). Two independent cookies → two independent `_user_id` values →
           > an admin and a customer can be logged in simultaneously in the same browser, same as
           > two separate Laravel guards.

- [ ] 3.7.15 Create `app/models/activity_log.py::ActivityLog`
           Relations: `admin_user`
           Static helper: `ActivityLog.record(action, model, old, new)`

- [ ] 3.7.16 Create `app/models/setting.py::Setting`
           Static helpers: `Setting.get(key, default)`, `Setting.set(key, value)` — cached via
                  `flask_caching`
           Query helpers: `.by_group()`

- [ ] 3.7.17 Create `app/models/vendor.py::Vendor`
           Relations: `purchase_orders`

- [ ] 3.7.18 Create `app/models/purchase_order.py::PurchaseOrder`
           Relations: `vendor`, `items`
           Event listener: `before_insert` auto-generates `po_number`

- [ ] 3.7.19 Create `app/models/purchase_order_item.py::PurchaseOrderItem`

- [ ] 3.7.20 Create `app/models/salesperson.py::Salesperson`
           Relations: `orders`

- [ ] 3.7.21 Create `app/mixins/media_mixin.py::MediaMixin` (companion to 3.7.2 in the Laravel
           plan's Spatie Media Library usage) — provides `add_media(file, collection)`,
           `get_media_url(collection, conversion)` backed by a lightweight `media` table
           (id, model_type, model_id, collection, disk_path, conversions_json)

---

## PHASE 4 — Services Layer
> Plain Python service classes/modules. No IoC container — instantiate directly or pass
> dependencies (db session, redis client, es client) through the constructor / module-level
> singletons from `app/extensions.py`. Where Laravel resolved a service from the container,
> Flask code typically does `from app.services.cart_service import CartService` and
> `CartService(db.session)` (or a module-level function if no state is needed).

### 4.1 Cart Service
- [ ] 4.1.1  Create `app/services/cart_service.py::CartService`
           Method: `get_or_create(session_id, user_id)` — finds cart by session_id or user_id, creates if missing
           Method: `add_item(cart, product_id, qty)` — adds or increments, price snapshot
           Method: `update_item(cart, item_id, qty)` — updates qty
           Method: `remove_item(cart, item_id)` — deletes item
           Method: `apply_coupon(cart, code)` — validates and applies coupon
           Method: `remove_coupon(cart)` — removes coupon from cart
           Method: `merge_guest_cart(session_id, user_id)` — merge session cart into user cart on login
           Method: `clear(cart)` — empties cart
           Method: `totals(cart)` — returns subtotal, discount, shipping, total
           Method: `to_order_data(cart)` — formats cart for order creation

- [ ] 4.1.2  Create `app/services/shipping_service.py::ShippingService`
           Method: `calculate(cart, address)` — returns shipping cost
           Method: `get_available_methods(emirate)` — delivery vs pickup options
           Method: `get_delivery_slots(date)` — available time slots

### 4.2 Order Service
- [ ] 4.2.1  Create `app/services/order_service.py::OrderService`
           Method: `create_from_cart(cart, checkout_data)` — builds Order + OrderItems
           Method: `update_status(order, status, comment)` — updates + logs history
           Method: `cancel(order)` — cancels + restores stock
           Method: `generate_order_number()` — format: TC-YYYYMMDD-XXXX
           Method: `decrement_stock(order_items)` — atomic stock decrement (`SELECT ... FOR UPDATE`
                  via SQLAlchemy `with_for_update()`)
           Method: `send_confirmation_email(order)` — queues Celery task
           Method: `generate_quick_payment_link(order, gateway)` — delegates to PaymentServiceFactory

### 4.3 Payment Services
- [ ] 4.3.1  Create `app/services/payment/base.py::PaymentGatewayBase` (abstract base class /
           `Protocol`, replacing the `PaymentGatewayInterface` contract)
           Methods: `create_checkout(order)`, `handle_webhook(request)`,
           `refund(payment, amount)`, `generate_quick_link(order)`, `gateway_name`

- [ ] 4.3.2  Create `app/services/payment/tamara_service.py::TamaraService(PaymentGatewayBase)`
           create_checkout(): build Tamara checkout payload, call API (via `requests`/`httpx`),
                  return redirect URL
           handle_webhook(): verify signature, update payment + order status
           refund(): call Tamara refund API
           generate_quick_link(): create checkout for existing order (admin use)

- [ ] 4.3.3  Create `app/services/payment/tabby_service.py::TabbyService(PaymentGatewayBase)`
           Same structure as Tamara with Tabby API endpoints

- [ ] 4.3.4  Create `app/services/payment/stripe_service.py::StripeService(PaymentGatewayBase)`
           create_checkout(): Stripe Checkout Session via the `stripe` Python SDK, with line items
           handle_webhook(): verify Stripe signature (`stripe.Webhook.construct_event`), handle
                  `checkout.session.completed`
           refund(): Stripe refund API call
           generate_quick_link(): new Checkout Session for existing order

- [ ] 4.3.5  Create `app/services/payment/totalpay_service.py::TotalPayService(PaymentGatewayBase)`

- [ ] 4.3.6  Create `app/services/payment/paytabs_service.py::PayTabsService(PaymentGatewayBase)`

- [ ] 4.3.7  Create `app/services/payment/factory.py::PaymentServiceFactory`
           `make(gateway)`: returns correct service instance
           Registered as a module-level singleton dict (`GATEWAYS = {...}`) or built fresh
           per request — no container binding needed since these are stateless

### 4.4 Search & Tire Finder Services
- [ ] 4.4.1  Create `app/services/search_service.py::SearchService`
           Method: `search_products(query, filters, page)` — ES search with filters (uses
                  `es_client.search(index=ProductIndex().index_name(), ...)`)
           Method: `autocomplete(query)` — fast partial match, returns top 8 results
           Method: `get_filter_aggregations(filters)` — ES aggregations for faceted nav
           Method: `search_all(query)` — cross-index: products + blogs + brands + faqs
           (This is the direct replacement for Laravel Scout + elastic-scout-driver — there is
           no intermediate "driver" package in Python, this service IS the driver)

- [ ] 4.4.2  Create `app/services/tyre_finder_service.py::TyreFinderService`
           Method: `get_makes()` — fetch from vehicles table (cached 24h via `flask_caching`)
           Method: `get_models(make)` — from vehicles table (cached)
           Method: `get_years(make, model)` — from vehicles table
           Method: `get_tire_size_for_vehicle(make, model, year)` — returns front+rear sizes
           Method: `sync_from_api()` — pull from wheel-api.klever.ae (via `requests`), upsert
                  vehicles table
           Method: `get_available_widths()` — DISTINCT tire_width from products (cached)
           Method: `get_available_heights_for_width(width)` — filtered (cached)
           Method: `get_available_rims_for_width_height(w, h)` — filtered (cached)

### 4.5 Other Services
- [ ] 4.5.1  Create `app/services/coupon_service.py::CouponService`
           Method: `validate(code, user_id, cart_total)` — returns coupon or raises
           Method: `apply(code, cart)` — applies discount to cart
           Method: `record_use(coupon, order)` — logs use + increments used_count

- [ ] 4.5.2  Create `app/services/reward_points_service.py::RewardPointsService`
           Method: `earn(user, order)` — calculate + add points for order
           Method: `redeem(user, points, order)` — deduct + apply discount
           Method: `get_balance(user)` — sum of all point transactions
           Method: `get_history(user)` — paginated point log

- [ ] 4.5.3  Create `app/services/email_service.py::EmailService`
           Method: `send_order_confirmation(order)`
           Method: `send_order_status_update(order, status)`
           Method: `send_abandoned_cart_email(abandoned_cart)`
           Method: `send_enquiry_confirmation(enquiry)`
           Method: `send_admin_new_enquiry(enquiry)`
           Method: `send_quick_payment_link(order, link)`
           All methods dispatch Celery tasks (`app/tasks/mail_tasks.py`) to the `mail` queue

- [ ] 4.5.4  Create `app/services/abandoned_cart_service.py::AbandonedCartService`
           Method: `snapshot()` — saves current active carts to abandoned_carts
           Method: `get_eligible()` — carts abandoned 1h+ ago, not yet notified 3x
           Method: `mark_notified(abandoned_cart)`
           Method: `mark_recovered(abandoned_cart)`

- [ ] 4.5.5  Create `app/services/media_service.py::MediaService` (backs `MediaMixin` from 3.7.21)
           Method: `store(file, model, collection)` — saves original + generates conversions
                  via Pillow (webp-thumb/card/full/hero, see 10.2.6)
           Method: `delete(media)`
           Method: `url_for(media, conversion)`

- [ ] 4.5.6  Create `app/services/sitemap_service.py::SitemapService` (replaces Spatie Sitemap)
           Method: `generate()` — builds sitemap XML for all routes (products, categories,
                  brands, blogs, static pages) using `xml.etree.ElementTree`, writes to
                  `app/static/sitemap.xml`

---

## PHASE 5 — Middleware & Auth

### 5.1 Middleware (Flask `before_request` hooks / decorators, replacing Laravel middleware classes)
- [ ] 5.1.1  Create `app/blueprints/admin/hooks.py::set_locale()`
           Scope: admin panel only — reads `?locale=` query param or session locale for admin UI
                  language, store in Flask `g.locale`; registered via `admin_bp.before_request`
           A separate `app/blueprints/site/hooks.py::set_locale()` does the equivalent for the
           customer `site` blueprint, deriving `g.locale` from the `/en/...`|`/ar/...` URL prefix
           instead of a query param (see 8.1.1/8.1.3)

- [ ] 5.1.2  ~~CartSession middleware~~ — NOT NEEDED
           Both the `site` blueprint's pages and the former Next.js frontend manage cart state via
           API calls (identified by an `X-Cart-Token` header, generated client-side in `site.js`);
           no server-side session cart middleware required, same as the Laravel version's decision

- [ ] 5.1.3  Create `app/blueprints/admin/hooks.py::require_admin_auth()` decorator
           Logic: checks `flask_login.current_user` is authenticated via the admin user-loader;
                  redirects to `admin.login` if not — applied via `@admin_bp.before_request` or
                  a `@login_required` equivalent scoped to the admin Flask-Login instance

- [ ] 5.1.4  Create `app/hooks/force_https.py::force_https()`
           Scope: production only — redirect HTTP → HTTPS (required for secure cookies / JWT
                  transport); registered as an `app.before_request` hook gated on
                  `app.config['ENV'] == 'production'`

### 5.2 Admin Auth Configuration
- [ ] 5.2.1  Configure a second `LoginManager` instance (or a single `LoginManager` with a
           custom `user_loader` that discriminates by session key) scoped to `AdminUser`,
           separate from the customer-facing `User` — the Python equivalent of Laravel's
           `admin` guard backed by the `admin_users` table
- [ ] 5.2.2  Register the admin user-loader: `@admin_login_manager.user_loader` loads
           `AdminUser.query.get(user_id)`

- [ ] 5.2.3  Configure a third `LoginManager` instance scoped to the customer-facing `User` model,
           used by the `site` blueprint (Phase 8) to gate `/account/*` pages with ordinary cookie
           sessions — separate from both the admin guard (5.2.1) and the stateless JWT guard (5.3)
           used by the JSON API; register its user-loader: `User.query.get(user_id)`

### 5.3 API Auth — Flask-JWT-Extended (replaces Laravel Sanctum)
- [ ] 5.3.1  Install Flask-JWT-Extended (done in 1.2.9)
- [ ] 5.3.2  Configure `app/config.py`: `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_EXPIRES` (24h,
           env-configurable, mirrors Sanctum's 1440-minute default), `JWT_REFRESH_TOKEN_EXPIRES`
- [ ] 5.3.3  Decide token storage: JWTs are issued at login and set as an httpOnly cookie by Flask
           itself (5.3.5) — since the `site` blueprint and the API are the same origin now, there
           is no separate client app to hand a bearer token to, so no client-side token storage or
           translation layer is needed (no `personal_access_tokens` table — JWTs are self-contained;
           if server-side revocation is required, add a small `token_blocklist` table and a
           `@jwt.token_in_blocklist_loader` callback — optional, add only if revocation-on-logout
           is a hard requirement)
- [ ] 5.3.4  Add `set_password`/`check_password` helpers to `app/models/user.py::User` (done in 3.2.1)
- [ ] 5.3.5  Configure `app/config.py`:
           `JWT_TOKEN_LOCATION = ['headers', 'cookies']`, `JWT_HEADER_TYPE = 'Bearer'`
           `JWT_COOKIE_SECURE = True` (prod), `JWT_COOKIE_CSRF_PROTECT = True` (double-submit CSRF
           token read by `site.js`'s `apiFetch()` helper, see 8.1.5/8.2.3)
           `JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)` (env-configurable)
           Headers stay supported for any future non-browser client (mobile app, etc.)
- [ ] 5.3.6  Configure Flask-CORS in `create_app()`:
           `origins` → env `CORS_ALLOWED_ORIGINS`, only needed if a future separate client (mobile
           app, third-party integration) calls the API cross-origin — the `site` blueprint and
           admin panel are same-origin and need no CORS entry
           `methods` → GET, POST, PUT, PATCH, DELETE, OPTIONS
           `allow_headers` → Content-Type, Authorization, X-Requested-With, Accept, X-Cart-Token,
                  X-CSRF-TOKEN
           `supports_credentials` → True (required now that the cookie-based JWT flow, 5.3.3, is default)
- [ ] 5.3.7  Register `jwt.init_app(app)` in `create_app()`; protect API blueprint routes with
           the `@jwt_required()` decorator (replaces `EnsureFrontendRequestsAreStateful` middleware)

### 5.4 Social Auth (Google/Facebook, used by the `site` blueprint's login page)
- [ ] 5.4.1  Configure Authlib OAuth clients: Google, Facebook in `app/config.py`
           (`GOOGLE_CLIENT_ID`/`SECRET`, `FACEBOOK_CLIENT_ID`/`SECRET`)
- [ ] 5.4.2  Add social provider credentials to `.env`
           Note: OAuth redirect goes to Flask (`/api/v1/auth/social/<provider>/callback`), which
           creates/finds the user, issues a JWT, sets the httpOnly cookie (5.3.3), calls
           `login_user()` against the site `LoginManager` (5.2.3), then redirects into the `site`
           blueprint (`site.social_callback`, 8.8.4) — a single-app redirect, no cross-app token
           hand-off the way the Next.js version needed; mirrors the Laravel version's
           Socialite → Sanctum token flow, simplified further since everything is one app now

---

## PERFORMANCE & QUALITY STANDARDS
> Target: PageSpeed Insights 100/100 mobile + desktop. W3C Nu Validator: 0 errors.
> Applies to: Jinja2 customer frontend (Phase 8) + Admin panel (Phase 6) — both are Flask
> Blueprints rendering Jinja2, so the same rule set now applies to both with only cosmetic
> differences (noted below).

### Site (Customer) Frontend Rules (Phase 8)
**PageSpeed 100 — Core Web Vitals**
- Use the shared `img()` Jinja macro (6.1.1/10.2.6) for ALL images → `<picture>`/`srcset` WebP via
  `MediaService` conversions, explicit `width`/`height`, no CLS — the direct equivalent of `next/image`
- Hero/LCP image: render a `<link rel="preload" as="image">` in the `lcp_image_url` block
  (10.2.10) instead of `priority` — the browser preloads it before CSS/JS parse
- Pages render fully server-side on request (no client-side data-fetching waterfall) → SSR-fast LCP
  by construction, no RSC/Suspense equivalent needed
- Self-host web fonts with `font-display: swap` in `site.css` (10.2.6-adjacent) → zero CLS,
  the same outcome `next/font` gave, achieved with a plain `@font-face` rule
- Use the shared `skeleton.html` macro (8.3.5) for the small set of client-only widgets (cart
  drawer count, autocomplete dropdown) that hydrate after Alpine.js loads
- Debounce search: 300ms minimum on any input that triggers an API call (8.2.4)
- Load any third-party script with `defer` or `async`, never a blocking `<script>` in `<head>`
- i18n: Flask-Babel + `/en/...` / `/ar/...` URL prefixes (8.1.1/8.1.3) — no client-side i18n library

**W3C Compliance (Site)**
- `<html lang="{{ g.locale }}" dir="{{ 'rtl' if g.locale == 'ar' else 'ltr' }}">` in
  `site/layouts/base.html` (8.1.6) — dynamic per locale
- `<meta charset="utf-8">` and `<meta name="viewport">` in the base layout `<head>`
- All images rendered via the `img()` macro have `alt` — no exceptions
- All `<input>` have associated `<label>` (`for` + `id`)
- All `<button>` have explicit `type` attribute
- Heading hierarchy: one `<h1>` per page, never skip levels
- ARIA landmarks on all structural elements
- Skip navigation link as first element in `site/layouts/base.html`
- `x-*` Alpine.js attributes will appear as W3C warnings — acceptable (same allowance as 6.x/Admin)

### Admin Panel Rules (Phase 6)
- `x-*` Alpine.js attributes will appear as W3C warnings — acceptable
- All `<img>` in Jinja2 templates must have `alt`, `width`, `height`
- All form inputs must have associated `<label>`
- All `<button>` must have explicit `type` attribute
- Heading hierarchy must be respected in all admin views

---

## PHASE 6 — TailAdmin-Themed Admin Panel (Flask Blueprint + Jinja2 + Alpine.js)

> **Theme**: TailAdmin (`tailadmin-laravel-main` HTML/Tailwind/JS assets) — ported to Jinja2
> includes/macros in place of Blade components (`<x-admin::...>` becomes `{% include "admin/... %}`
> or a Jinja2 macro call). ApexCharts/Flatpickr/jsvectormap JS is copied over unchanged (it was
> always plain JS, never PHP-templated).
> **Stack**: Flask Blueprint (`admin_bp`) view functions · Jinja2 views · Alpine.js · Tailwind CSS v4
>            ApexCharts · Flatpickr · FullCalendar
> **Routes**: All admin routes registered on `admin_bp`, mounted at `/admin` in `create_app()`
> **Auth**: Flask-Login session auth scoped to `AdminUser` (see 5.2) — NO JWT here, cookie session only
> **Layout**: Adapt TailAdmin layout partials (sidebar, app-header, backdrop) into
>            `app/templates/admin/layouts/base.html`

---

### 6.1 Admin Theme Integration

- [x] 6.1.1  Port TailAdmin HTML partials into project as Jinja2 includes:
            `tailadmin-laravel-main/resources/views/components/*` → `app/templates/admin/partials/`
            Includes: layouts (base, header, sidebar, sidebar-widget, backdrop, fullscreen-layout),
            ecommerce (ecommerce-metrics, monthly-sale, monthly-target, recent-orders, statistics-chart,
            customer-demographic),
            form (date-picker, default-inputs, dropzone, file-input, input-group, checkbox, radio,
            select-inputs, text-area, toggle-switch, multiple-select),
            tables (basic-tables-one through five),
            ui (alert, avatar, badge, button, modal),
            common (page-breadcrumb, component-card, dropdown-menu, preloader, table-dropdown, theme-toggle),
            header (notification-dropdown, user-dropdown),
            profile (profile-card, personal-info-card, address-card)
            Each Blade component's `@props`/slot pattern becomes a Jinja2 macro with keyword
            arguments (`{% macro badge(text, color='gray') %}`) collected in `app/templates/admin/macros.html`

- [x] 6.1.2  Any TailAdmin PHP view-model classes (`app/View/Components/*`) become plain Python
            helper functions/dataclasses passed into `render_template()` context, or Jinja2
            custom filters registered via `app.jinja_env.filters[...]` — no component registration
            step is needed since Jinja2 macros are imported directly where used

- [x] 6.1.3  Port TailAdmin JS into project (unchanged, plain JS):
            `tailadmin-laravel-main/resources/js/components/*` → `app/static/src/admin/components/`
            (chart-1.js through chart-13.js, calendar-init.js, map.js)

- [x] 6.1.4  Port TailAdmin CSS into `app/static/src/admin.css`
            Adapt `tailadmin-laravel-main/resources/css/app.css` for the admin namespace

- [x] 6.1.5  Create `app/templates/admin/layouts/base.html`
            Adapted from TailAdmin `layouts/app.blade.php`
            Loads: `admin.css`, `admin.js` via the `vite_asset()` Jinja2 global (see 1.3.9)
            Includes: `{% include "admin/partials/sidebar.html" %}`, `.../header.html`, `.../backdrop.html`
            Block: `{% block content %}{% endblock %}` for page content

- [x] 6.1.6  Create `app/templates/admin/layouts/auth.html`
            Adapted from TailAdmin `fullscreen-layout.blade.php` — used for login page only

- [x] 6.1.7  Create `app/helpers/admin_menu.py::AdminMenuHelper`
            Plain Python module (list of dicts / small dataclasses) replacing `MenuHelper.php`
            Nav items for TyresCart: Dashboard, Products, Orders, Enquiries, Customers,
            Brands, Categories, Coupons, Banners, Special Offers, Blogs, FAQs, Stores,
            Purchase Orders, Reports, Settings, Admin Users

### 6.2 Admin Auth

- [x] 6.2.1  Create `app/blueprints/admin/auth.py`
            GET  `/admin/login` → show login form (`admin/auth/login.html`)
            POST `/admin/login` → validate credentials against `admin_users` table via
                                  `AdminUser.query.filter_by(email=...)` + `check_password_hash`,
                                  on success → `login_user(admin_user)` (admin Flask-Login instance)
                                  → redirect to `/admin`
            POST `/admin/logout` → `logout_user()` → redirect to `/admin/login`

- [x] 6.2.2  Create `app/templates/admin/auth/login.html`
            Extends `admin/layouts/auth.html`
            Adapts TailAdmin `pages/auth/signin.blade.php` with TyresCart branding
            Fields: email, password, remember me (WTForms `LoginForm`)
            POSTs to `/admin/login`

- [x] 6.2.3  Register admin blueprint in `app/blueprints/admin/__init__.py` mounted at `/admin`:
            ```python
            admin_bp = Blueprint('admin', __name__, url_prefix='/admin',
                                  template_folder='../../templates/admin')
            admin_bp.before_request(require_admin_auth_except_login)
            # sub-blueprints or route modules registered here: auth, dashboard, products, orders, ...
            ```

- [x] 6.2.4  Finalize `require_admin_auth()` from 5.1.3: redirect unauthenticated requests to
            `url_for('admin.login')`, excluding the login route itself from the check

### 6.3 Admin Dashboard

- [x] 6.3.1  Create `app/blueprints/admin/dashboard.py::dashboard()`
            GET `/admin` → queries via SQLAlchemy: today_sales, total_orders, pending_orders,
            new_enquiries, monthly_revenue[] (12 months, `func.sum`/`func.date_trunc` grouping),
            top_products[] (top 10 by revenue), low_stock_count (stock_qty < 5),
            recent_orders (last 10)
            Pass all to `render_template()`

- [x] 6.3.2  Create `app/templates/admin/dashboard.html`
            Extends `admin/layouts/base.html`
            Widgets row: ecommerce-metrics partial (today sales, orders, enquiries)
            Sales chart: monthly-sale partial with ApexCharts line chart (real monthly_revenue data,
                  passed as a JSON blob via `{{ monthly_revenue | tojson }}`)
            Monthly target: monthly-target partial with donut chart (top products)
            Recent orders table: recent-orders partial (last 10 orders)
            Stats chart: statistics-chart partial (revenue vs orders overlay)
            Low stock alert: badge count widget linking to products filtered by low stock

### 6.4 Products Admin

- [ ] 6.4.1  Create `app/blueprints/admin/products.py`
            `index()`  → paginated products (SQLAlchemy `.paginate()`), filter by
                  brand/category/status/type, search SKU/name (`ILIKE`/FULLTEXT), sort any
                  column, per_page 25/50/100
            `create_view()` → show create form
            `store()`  → validate (WTForms `ProductForm`) + create product + sync ES
                  (dispatch `app/tasks/index_tasks.py::index_product`) + log activity → redirect index
            `edit_view()`   → show edit form prefilled
            `update()` → validate + update + re-sync ES + log activity → redirect index
            `destroy()`→ soft delete (`deleted_at = now()`) + remove from ES + log activity → redirect index
            `bulk_action()` → POST bulk: status change or delete for `selected_ids[]`
            `export()` → stream CSV of filtered results (`Response(generate(), mimetype='text/csv')`)
            `import_csv()` → POST CSV file → dispatch `app/tasks/index_tasks.py::import_products` → flash message

- [ ] 6.4.2  Create `app/forms/admin/product_form.py::ProductForm` (WTForms)
            Validates all flat product fields (SKU unique via a custom `Unique` validator,
            price positive, etc.) — replaces `ProductRequest` Form Request

- [ ] 6.4.3  Create `app/templates/admin/products/index.html`
            Extends `admin/layouts/base.html` · includes `partials/common/page_breadcrumb.html`
            Filter bar: search input, brand select, category select, status select, type select,
                        per_page select, bulk action select — all Alpine.js reactive, submit on change
            Table: horizontally scrollable, all flat columns visible:
                   checkbox | SKU | Name | Brand | Category | Size | Type | Speed | Load | Vehicle |
                   Price | Sale Price | Stock | Stock Status | Run Flat | EV | Featured | Status | Actions
            Each row: badge macro for status/stock, edit + delete action buttons
            table-dropdown partial for per-row actions
            modal partial for delete confirmation (Alpine.js `x-data`)
            Pagination: Jinja2 macro wrapping SQLAlchemy's `Pagination` object, styled like TailAdmin
            Top bar: Export CSV button, Import CSV button → link to import page

- [ ] 6.4.4  Create `app/templates/admin/products/form.html` (shared by create + edit)
            Extends `admin/layouts/base.html`
            Section 1 — Basic Info:
              SKU (default-inputs partial),
              Name EN / Name AR (text inputs),
              Status (select-inputs partial),
              Visibility select
            Section 2 — Tire Specs:
              Width / Height / Rim (number inputs),
              Tire Type select, Speed Rating, Load Index, Pattern (text),
              Run Flat (toggle-switch partial),
              EV Rated toggle, OEM toggle, OEM Brand text
            Section 3 — EU Labels:
              Fuel Efficiency select (A–G), Wet Grip select (A–G), Noise dB number input
            Section 4 — Pricing:
              Price / Sale Price / Cost Price (decimal inputs),
              Pay Later Eligible toggle
            Section 5 — Inventory:
              Stock Qty, Stock Status select, Min/Max Order Qty
            Section 6 — Relations:
              Brand select (populated), Category select (populated), Vehicle Type select
            Section 7 — Media:
              Main image (dropzone partial, POSTs to `MediaService.store()` via an admin upload route),
              Gallery multi-upload dropzone
            Section 8 — Product Info:
              Weight, Country of Origin, Warranty Months
            Section 9 — SEO:
              Meta Title EN/AR, Meta Desc EN/AR (text-area partial),
              Canonical URL
            Section 10 — Flags:
              Featured toggle, Is New toggle, Sort Order number
            Save button (button partial)

- [ ] 6.4.5  Create `app/templates/admin/products/create.html`
            Extends form.html partial, POSTs to `admin.products_store`

- [ ] 6.4.6  Create `app/templates/admin/products/edit.html`
            Same form, PUTs (via a hidden `_method=PUT` field + Flask method-override, or a
            plain POST to an `/edit` route since HTML forms don't support PUT natively) to
            `admin.products_update`, prefilled with `product`

- [ ] 6.4.7  Create `app/templates/admin/products/import.html`
            dropzone partial for CSV upload
            POSTs to `admin.products_import`, shows flash success/error

### 6.5 Orders Admin

- [ ] 6.5.1  Create `app/blueprints/admin/orders.py`
            `index()`        → paginated orders, filters: status/payment_status/payment_method/
                  date_range/salesperson, search order_number/email/phone
            `show()`         → single order with items + history + payment
            `update_status()`→ POST: new status + comment → `OrderService.update_status()`
            `quick_pay_link()`→ POST: select gateway → `PaymentServiceFactory` → return link (JSON,
                  since this is an AJAX call from the admin page)
            `export()`       → stream CSV

- [ ] 6.5.2  Create `app/templates/admin/orders/index.html`
            Status tab bar (All/Pending/Confirmed/Processing/Shipped/Delivered/Cancelled/Refunded)
            Filter row: payment status, payment method, date range (Flatpickr via date-picker
                  partial), salesperson select
            Search input: order_number / email / phone
            Table: Order # | Date | Customer | Items count | Total (AED) | Payment Method |
                  Status badge | Payment Status badge | Actions
            Export CSV button

- [ ] 6.5.3  Create `app/templates/admin/orders/show.html`
            Left column:
              Order summary card: order #, date, status badge, payment status badge
              Items table: image, name, SKU, tire size label, qty, unit price, subtotal
              Payment info card: gateway, ref, amount, status
              Status history timeline (Alpine.js accordion)
            Right column (actions panel):
              Update Status: select-inputs partial + textarea → POST update_status
              Quick Pay Link: gateway select + "Generate Link" button → fetch() AJAX → show
                  link in a modal partial with copy button + "Email to Customer" button
              Print Invoice: `window.print()` link

### 6.6 Enquiries Admin

- [x] 6.6.1  Create `app/blueprints/admin/enquiries.py`
            `index()`  → paginated, filter by form_type (tab), status, date range, assigned_to
            `show()`   → single enquiry all fields
            `update()` → POST: status, assigned_to, reply_notes → redirect back

- [x] 6.6.2  Create `app/templates/admin/enquiries/index.html`
            Tab bar: All | Contact | Service Booking | Callback | Quote Request | Insurance
            Each tab: table with relevant columns shown (service booking shows vehicle/date cols)
            Filter: status select, date range, assigned_to select
            Row click → enquiry show page

- [x] 6.6.3  Create `app/templates/admin/enquiries/show.html`
            Shows all fields for the enquiry's form_type in a detail card
            Status select-inputs partial, Assign To select, Reply Notes textarea → POST update

### 6.7 Customers Admin

- [x] 6.7.1  Create `app/blueprints/admin/customers.py`
            `index()` → paginated customers, searchable by name/email/phone
            `show()`  → customer profile + orders + reward points + addresses

- [x] 6.7.2  Create `app/templates/admin/customers/index.html`
            Search input, table: Name | Email | Phone | Orders count | Points balance | Status | Joined | Actions

- [x] 6.7.3  Create `app/templates/admin/customers/show.html`
            Profile card (profile-card partial),
            Tab panels (Alpine.js): Orders | Reward Points | Addresses
            Each tab: relevant table/list

### 6.8 Brands Admin

- [ ] 6.8.1  Create `app/blueprints/admin/brands.py` (CRUD route group)
- [ ] 6.8.2  Create `app/templates/admin/brands/index.html`
            Table: Logo | Name | Slug | Country | Products count | Featured | Status | Actions
- [ ] 6.8.3  Create `app/templates/admin/brands/form.html`
            Logo dropzone (uploads via `MediaService`), Name EN/AR, Country, Sort Order,
            Featured toggle, Status select
- [ ] 6.8.4  Create `app/templates/admin/brands/create.html` + `edit.html`

### 6.9 Categories Admin

- [ ] 6.9.1  Create `app/blueprints/admin/categories.py` (CRUD route group)
- [ ] 6.9.2  Create `app/templates/admin/categories/index.html`
            Tree-style nested list (Alpine.js collapsible), flat table toggle
            Columns: Name | Parent | Slug | Products count | Sort Order | Status | Actions
- [ ] 6.9.3  Create `app/templates/admin/categories/form.html`
            Image dropzone, Name EN/AR, Parent Category select, Slug, Description EN/AR,
            Sort Order, Status, Meta Title/Desc EN/AR
- [ ] 6.9.4  Create `app/templates/admin/categories/create.html` + `edit.html`

### 6.10 Coupons Admin

- [ ] 6.10.1 Create `app/blueprints/admin/coupons.py` (CRUD route group)
- [ ] 6.10.2 Create `app/templates/admin/coupons/index.html`
            Table: Code | Type | Value | Min Order | Used/Total | Expires | Status | Actions
- [ ] 6.10.3 Create `app/templates/admin/coupons/form.html`
            Code, Type select (percent/fixed/free_shipping), Value, Min Order Amount,
            Max Discount, Uses Total, Uses Per Customer,
            Start/End dates (date-picker partial), Active toggle

### 6.11 Banners Admin & Dynamic Page Sections Studio

- [x] 6.11.1 Create `app/blueprints/admin/banners.py` (CRUD route group) & `app/models/page_section.py`
- [x] 6.11.2 Create `app/templates/admin/banners/index.html` & `app/templates/visionadmin/sections.html`
            Table: Desktop image preview | Title | Position | Sort | Active | Dates | Actions
            Predefined Layouts: Content+Image, Features/Pillars, Stats Band, Mission & Team, CTA Box
- [x] 6.11.3 Create `app/templates/admin/banners/form.html` & Section Editor with Bilingual EN/AR support,
            structured JSON repeater items, sorting, and active toggles

### 6.12 Special Offers Admin

- [ ] 6.12.1 Create `app/blueprints/admin/special_offers.py` (CRUD route group)
- [ ] 6.12.2 Create `app/templates/admin/special-offers/index.html`
- [ ] 6.12.3 Create `app/templates/admin/special-offers/form.html`
            Image dropzone, Title EN/AR, Description EN/AR textarea, Badge Text,
            Link URL, Discount %, Start/End dates, Active toggle, Sort Order

### 6.13 Blogs Admin

- [x] 6.13.1 Create `app/blueprints/admin/blogs.py` (CRUD route group & `app/models/blog.py`)
- [x] 6.13.2 Create `app/templates/admin/blogs/index.html` (`app/templates/visionadmin/blogs.html`)
            Table: Title | Category | Author | Status | Published At | Actions
- [x] 6.13.3 Create `app/templates/admin/blogs/form.html`
            Featured image dropzone, Title EN/AR, Slug, Blog Category select, Status select,
            Content EN/AR rich text, Excerpt EN/AR textarea, SEO fields
- [x] 6.13.4 Create `app/templates/admin/blogs/create.html` + `edit.html` (Integrated in Studio Modal)

### 6.14 FAQs Admin

- [ ] 6.14.1 Create `app/blueprints/admin/faqs.py` (CRUD route group)
- [ ] 6.14.2 Create `app/templates/admin/faqs/index.html`
            Sortable list via drag-handle (Alpine.js + Sortable.js), AJAX save sort order
            (POST to a small `admin.faqs_reorder` route)
            Table: Question (EN) | Category Tag | Active | Sort | Actions
- [ ] 6.14.3 Create `app/templates/admin/faqs/form.html`
            Question EN/AR textarea, Answer EN/AR textarea, Category Tag, Sort Order, Active toggle

### 6.15 Stores Admin

- [ ] 6.15.1 Create `app/blueprints/admin/stores.py` (CRUD route group)
- [ ] 6.15.2 Create `app/templates/admin/stores/index.html`
            Table: Name | City | Emirate | Phone | Active | Actions
- [ ] 6.15.3 Create `app/templates/admin/stores/form.html`
            Name EN/AR, Address EN/AR, City, Emirate select, Phone, Email,
            Google Maps embed with lat/lng picker (Alpine.js + Google Maps JS API),
            Hours JSON editor (repeater: day + open time + close time using Flatpickr),
            Services JSON checklist (tire change, balancing, alignment, etc.), Active toggle

### 6.16 Purchase Orders Admin

- [ ] 6.16.1 Create `app/blueprints/admin/purchase_orders.py`
            `index()`  → paginated POs filtered by status
            `create_view()` → show form
            `store()`  → create PO + items → redirect show
            `show()`   → PO detail with items + vendor
            `update()` → update status (draft/sent/confirmed/received/cancelled)

- [ ] 6.16.2 Create `app/templates/admin/purchase-orders/index.html`
            Status tabs, table: PO # | Vendor | Items count | Total | Status | Date | Actions

- [ ] 6.16.3 Create `app/templates/admin/purchase-orders/form.html`
            Vendor select, PO date (date-picker partial), Notes textarea
            Line items repeater (Alpine.js `x-data` array):
              Product search input → select → auto-fill SKU + Name
              Qty input, Unit Price input, line subtotal (computed via Alpine.js)
              Add/Remove row buttons
            Totals: subtotal, tax input, grand total (computed via Alpine.js)

- [ ] 6.16.4 Create `app/templates/admin/purchase-orders/show.html`
            PO header card, items table, status update select → POST update

### 6.17 Reports Admin

- [x] 6.17.1 Create `app/blueprints/admin/reports.py` (`app/reports_repo.py` + `app/api.py`)
            `index()` → date range filter, payment method filter, salesperson filter
                      queries via SQLAlchemy: daily/monthly sales, top 10 products, revenue by brand
                      Pass chart data arrays to template (JSON-encoded for ApexCharts via `tojson`)

- [x] 6.17.2 Create `app/templates/admin/reports/index.html` (`app/templates/reports.html`)
            Filter bar: date range, scraper execution reports, per-URL breakdown metrics,
            status monitoring, downloadable `.xlsx` reports

### 6.18 Settings Admin

- [x] 6.18.1 Create `app/blueprints/admin/settings.py` (`app/api.py` /visionadmin/api/settings)
            `index()`  → load all settings grouped → pass to template
            `update()` → POST: validate + `Setting.set()` for each key → redirect back with success

- [x] 6.18.2 Create `app/templates/admin/settings/index.html` (`app/templates/visionadmin/settings.html`)
            Tab panels: General | Reviewer Settings | Content & SEO Config

### 6.19 Admin Users Admin

- [x] 6.19.1 Create `app/blueprints/admin/admin_users.py` (`app/auth.py` + `app/api.py`)
            Visible to `super_admin` role only (a `@require_role('super_admin')` decorator)
            `index()`    → paginated admin users
            `create_view()` → show form
            `store()`    → create admin user with hashed password
            `edit_view()`   → show edit form (no password shown)
            `update()`   → update fields, optionally reset password if filled
            `destroy()`  → soft-delete (`IsDeleted = 1`, Trash bin support)

- [x] 6.19.2 Create `app/templates/admin/admin-users/index.html` (`app/templates/admin.html` & `app/templates/trash.html`)
            Table: Name | Email | Role badge | Active | Last Login / Created At | Actions

- [x] 6.19.3 Create `app/templates/admin/admin-users/form.html`
            Name, Email, Role select (SuperAdmin/Admin/User), Active toggle,
            Password / Confirm Password, Soft delete / Restore

### 6.20 Admin Sidebar Navigation (AdminMenuHelper)

- [x] 6.20.1 Populate `app/helpers/admin_menu.py::AdminMenuHelper.menu()` nav items:
            Dashboard → `/admin`
            Products & Scraper Management → `/files`, `/`
            Enquiries / Leads CRM → `/visionadmin/enquiries`
            Content (group):
              Static Pages Studio → `/visionadmin/pages`
              Page Sections Dynamic Layout Studio → `/visionadmin/sections`
              Blogs Studio → `/visionadmin/blogs`
            Reports & Audit Logs → `/reports`
            Settings → `/visionadmin/settings`
            Admin Users & Customers → `/Admin`, `/trash` (SuperAdmin role gate)

- [x] 6.20.2 Update `app/templates/admin/partials/layouts/sidebar.html` (`app/templates/visionadmin/base.html` & `app/templates/base.html`)
            Branded navigation, dynamic active route highlighting, responsive mobile sidebar drawer

### 6.21 Static Pages Management Studio (Added to CMS)

- [x] 6.21.1 Create `app/models/page.py` & `app/api.py` (`/visionadmin/api/pages`)
            CRUD routes with slug management, bilingual EN/AR support, hero banner uploads, and SEO parameters
- [x] 6.21.2 Create `app/templates/visionadmin/pages.html` & `app/static/visionadmin/pages.js`
            Data table with live status badges, creation/edit modals, image uploader, and search filter

### 6.22 File & Python Scraper Management Studio (Added to Automation)

- [x] 6.22.1 Create `app/files_repo.py` & `app/file_scraper_runner.py`
            Python script registration, URL JSON management, process concurrency runner (up to 4 jobs)
- [x] 6.22.2 Create `app/templates/files.html` & `app/static/files.js`
            Scraper cards/table, multi-select batch run, CSV URL import, live polling indicators

---

## PHASE 7 — Flask API Layer
> Flask serves a JSON REST API consumed same-origin by the `site` blueprint's Jinja2 pages
> (Phase 8) for cart, checkout, live search, and tyre-finder interactions, and, for a few
> read-only lookups, by the admin panel. All routes: `app/blueprints/api/` under `/api/v1/` prefix
> Auth: Flask-JWT-Extended (`@jwt_required()`), issued at login and held in an httpOnly cookie for
> the `site` blueprint's page JS (5.3.3/5.3.5); the admin panel uses its own Flask-Login session
> auth and does not go through this API layer
> Response format: Marshmallow schemas (`schema.dump(obj)`) — consistent JSON structure,
> replacing Laravel API Resources
> Webhook routes: public, no auth, verified by gateway signature

### 7.1 API Foundation
- [ ] 7.1.1  Create `app/blueprints/api/__init__.py` structure:
           `api_bp = Blueprint('api', __name__, url_prefix='/api/v1')`
           Public routes (no auth): catalog, search, tire-finder, content, webhooks
           Protected routes (`@jwt_required()`): cart, orders, account, checkout
- [ ] 7.1.2  Create `app/schemas/base.py` base classes:
           `BaseSchema(Schema)` — a `wrap()` helper that adds `success`, `message` wrapper to
                  all responses (a plain function, since Marshmallow schemas serialize the
                  resource itself; wrapping happens in a small `api_response(data, message=None)`
                  helper used by every view)
           `paginated_response(pagination_obj, schema)` — wraps paginated results with
                  `meta` (page, per_page, total, pages) + `links` (next/prev URLs)
- [ ] 7.1.3  Create `app/schemas/product_schema.py::ProductSchema`
           Fields: id, sku, name_en, name_ar, slug, price, sale_price, current_price,
           is_on_sale, tire_size_label, tire_width, tire_height, tire_rim,
           tire_type, speed_rating, load_index, run_flat, ev_rated,
           fuel_efficiency, wet_grip, noise_level_db,
           stock_status, stock_qty, brand (nested: id+name+slug), category (nested: id+name+slug),
           image_url (WebP via MediaService), gallery_urls (list), meta_title_en/ar, meta_desc_en/ar
- [ ] 7.1.4  Create `app/schemas/brand_schema.py::BrandSchema`
           Fields: id, name, slug, logo_url, description_en, description_ar, country, is_featured
- [ ] 7.1.5  Create `app/schemas/category_schema.py::CategorySchema`
           Fields: id, name_en, name_ar, slug, parent_id, image_url, children (nested, recursive)
- [ ] 7.1.6  Create `app/schemas/order_schema.py::OrderSchema` + `OrderItemSchema`
- [ ] 7.1.7  Create `app/schemas/cart_schema.py::CartSchema` + `CartItemSchema`
- [ ] 7.1.8  Create `app/schemas/user_schema.py::UserSchema` + `AddressSchema`
- [ ] 7.1.9  Create `app/schemas/blog_schema.py::BlogSchema` + `BlogCategorySchema`
- [ ] 7.1.10 Create `app/schemas/content_schema.py::BannerSchema`, `SpecialOfferSchema`,
            `StoreSchema`, `FaqSchema`

### 7.2 Auth API Endpoints
- [ ] 7.2.1  Create `app/blueprints/api/auth.py::login()` / `logout()`
           POST `/api/v1/auth/login` — validate credentials, return JWT access+refresh tokens
                  (`create_access_token`/`create_refresh_token`) + user schema
           POST `/api/v1/auth/logout` — with a blocklist configured (5.3.3), add the current
                  token's `jti` to the blocklist; otherwise this is a client-side no-op (JWT is
                  stateless) and the endpoint simply confirms
- [ ] 7.2.2  Create `app/blueprints/api/auth.py::register()`
           POST `/api/v1/auth/register` — create user, return tokens + user
- [ ] 7.2.3  Create `app/blueprints/api/auth.py::forgot_password()` / `reset_password()`
           POST `/api/v1/auth/forgot-password` — generate a signed reset token
                  (`itsdangerous.URLSafeTimedSerializer`), send reset link email via Celery task
           POST `/api/v1/auth/reset-password` — validate token + update password
- [ ] 7.2.4  Create `app/blueprints/api/auth.py::current_user_view()`
           GET `/api/v1/auth/user` — return authenticated user (`@jwt_required()` protected)
- [ ] 7.2.5  Create `app/blueprints/api/social_auth.py`
           GET  `/api/v1/auth/social/<provider>` — redirect to OAuth provider via Authlib
           GET  `/api/v1/auth/social/<provider>/callback` — handle callback,
                create/find user, issue JWT (set as the httpOnly cookie per 5.3.3), `login_user()`
                against the site `LoginManager` (5.2.3), redirect to `site.social_callback` (8.8.4)

### 7.3 Catalog API Endpoints
- [ ] 7.3.1  Create `app/blueprints/api/products.py`
           GET `/api/v1/products` — paginated, filters: brand, category, width, height,
                rim, tire_type, vehicle_type, min_price, max_price, sort, per_page
                Uses `SearchService` (ES) for filtered results
           GET `/api/v1/products/<slug>` — single product with brand + category
- [ ] 7.3.2  Create `app/blueprints/api/search.py`
           GET `/api/v1/search?q=...` — ES full-text: products + brands + blogs + faqs
           GET `/api/v1/search/autocomplete?q=...` — fast partial match, returns top 8
- [ ] 7.3.3  Create `app/blueprints/api/brands.py`
           GET `/api/v1/brands` — all active brands (cached via `flask_caching`, Redis 6h)
           GET `/api/v1/brands/<slug>` — brand + paginated products
- [ ] 7.3.4  Create `app/blueprints/api/categories.py`
           GET `/api/v1/categories` — full tree (cached Redis 6h)
           GET `/api/v1/categories/<slug>` — category + subcategories + paginated products

### 7.4 Tire Finder API Endpoints
- [ ] 7.4.1  Create `app/blueprints/api/tyre_finder.py`
           GET `/api/v1/tyre-finder/makes` — distinct makes (Redis cached 24h)
           GET `/api/v1/tyre-finder/models?make=` — models for make (Redis cached 24h)
           GET `/api/v1/tyre-finder/years?make=&model=` — years
           GET `/api/v1/tyre-finder/tyre-size?make=&model=&year=` — front+rear size
           GET `/api/v1/tyre-finder/widths` — distinct tire_width from products
           GET `/api/v1/tyre-finder/heights?width=` — filtered heights
           GET `/api/v1/tyre-finder/rims?width=&height=` — filtered rims

### 7.5 Cart API Endpoints (`@jwt_required(optional=True)` — guest-or-auth)
- [ ] 7.5.1  Create `app/blueprints/api/cart.py`
           GET    `/api/v1/cart` — current cart with items + totals
           POST   `/api/v1/cart/items` — add item `{product_id, qty}`
           PUT    `/api/v1/cart/items/<id>` — update qty
           DELETE `/api/v1/cart/items/<id>` — remove item
           POST   `/api/v1/cart/coupon` — apply coupon `{code}`
           DELETE `/api/v1/cart/coupon` — remove coupon
           Note: guest cart identified by `X-Cart-Token` header (UUID generated client-side in
                 `site.js`, 1.3.12/8.2.1) merged into user cart on login (`CartService.merge_guest_cart`)

### 7.6 Checkout & Order API Endpoints (`@jwt_required()`)
- [ ] 7.6.1  Create `app/blueprints/api/checkout.py`
           POST `/api/v1/checkout` — create order from cart, return order + payment URL
           Body: `{address_id|new_address, delivery_type, delivery_date, time_slot,
                  payment_method, coupon_code, redeem_points}`
- [ ] 7.6.2  Create `app/blueprints/api/orders.py`
           GET `/api/v1/orders` — paginated order history
           GET `/api/v1/orders/<order_number>` — single order detail

### 7.7 Account API Endpoints (`@jwt_required()`)
- [ ] 7.7.1  Create `app/blueprints/api/account.py`
           PUT  `/api/v1/account/profile` — update name, phone, locale
           POST `/api/v1/account/password` — change password
- [ ] 7.7.2  Create `app/blueprints/api/addresses.py`
           GET    `/api/v1/account/addresses`
           POST   `/api/v1/account/addresses`
           PUT    `/api/v1/account/addresses/<id>`
           DELETE `/api/v1/account/addresses/<id>`
- [ ] 7.7.3  Create `app/blueprints/api/reward_points.py`
           GET `/api/v1/account/reward-points` — balance + paginated history

### 7.8 Content API Endpoints (Public)
- [ ] 7.8.1  Create `app/blueprints/api/content.py`
           GET `/api/v1/banners?position=homepage_hero` — active banners by position
           GET `/api/v1/special-offers` — active offers
           GET `/api/v1/stores` — all active stores (optionally `?emirate=Dubai`)
           GET `/api/v1/faqs` — active FAQs grouped by category_tag
- [ ] 7.8.2  Create `app/blueprints/api/blogs.py`
           GET `/api/v1/blogs` — paginated, filterable by category
           GET `/api/v1/blogs/<slug>` — single post

### 7.9 Payment & Quick Pay API
- [ ] 7.9.1  Create `app/blueprints/api/payments/tamara.py`
           POST `/api/v1/payments/tamara/webhook` (public, signature verified)
           GET  `/api/v1/payments/tamara/success` (redirect callback)
           GET  `/api/v1/payments/tamara/cancel`
- [ ] 7.9.2  Create `app/blueprints/api/payments/tabby.py`
- [ ] 7.9.3  Create `app/blueprints/api/payments/stripe.py`
           POST `/api/v1/payments/stripe/webhook` (public, `Stripe-Signature` verified)
- [ ] 7.9.4  Create `app/blueprints/api/payments/totalpay.py`
- [ ] 7.9.5  Create `app/blueprints/api/quick_pay.py`
           GET  `/api/v1/quick-pay/<token>` — validate token, return order summary
           POST `/api/v1/quick-pay/<token>/pay` — initiate payment for token

### 7.10 Enquiries API (Public)
- [ ] 7.10.1 Create `app/blueprints/api/enquiries.py`
            POST `/api/v1/enquiries` — accepts any form_type, validates per type (Marshmallow
                  schema with a `form_type`-conditional validation method)
            Body: `{form_type, name, email, phone, message, ...type-specific fields}`

---

## PHASE 8 — Jinja2 Customer Frontend (Flask Blueprint `site`)
> Same Flask app/process as the admin panel and API — a second Blueprint, `site_bp`, renders
> server-side Jinja2 templates for every customer-facing page, styled with Tailwind CSS v4 and
> made interactive with Alpine.js, mirroring how Phase 6 built the admin panel with TailAdmin.
> Page loads read data directly via SQLAlchemy models/services (no internal HTTP hop) — this
> replaces Next.js's RSC/SSR data fetching with a plain Flask view function passing context into
> `render_template()`. Dynamic, stateful interactions that genuinely need a round trip after the
> page has loaded — cart, checkout, live search-as-you-type, tyre-finder cascades — call the
> existing `/api/v1` JSON endpoints (Phase 7) via `fetch()`/Alpine.js, the same pattern the former
> Next.js frontend used to talk to the API, just same-origin now (no CORS, no cookie-bridging).
> **Auth:** a third Flask-Login instance scoped to `User` (5.2.3), cookie-session based, gates
> `/account/*` pages and drives header login-state; the API's JWT (5.3) is issued at the same
> login and set as an httpOnly cookie by Flask directly, so page JS can call `/api/v1/*` without
> ever touching a bearer token — simpler than the Next.js route-handler cookie-bridge because
> everything is one origin.
> **i18n:** Flask-Babel (`/en/...`, `/ar/...` URL prefixes) + `{{ _('...') }}` translation strings
> in templates, replacing `next-intl`; `dir="rtl"` set on `<html>` for `ar`.
> **Images:** the shared `img()` Jinja macro (10.2.8/6.1.1) emits `<picture>`/`srcset` WebP via
> `MediaService` conversions — the direct equivalent of `next/image`.

### 8.1 Project Setup
- [ ] 8.1.1  Create `app/blueprints/site/__init__.py`:
           `site_bp = Blueprint('site', __name__, template_folder='../../templates/site')`
           Mounted with a `/<locale>` URL prefix (`en`/`ar`) in `create_app()`; a
           `site_bp.before_request` reads the locale from the path into `g.locale` and 404s on
           anything else (mirrors `next-intl`'s locale-prefix routing)
- [ ] 8.1.2  Register `site_bp` in `create_app()` alongside `admin_bp` and `api_bp`
- [ ] 8.1.3  Configure Flask-Babel: `BABEL_DEFAULT_LOCALE='en'`, `BABEL_SUPPORTED_LOCALES=['en','ar']`
           (shared with 1.1.10); extract/compile translation strings with
           `pybabel extract/update/compile` into `translations/en/LC_MESSAGES/messages.po` + `ar/...`
- [ ] 8.1.4  Create `app/static/src/site.css` — Tailwind v4 entry for the storefront (1.3.10),
           a separate Vite bundle from `admin.css`
- [ ] 8.1.5  Create `app/static/src/site.js` — Alpine.js init + site-wide stores (8.2) + a small
           `apiFetch(path, opts)` helper that calls `/api/v1/...` same-origin, attaches the
           `X-CSRF-TOKEN` header required by the cookie-JWT flow (5.3.5), and redirects to
           `site.login` on a 401
- [ ] 8.1.6  Create `app/templates/site/layouts/base.html`:
           `<html lang="{{ g.locale }}" dir="{{ 'rtl' if g.locale == 'ar' else 'ltr' }}">`
           Loads `site.css`/`site.js` via the `vite_asset()` Jinja2 global (1.3.9)
           Skip navigation link, `{% include "site/partials/header.html" %}` / `footer.html` /
           `cart_drawer.html`
           Named blocks: `title`, `meta_description`, `canonical`, `og_image`, `schema`, `content`
- [ ] 8.1.7  Create `app/templates/site/layouts/auth.html` — minimal layout for
           login/register/forgot-password pages
- [ ] 8.1.8  Add to `.env`: `SITE_URL` (public base URL for canonical/OG/sitemap),
           `GOOGLE_MAPS_KEY` (store locator, 8.9.3)

### 8.2 Client-Side State (Alpine.js stores — replaces Zustand/SWR hooks)
- [ ] 8.2.1  `Alpine.store('cart', {...})` in `site.js` — items, totals, coupon, drawer open/close;
           hydrated via `GET /api/v1/cart` on page load, mutated through the cart endpoints (7.5);
           owns the guest `X-Cart-Token` (generates + persists a UUID in `localStorage` if absent)
- [ ] 8.2.2  `Alpine.store('auth', {...})` — `isLoggedIn`, `user`; hydrated once from a small
           JSON blob the base layout renders from Flask's `current_user` — no client refetch needed
- [ ] 8.2.3  `apiFetch()` wrapper (8.1.5) used by every client-side call in this phase — the one
           place that knows about `/api/v1`, CSRF header, and 401 handling
- [ ] 8.2.4  Debounced search-bar component (`x-data`, `setTimeout` 300ms) calling
           `/api/v1/search/autocomplete` (8.3.4)
- [ ] 8.2.5  Tyre-finder cascade component (`x-data`) driving `/api/v1/tyre-finder/*` step by
           step (make → model → year, or width → height → rim), used on 8.5.1

### 8.3 Layout Partials
- [ ] 8.3.1  `app/templates/site/partials/header.html` — logo, nav, search bar (8.3.4), cart icon
           (badge bound to `$store.cart.count`), language switcher (links to the same route under
           the other locale prefix)
- [ ] 8.3.2  `app/templates/site/partials/footer.html` — links, social, newsletter form (posts to
           `site.newsletter_subscribe`, backed by the `newsletter_subscribers` table)
- [ ] 8.3.3  `app/templates/site/partials/cart_drawer.html` — slide-over (`x-show` + Alpine
           transition), items, totals, checkout CTA
- [ ] 8.3.4  `app/templates/site/partials/search_bar.html` — input + autocomplete dropdown (8.2.4)
- [ ] 8.3.5  `app/templates/site/partials/skeleton.html` — Jinja macro emitting loading-placeholder
           markup sized to match the real card/row it stands in for, used only for the handful of
           client-hydrated widgets (cart count, autocomplete results)

### 8.4 Pages — Catalog
- [ ] 8.4.1  `app/blueprints/site/pages.py::home()` → `GET /<locale>/`
           Queries banners, featured products/brands, special offers directly (no HTTP hop) →
           `site/home.html`: hero slider, tyre-finder widget, brands row, product grid, offers,
           blog preview
- [ ] 8.4.2  `app/blueprints/site/catalog.py::tyres_index()` → `GET /<locale>/tyres`
           Server-side filtered/paginated query — same params as the API's 7.3.1 (brand, category,
           width, height, rim, type, vehicle_type, min/max price, sort, page), reusing
           `SearchService` directly → `site/tyres/index.html`; filter sidebar submits via GET
           query string, results re-render server-side (no client refetch needed for filtering)
- [ ] 8.4.3  `app/blueprints/site/catalog.py::tyre_detail(slug)` → `GET /<locale>/tyres/<slug>` →
           `site/tyres/show.html` — image gallery, specs, "Add to Cart" button (`apiFetch` POST to
           `/api/v1/cart/items`), Tamara/Tabby widget, related products
- [ ] 8.4.4  `app/blueprints/site/catalog.py::brands_index()` → `GET /<locale>/brands` — A–Z grid
           → `site/brands/index.html`
- [ ] 8.4.5  `app/blueprints/site/catalog.py::brand_detail(slug)` → `GET /<locale>/brands/<slug>`
           → `site/brands/show.html` — brand info + paginated products
- [ ] 8.4.6  `app/blueprints/site/catalog.py::category_detail(slug)` →
           `GET /<locale>/categories/<slug>` → `site/categories/show.html`
- [ ] 8.4.7  `app/blueprints/site/catalog.py::size_search(size)` → `GET /<locale>/size/<size>`
           e.g. `/size/225-55-r17` → reuses `site/tyres/index.html` with the size parsed into a
           preset filter

### 8.5 Pages — Tyre Finder
- [ ] 8.5.1  `app/blueprints/site/tyre_finder.py::index()` → `GET /<locale>/tyre-finder` →
           `site/tyre-finder/index.html` — multi-step finder (Alpine `x-data`, 8.2.5):
           Step 1 by-vehicle or by-size; Step 2a make→model→year cascade; Step 2b
           width→height→rim cascade; Step 3 results fetched from `/api/v1/products` with the
           resolved size and rendered into the page without a full reload

### 8.6 Pages — Search
- [ ] 8.6.1  `app/blueprints/site/search.py::search()` → `GET /<locale>/search?q=&tab=` — tabs
           (Products/Brands/Blogs/FAQs) rendered server-side using `SearchService.search_all()`
           directly → `site/search/index.html`

### 8.7 Pages — Cart & Checkout
- [ ] 8.7.1  `app/blueprints/site/cart.py::cart_page()` → `GET /<locale>/cart` →
           `site/cart/index.html` — a shell page; items/totals hydrate client-side from
           `$store.cart` (8.2.1), same data the drawer (8.3.3) shows
- [ ] 8.7.2  `app/blueprints/site/checkout.py::checkout_page()` → `GET /<locale>/checkout`
           (login required, site `LoginManager`) → `site/checkout/index.html` — multi-step form
           (Alpine `x-data` step state): Step 1 address, Step 2 delivery, Step 3 payment method →
           `apiFetch` POST to `/api/v1/checkout` (7.6.1) → redirect to the gateway or to 8.7.3
- [ ] 8.7.3  `app/blueprints/site/checkout.py::checkout_success(order_number)` →
           `GET /<locale>/checkout/success/<order_number>` → `site/checkout/success.html`
- [ ] 8.7.4  `app/blueprints/site/checkout.py::quick_pay(token)` →
           `GET /<locale>/quick-pay/<token>` → `site/checkout/quick_pay.html` — validates the
           token server-side via `QuickPaymentLinkService.validate_token()` (8.10.7), shows the
           order summary + gateway selection, no login required

### 8.8 Pages — Auth & Account
- [ ] 8.8.1  `app/blueprints/site/auth.py::login()` → `GET/POST /<locale>/auth/login` — WTForms
           `LoginForm`; on success `login_user()` against the site `LoginManager` (5.2.3) + the
           JWT cookie is set by the same request → redirect to `?next=` or `/account`
           Google/Facebook buttons link straight to `/api/v1/auth/social/<provider>` (7.2.5)
- [ ] 8.8.2  `app/blueprints/site/auth.py::register()` → `GET/POST /<locale>/auth/register`
- [ ] 8.8.3  `app/blueprints/site/auth.py::forgot_password()` →
           `GET/POST /<locale>/auth/forgot-password`
- [ ] 8.8.4  `app/blueprints/site/auth.py::social_callback()` → `GET /<locale>/auth/social/callback`
           — lands here after the API's OAuth callback (7.2.5) already issued the JWT cookie and
           called `login_user()`; this route just redirects into the site (replaces the Next.js
           callback page — no cross-app token hand-off needed since it's one app now)
- [ ] 8.8.5  `app/blueprints/site/account.py::dashboard()` → `GET /<locale>/account`
           (login required)
- [ ] 8.8.6  `app/blueprints/site/account.py::orders()` → `GET /<locale>/account/orders` — order history
- [ ] 8.8.7  `app/blueprints/site/account.py::order_detail(order_number)` →
           `GET /<locale>/account/orders/<order_number>`
- [ ] 8.8.8  `app/blueprints/site/account.py::addresses()` → `GET /<locale>/account/addresses` —
           address CRUD as server-rendered forms (POST back to this blueprint, consistent with
           the rest of Phase 8 rather than a client-only fetch flow)
- [ ] 8.8.9  `app/blueprints/site/account.py::profile()` → `GET/POST /<locale>/account/profile`
- [ ] 8.8.10 `app/blueprints/site/account.py::reward_points()` →
           `GET /<locale>/account/reward-points` — balance + paginated history

### 8.9 Pages — Content
- [ ] 8.9.1  `app/blueprints/site/content.py::special_offers()` → `GET /<locale>/special-offers`
- [ ] 8.9.2  `app/blueprints/site/content.py::ev_tyres()` → `GET /<locale>/ev-tyres`
- [ ] 8.9.3  `app/blueprints/site/content.py::store_locator()` → `GET /<locale>/store-locator` —
           Google Maps JS API + store list queried directly from `Store`
- [ ] 8.9.4  `app/blueprints/site/content.py::about()` → `GET /<locale>/about-us`
- [ ] 8.9.5  `app/blueprints/site/content.py::contact()` → `GET/POST /<locale>/contact-us` — POST
           submits via `apiFetch` to `/api/v1/enquiries` (7.10.1, `form_type=contact`)
- [ ] 8.9.6  `app/blueprints/site/content.py::faq()` → `GET /<locale>/faq` — accordion (Alpine),
           grouped by `category_tag`
- [ ] 8.9.7  `app/blueprints/site/content.py::insurance()` → `GET /<locale>/insurance`
- [ ] 8.9.8  `app/blueprints/site/content.py::service_booking()` →
           `GET/POST /<locale>/service-booking` — POST → enquiries API, `form_type=service_booking`
- [ ] 8.9.9  `app/blueprints/site/content.py::request_callback()` →
           `GET/POST /<locale>/request-callback`
- [ ] 8.9.10 `app/blueprints/site/content.py::quote_request()` →
           `GET/POST /<locale>/quote-request`
- [ ] 8.9.11 `app/blueprints/site/blog.py::index()` → `GET /<locale>/blog` — paginated, category filter
- [ ] 8.9.12 `app/blueprints/site/blog.py::show(slug)` → `GET /<locale>/blog/<slug>` — full post + related

### 8.10 SEO Setup (Jinja2/Flask)
- [ ] 8.10.1 Every `site/*.html` template fills the `title`/`meta_description`/`canonical`/
           `og_image` blocks (8.1.6) — the direct equivalent of `generateMetadata()`
- [ ] 8.10.2 No ISR/`generateStaticParams()` needed — every page renders on request; where a
           listing is expensive (product/category listing), add Redis response caching per
           Phase 10.2 instead of a build-time regeneration step
- [ ] 8.10.3 JSON-LD via the `schema` block + `app/helpers/json_ld.py` (10.1.2–10.1.5), the same
           helpers the admin layout uses — Product schema, BreadcrumbList, Organization,
           LocalBusiness, Article
- [ ] 8.10.4 `SitemapService.generate()` (4.5.6) already builds the full sitemap server-side for
           every route (products, categories, brands, blogs, static pages) — no separate
           `sitemap.ts`/API round trip needed
- [ ] 8.10.5 `app/static/robots.txt` (10.1.7) served directly by Flask
- [ ] 8.10.6 `<link rel="alternate" hreflang>` pairs in `site/layouts/base.html` for the current
           route's `en`/`ar` counterpart
- [ ] 8.10.7 `app/services/quick_pay_link_service.py::QuickPaymentLinkService` (Phase 4 services,
           also used by the admin panel):
           `generate(order, gateway)` → signed URL (`itsdangerous`) → `/<locale>/quick-pay/<token>` (8.7.4)
           `validate_token(token)` → returns order or raises

---

## PHASE 9 — Background Jobs & Cron (Celery + Celery Beat)

### 9.1 Mail Tasks
- [ ] 9.1.1  Create `app/tasks/mail_tasks.py::send_order_confirmation_email` → `mail` queue
- [ ] 9.1.2  Create `app/tasks/mail_tasks.py::send_order_status_email` → `mail` queue
- [ ] 9.1.3  Create `app/tasks/mail_tasks.py::send_abandoned_cart_email` → `mail` queue
- [ ] 9.1.4  Create `app/tasks/mail_tasks.py::send_enquiry_confirmation_email` → `mail` queue
- [ ] 9.1.5  Create `app/tasks/mail_tasks.py::send_quick_payment_link_email` → `mail` queue

### 9.2 Search Index Tasks
- [ ] 9.2.1  Create `app/tasks/index_tasks.py::index_product` → `search` queue (on product save)
- [ ] 9.2.2  Create `app/tasks/index_tasks.py::remove_product_from_index` → `search` queue (on delete)

### 9.3 Scheduled Tasks (Celery Beat — replaces Laravel's routes/console.php schedule)
- [ ] 9.3.1  Create `app/tasks/cron_tasks.py::snapshot_abandoned_carts`
           Schedule: every 30 minutes (`beat_schedule` entry, crontab or `timedelta(minutes=30)`)
           Logic: find carts with items, inactive 60+ min, save to abandoned_carts

- [ ] 9.3.2  Create `app/tasks/cron_tasks.py::send_abandoned_cart_emails`
           Schedule: every hour
           Logic: find eligible abandoned_carts (notified_count < 3), dispatch email task

- [ ] 9.3.3  Create `app/tasks/cron_tasks.py::sync_vehicles_from_api`
           Schedule: daily at 2am (`crontab(hour=2, minute=0)`)
           Logic: call wheel-api.klever.ae, upsert vehicles table, flush Redis cache

- [ ] 9.3.4  Create `app/tasks/cron_tasks.py::expire_reward_points`
           Schedule: daily at midnight
           Logic: expire points older than 12 months, add expiry records

- [ ] 9.3.5  Create `app/tasks/cron_tasks.py::generate_sitemaps`
           Schedule: daily at 3am
           Logic: call `SitemapService.generate()` — regenerate sitemap.xml (products, categories,
                  brands, blogs, pages)

- [ ] 9.3.6  Register all scheduled tasks in `celery_worker.py`'s `beat_schedule` dict
           (replaces `routes/console.php` schedule registrations)

---

## PHASE 10 — SEO & Performance

### 10.1 SEO
> SEO meta is handled by named blocks on both layouts — `admin/layouts/base.html` (6.1.5) for the
> admin panel and `site/layouts/base.html` (8.1.6) for the customer-facing site — via
> `{% block title %}`, `{% block meta_description %}`, `{% block canonical %}`,
> `{% block og_image %}`, `{% block schema %}`. No separate MetaTags component needed; this is
> also where the full customer-facing SEO surface now lives (Phase 8.10), since Flask renders
> every customer page directly.

- [ ] 10.1.1 ~~Create MetaTags component~~ — NOT NEEDED: layout named blocks cover this
            (admin: 6.1.5, site: 8.1.6)
- [ ] 10.1.2 Create `app/helpers/json_ld.py::product_schema(product)` (Product schema, returns a
            dict rendered via `{{ product_schema(product) | tojson }}` inside a
            `<script type="application/ld+json">` tag in the relevant template's `schema` block)
- [ ] 10.1.3 Create `app/helpers/json_ld.py::brand_schema(brand)` (Organization schema)
- [ ] 10.1.4 Create `app/helpers/json_ld.py::blog_post_schema(blog)` (Article schema)
- [ ] 10.1.5 Create `app/helpers/json_ld.py::local_business_schema(store)` (store pages)
- [ ] 10.1.6 Configure `SitemapService` (4.5.6) for all routes (replaces spatie/laravel-sitemap)
- [ ] 10.1.7 Create `app/static/robots.txt`
- [ ] 10.1.8 hreflang in layout ✅ already in `admin/layouts/base.html` (6.1.5) and
            `site/layouts/base.html` (8.10.6)

### 10.2 Performance
> Target: PageSpeed Insights 100/100 mobile + desktop
> See PERFORMANCE & QUALITY STANDARDS section above for full rules

- [ ] 10.2.1 Add Redis caching in `SearchService` (cache ES results 5 min per query hash, via
            `flask_caching`'s `@cache.memoize(timeout=300)`)
- [ ] 10.2.2 Add Redis caching for `Setting.get()` (cache all settings 1h)
- [ ] 10.2.3 Add Redis caching for vehicle makes/models (24h)
- [ ] 10.2.4 Add Redis caching for categories tree (6h), bust on category save (invalidate via
            `cache.delete_memoized()` in the model's `after_update`/`after_insert` event)
- [ ] 10.2.5 Add Redis caching for brand list (6h), bust on brand save
- [ ] 10.2.6 Configure Pillow-based media conversions in `MediaService` for Product/Brand/Blog:
            'webp-thumb'  → 150×150 WebP
            'webp-card'   → 400×400 WebP (product cards)
            'webp-full'   → 800px wide WebP (product detail)
            'webp-hero'   → 1200px wide WebP (banners/heroes)
            Always serve WebP; fall back to the original only if the browser rejects WebP
            (`Accept` header sniffing, rarely needed today)
- [ ] 10.2.7 ~~Configure responsive image sizes~~ — MERGED into 10.2.6 above
- [ ] 10.2.8 ~~Add img width/height~~ — enforced globally by a shared `img()` Jinja2 macro
            (6.1.1), imported into both `admin/` and `site/` templates
- [ ] 10.2.9 ~~Add loading="lazy"~~ — default in the `img()` macro (6.1.1)
- [ ] 10.2.10 Hero preload — via an `lcp_image_url` block in `admin/layouts/base.html` (6.1.5) and
            `site/layouts/base.html` (8.1.6)
- [ ] 10.2.11 Vite code splitting — configured in `vite.config.js` (1.3.9): es2020 target, manual chunks
- [ ] 10.2.12 Configure HTTP `Cache-Control` headers for `/static/build/*` assets in production:
             Nginx (or a Flask `after_request` hook for the dev server):
             `Cache-Control: public, max-age=31536000, immutable`
             Safe because Vite output filenames include a content hash
- [ ] 10.2.13 Configure gzip/Brotli compression at the Nginx layer in front of Gunicorn (for HTML,
             CSS, JS, JSON) — Flask itself does not compress responses; this is an Nginx
             `gzip on;`/`brotli on;` directive, not an application-level step
- [ ] 10.2.14 Pre-warm caches before each deploy: run a small `flask warm-cache` CLI command that
             populates the Redis caches from 10.2.1–10.2.5 (there is no Python equivalent of
             `php artisan optimize`'s bytecode/route/view compilation caching — Python has no
             such compile step, so this honestly replaces it with cache warming only, not a
             fabricated "optimize" command)
- [ ] 10.2.15 Add `app/static/favicon.ico` + `<link rel="icon">` in `admin/layouts/base.html`
             Add apple-touch-icon (180×180) for mobile
- [ ] 10.2.16 Final PageSpeed audit: run Lighthouse on homepage, product page, category page
             (all served by the Flask `site` blueprint) — must score 100/100 mobile + desktop
             before go-live
- [ ] 10.2.17 Final W3C audit: run https://validator.w3.org/nu/ on every unique page template
             Must pass with 0 errors (`x-*` Alpine.js attribute warnings are acceptable)

---

## PHASE 11 — Data Migration from Magento

### 11.1 Migration Scripts
- [ ] 11.1.1 Create `app/cli.py::migrate_products` (Flask CLI command `flask migrate-data products`)
            Read from Magento DB directly via a second SQLAlchemy engine/raw
            `mysql-connector-python` connection (catalog_product_flat_* tables)
            Map EAV attributes to flat product columns
            Handle: names, descriptions, prices, images, categories, brands

- [ ] 11.1.2 Create `flask migrate-data categories` command
            Read from Magento catalog_category_entity + flat tables

- [ ] 11.1.3 Create `flask migrate-data brands` command
            Read from MGS Brand tables

- [ ] 11.1.4 Create `flask migrate-data customers` command
            Read from Magento customer_entity + address tables
            Magento password hashes are not compatible with Werkzeug's hasher — mark all
            migrated users as requiring a password reset on first login rather than attempting
            hash translation

- [ ] 11.1.5 Create `flask migrate-data orders` command
            Read from Magento sales_order + sales_order_item tables
            Map order statuses to new ENUM values

- [ ] 11.1.6 Create `flask migrate-data product-images` command
            Copy images from Magento pub/media to Flask's media storage
            Trigger WebP conversion via `MediaService`

- [ ] 11.1.7 After migration: run `flask elastic reindex product` (custom CLI command that
            iterates all Product rows and calls `SearchService`'s indexing method — the
            equivalent of `php artisan scout:import`)

### 11.2 Go-Live Checklist
- [ ] 11.2.1 SSL certificate configured for new domain/subdomain
- [ ] 11.2.2 Run Gunicorn in production mode: `gunicorn -c gunicorn.conf.py wsgi:app` (behind
            Nginx, managed by systemd or the Procfile process manager)
- [ ] 11.2.3 Start Celery workers + Celery Beat for queue/cron processing
- [ ] 11.2.4 Warm Redis cache: featured products, brands, categories, settings
            (`flask warm-cache`, see 10.2.14)
- [ ] 11.2.5 Verify all payment webhooks point to new URLs
- [ ] 11.2.6 Test all 5 payment gateways end-to-end
- [ ] 11.2.7 Test Arabic locale: RTL layout, Arabic content display
- [ ] 11.2.8 DNS cutover from Magento to Flask
- [ ] 11.2.9 Monitor Flower dashboard for queue backlogs
- [ ] 11.2.10 Monitor Gunicorn/application error logs for first 24h

---

## SUMMARY

| Phase | Steps | Deliverable |
|-------|-------|-------------|
| 0 — Project Layout | 3 steps | Flask project scaffold |
| 1 — Foundation | 65 steps | Flask 3.x + all packages + ES + Gunicorn + Celery |
| 2 — Migrations | 35 steps | All 35 tables created (Alembic) |
| 3 — Models | 21 steps | All SQLAlchemy models |
| 4 — Services | 20 steps | Business logic layer |
| 5 — Middleware | 8 steps | Locale, admin auth, JWT auth |
| 6 — Admin Panel | 65 steps | Full Jinja2 admin panel using TailAdmin theme |
| 7 — Flask API Layer | 45 steps | Cart/checkout/search/tyre-finder + a few public endpoints (JSON) |
| 8 — Site (Jinja2) Frontend | 47 steps | All customer-facing pages, server-rendered Flask Blueprint |
| 9 — Jobs & Cron | 11 steps | Celery + Celery Beat background processing |
| 10 — SEO & Performance | 14 steps | Launch-ready optimization |
| 11 — Migration | 10 steps | Magento → Flask data |
| **TOTAL** | **~344 steps** | **Complete site** |

### Architecture Overview
```
Customer Browser → Flask Blueprint `site` + Jinja2 (SSR) ─┬→ MySQL / Redis / Elasticsearch (direct)
                    Alpine.js (client-side widgets)        └→ Flask API /api/v1 (fetch, same-origin:
                                                                cart, checkout, search, tyre-finder)
Admin Browser   → Flask Blueprint `admin` + Jinja2 (TailAdmin theme) → MySQL / Redis
                  Alpine.js + ApexCharts + Flatpickr (client-side only)
                  MediaService (Pillow-based image processing, local disk or S3)
                  Celery + Flower (queue dashboard) + Celery Beat (scheduled tasks)
                  Flask-Login: separate admin- and customer-scoped instances (session auth)
                  — separate again from Flask-JWT-Extended (API auth, cookie-delivered to `site`)
```

---

> File: TYRESCART_FLASK_JINJA_PLAN.md
> Migrated from: TYRESCART_FLASK_PLAN.md (Flask + Next.js variant) / originally TYRESCART_LARAVEL_PLAN.md
> Admin theme: TailAdmin (HTML/Tailwind assets) — Jinja2 + Alpine.js + ApexCharts
> Customer frontend: no Next.js — a second Jinja2 + Alpine.js Blueprint (`site`), same app as admin
> No Livewire equivalent needed · Flask API (JWT, cookie-delivered) backs `site`'s dynamic
> interactions · Flask-Login session auth serves both `admin` and `site` (separate instances)
> One Flask app serves the admin panel, the customer site, and the API — one deployable, not three
> Next action: Begin Phase 0 (project scaffold) and Phase 1.1–1.2 (bootstrap + core packages)
