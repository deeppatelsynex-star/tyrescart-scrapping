# TyresCart Scraping Dashboard

A Flask web dashboard for scraping tyre product data from [pitstoparabia.com](https://www.pitstoparabia.com).
Authenticated users start scraping jobs from the browser — by uploading a CSV/JSON
file or pasting URLs directly — watch live per-URL progress, and download the
resulting `.xlsx` report. The backend automatically detects which of three Scrapy
spiders should handle each URL; the browser never chooses the scraper itself.

This is a small internal tool: no build step, no test runner/linter, no frontend
framework — server-rendered Jinja templates + vanilla JS.

## Features

- **Login / session auth** with bcrypt password hashing, per-email rate limiting,
  and "Remember me" (persistent vs. browser-session cookies).
- **Forgot / reset password** via emailed single-use links (sent through SMTP).
- **User Management & Trash** — role-based (`SuperAdmin` / `Admin` / `User`),
  soft-delete only (no permanent delete), searchable/sortable DataTables.
- **Flexible scraper input** — start a job by:
  - Uploading a `.csv` (a `url` column, or `type,url`)
  - Uploading a `.json` file, or pasting raw JSON (array of URLs, `{"urls": [...]}`,
    or an array of `{"url": "..."}` objects)
  - Pasting one or more URLs directly (newline-separated, quotes/commas tolerated)
- **Automatic scraper routing** — every URL is classified (`brand` / `sitemap` /
  `listing`/`product` / `unknown`) before anything runs; a "Detected URLs" preview
  table shows exactly which scraper will handle each URL, and unsupported/invalid
  URLs are rejected with a clear reason instead of being guessed at.
- **Live progress tree** — per-URL pending/running/done/blocked status, polled
  from the backend while a job runs; safe to refresh mid-job.
- **One-click `.xlsx` download** of the merged results once a job finishes.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Flask, PyMySQL, bcrypt, python-dotenv |
| Scraping | Scrapy, scrapy-xlsx, openpyxl |
| Email | Native Python `smtplib` (SMTP SSL/TLS) |
| Database | MySQL (Railway-hosted by default; local MySQL as an optional fallback) |
| Frontend | Server-rendered Jinja templates, Alpine.js, vanilla JS, Tailwind (via CDN), DataTables |

## Prerequisites

- Python 3.10+ (a `venv/` is expected at the project root — see below)
- A MySQL server/database (Railway or local)

## Setup

```bash
git clone https://github.com/deeppatelsynex-star/tyrescart-scrapping.git
cd tyrescart-scrapping

python -m venv venv
venv\Scripts\pip install -r requirements.txt        # Windows
# source venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

venv\Scripts\python -m playwright install chromium  # one-time browser download, needed by scan.py

copy .env.example .env      # Windows -- or `cp .env.example .env`
# then edit .env with real DB credentials
```

### Environment variables (`.env`)

| Variable | Required | Purpose |
|---|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Yes | MySQL connection (Railway by default; a commented-out local-MySQL block is included as a fallback) |
| `FLASK_SECRET_KEY` | Recommended outside dev | Session signing key — set this in any environment that restarts the process, or sessions won't survive a restart |

### Database

```bash
venv\Scripts\python.exe app\init_db.py       # creates/upgrades userTbl (safe to re-run)
venv\Scripts\python.exe app\create_user.py   # interactive prompt to add a login user (first one should be a SuperAdmin)
```

## Running it

```bash
venv\Scripts\python.exe app\app.py
```

Dev server runs at `http://0.0.0.0:5000` with `debug=True`. Log in with the user
created above.

## Using the scraper

1. Go to `/` and pick a tab under **Scraper Input**: Upload CSV, Upload JSON, or
   Enter URL.
2. Provide your URLs (drag-and-drop a file, choose a file, or paste text/JSON) and
   analyze — a preview table shows each URL's detected type and which scraper will
   run it. Rows with invalid or unsupported URLs are reported but don't block the
   rest of the batch.
3. Click **Start Scraping**. If the batch spans multiple URL types (e.g. brand +
   listing URLs together), each type's scraper runs in turn and all progress
   shows up in the same live tree.
4. Once finished, click **Download** for the merged `.xlsx` report.

## Project structure

```
app/            Flask app, auth, DB access, mailer, scraper-input normalizer
scrapers/       Standalone Scrapy spider scripts + scraper_config.py (URL routing)
templates/      Jinja templates (dashboard, login, admin, trash, emails)
static/         Vanilla JS + CSS for the dashboard and admin pages
tmp/scrapers/   Per-job temp input/output files (auto-created, auto-cleaned up)
```

See [`CLAUDE.md`](CLAUDE.md) for a detailed architecture writeup (per-session job
state, the `URL_STATUS` stdout protocol between spiders and Flask, RBAC rules,
etc.), and [`TESTCASES.md`](TESTCASES.md) / [`TEST_FLOW.md`](TEST_FLOW.md) for the
manual test suite.

## Notes

- There is no test runner or linter configured — testing is manual, per
  `TESTCASES.md`/`TEST_FLOW.md`.
- Scraper output files (`pitstoparabia_data_<jobid>_<timestamp>.xlsx`) are written
  to the project root and are **not** cleaned up automatically — remove old ones
  periodically.
- `.env` (real credentials) is gitignored; only `.env.example` (placeholders) is
  committed.
