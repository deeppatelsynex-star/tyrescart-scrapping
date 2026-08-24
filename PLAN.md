# TyresCart Platform — Admin Split Plan

Two separate admin surfaces on the same Flask app, each hidden behind its own
obscure path prefix (no direct root access, matching the existing
`/tcsadmin` convention):

| Prefix | Purpose | Audience |
|---|---|---|
| `https://tyrescart-scrapping.klever.ae/tcsadmin` | Scraper admin — existing tool (start/stop scrapers, live progress, execution reports, user/trash management) | Ops / engineering |
| `https://tyrescart-scrapping.klever.ae/visonadmin` | CMS — manage the public storefront (`/`, `/home`, and future public pages) | Content / marketing |

The public storefront itself (`templates/Client/Home.html`, served at `/`
and `/home`) is unaffected by either admin panel and stays reachable at the
bare domain root.

## Current state (already built, `/tcsadmin`)

```
app/
  app.py            # page routes: /tcsadmin/*, /login /logout /forgot-password
                     #   /reset-password aliases, / and /home -> Client/Home.html
  api.py            # /tcsadmin/api/* JSON endpoints (files, scraper jobs, admin users, reports)
  auth.py           # session/CSRF decorators, password reset tokens -- shared by both admin panels
  db.py             # single pymysql connection helper, shared by both
  files_repo.py, reports_repo.py, job_manager.py, file_scraper_runner.py,
  scraper_input.py, scraper_status_utils.py, mailer.py, init_db.py, cache_manager.py

templates/
  base.html         # shared shell (icon-only sidebar) for every /tcsadmin/* page
  login.html, forgot_password.html, reset_password.html
  files.html, Scrap.html, admin.html, trash.html, reports.html, scraper_guide.html
  404.html          # standalone, branches on session state
  Client/
    Home.html       # public storefront, unrelated to either admin panel

static/
  script.js, files.js, admin.js, trash.js, profile.js, reports.js, scraperGuide.js
  internal.css, style.css, css/dashboard.css
  assets/images/favicon-color.webp
```

## Proposed addition: `/visonadmin` (CMS)

Mirrors the `/tcsadmin` pattern (thin `app.py` page routes + a dedicated
`api.py`-style module for JSON endpoints + its own template/static
namespace) rather than bolting CMS routes into the existing scraper files.

```
app/
  vison_api.py      # NEW -- /visonadmin/api/* JSON endpoints (CRUD for pages,
                     #   sections, media, settings)
  cms_repo.py        # NEW -- DB access layer for CMS content tables,
                     #   mirroring files_repo.py's shape (one connection per
                     #   call, *_COLUMNS constants, serialize_*() helpers)

templates/
  visonadmin/         # NEW
    base.html         # CMS shell (its own sidebar/nav -- do not reuse
                       #   tcsadmin's base.html, the nav items differ entirely)
    login.html         # or share templates/login.html if visonadmin reuses
                       #   the same userTbl/session login (see decision below)
    dashboard.html      # landing page after login
    pages.html          # list + edit storefront pages/sections
    media.html          # media library (images used on the storefront)
    settings.html        # site-wide settings (SEO meta, contact info, etc.)

static/
  visonadmin/          # NEW -- keep CMS JS/CSS fully separate from the
                        #   scraper admin's static/*.js so neither can
                        #   accidentally break the other on a shared deploy
    dashboard.js, pages.js, media.js, settings.js
    visonadmin.css
```

## Route map for `/visonadmin`

Following the same shape already established for `/tcsadmin` in `app.py`:

```
GET/POST /visonadmin, /visonadmin/, /visonadmin/login   -> login page
POST     /visonadmin/logout
GET/POST /visonadmin/forgot-password, /visonadmin/reset-password
GET      /visonadmin/dashboard
GET      /visonadmin/pages                 (list)
GET/POST /visonadmin/pages/<id>            (edit / save)
GET      /visonadmin/media
POST     /visonadmin/media/upload
GET/POST /visonadmin/settings

/visonadmin/api/pages            (GET list, POST create)
/visonadmin/api/pages/<id>       (GET, PUT, DELETE)
/visonadmin/api/media            (GET list, POST upload)
/visonadmin/api/media/<id>       (DELETE)
/visonadmin/api/settings         (GET, PUT)
```

## Open decisions before implementation

1. **Auth model** — does `/visonadmin` share `userTbl`/session login with
   `/tcsadmin` (add a `CanAccessCMS` flag or a new role value), or does it
   get its own independent login entirely? Sharing is less code; separate
   auth is cleaner if CMS editors should never see scraper-admin data.
2. **New DB tables** — likely `cmsPageTbl` (slug, title, sections as JSON or
   normalized rows), `cmsMediaTbl` (uploaded asset metadata), `cmsSettingsTbl`
   (key/value site settings). Schema to be finalized once the storefront's
   actual editable fields are known.
3. **How `Client/Home.html` reads CMS content** — either the template
   queries the CMS tables directly at render time (simplest), or the CMS
   writes a generated static JSON/HTML fragment that `Client/Home.html`
   includes (faster, avoids a DB hit on every public page load).

This file is a planning document only — nothing under `/visonadmin` has been
built yet.
