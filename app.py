import os
import secrets
import subprocess
import sys
import threading
from datetime import datetime, timedelta

from flask import Flask, Response, jsonify, render_template, send_from_directory, session

from scraper_status_utils import build_status_summary, parse_status_line

app = Flask(__name__)
# A random fallback key here would change on every process restart (e.g. Render's
# free-tier spin-down/cold-start), invalidating every existing session cookie and
# making the app look like it "reset" on refresh. Set FLASK_SECRET_KEY in the
# hosting environment so sessions survive restarts.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-insecure-key-set-FLASK_SECRET_KEY-in-production')
app.permanent_session_lifetime = timedelta(days=7)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(BASE_DIR, 'pitstoparabiabycsv.py')


class ScraperSession:
    """Per-browser-session scraper state, so concurrent users don't see or control each other's runs."""

    def __init__(self):
        self.lock = threading.Lock()
        self.process = None
        self.thread = None
        self.url_statuses = []
        self.done = False
        self.stopped = False
        self.output_file = None


scraper_sessions = {}
scraper_sessions_lock = threading.Lock()


def get_session_id():
    if 'sid' not in session:
        session.permanent = True
        session['sid'] = secrets.token_hex(16)
    return session['sid']


def get_scraper_session():
    session_id = get_session_id()
    with scraper_sessions_lock:
        state = scraper_sessions.get(session_id)
        if state is None:
            state = ScraperSession()
            scraper_sessions[session_id] = state
    return state


# @app.route('/')
# def index():
#     return render_template("Dashboard.html", page="Dashboard")


@app.route('/') 
def Scrap():
    return render_template("Scrap.html", page="scraping")


def _read_scraper_output(state, process):
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            cleaned_line = line.rstrip('\n')
            with state.lock:
                parsed_status = parse_status_line(cleaned_line)
                if parsed_status:
                    existing = next((item for item in state.url_statuses if item['url'] == parsed_status['url']), None)
                    if existing:
                        existing['status'] = parsed_status['status']
                        if parsed_status.get('parent'):
                            existing['parent'] = parsed_status['parent']
                        if parsed_status.get('type'):
                            existing['type'] = parsed_status['type']
                    else:
                        state.url_statuses.append({
                            'url': parsed_status['url'],
                            'status': parsed_status['status'],
                            'parent': parsed_status.get('parent') or '',
                            'type': parsed_status.get('type') or 'root',
                        })
        process.stdout.close()
        process.wait()
    finally:
        with state.lock:
            state.done = not state.stopped


@app.route('/StartScraper', methods=['POST'])
def start_scraper():
    state = get_scraper_session()

    with state.lock:
        if state.process and state.process.poll() is None:
            return Response('Scraper is already running.', status=409, mimetype='text/plain')

        state.url_statuses.clear()
        state.done = False
        state.stopped = False

        timestamp = datetime.now().strftime('%d-%m-%Y_%H%M%S')
        output_file = os.path.join(BASE_DIR, f'pitstoparabia_data_{get_session_id()[:8]}_{timestamp}.xlsx')
        state.output_file = output_file

        process = subprocess.Popen(
            [sys.executable, '-u', SCRIPT_PATH, output_file],
            cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
        )

        state.process = process
        state.thread = threading.Thread(target=_read_scraper_output, args=(state, process), daemon=True)
        state.thread.start()

    return Response(
        f'Background scraper started with PID {process.pid}.',
        status=200,
        mimetype='text/plain'
    )


@app.route('/stop-scraper', methods=['POST'])
def stop_scraper():
    state = get_scraper_session()
    with state.lock:
        if not state.process or state.process.poll() is not None:
            return jsonify({'stopped': False, 'message': 'No scraper process is running.'})

        state.stopped = True
        try:
            state.process.terminate()
            state.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            state.process.kill()
            state.process.wait()
        finally:
            state.process = None

    return jsonify({'stopped': True, 'message': 'Scraper has been stopped.'})

@app.route('/scraper-url-statuses')
def scraper_url_statuses_endpoint():
    state = get_scraper_session()
    with state.lock:
        statuses = list(state.url_statuses)

    return jsonify({
        'statuses': statuses,
        'summary': build_status_summary(statuses),
    })


@app.route('/scraper-status')
def scraper_status():
    state = get_scraper_session()
    with state.lock:
        running = state.process is not None and state.process.poll() is None
        done = state.done and not running
        output_file = state.output_file

    output_available = bool(output_file and os.path.exists(output_file))

    return jsonify({
        'running': running,
        'done': done,
        'outputAvailable': output_available,
        'outputFile': os.path.basename(output_file) if output_available else '',
    })


@app.route('/download-output')
def download_output():
    state = get_scraper_session()
    with state.lock:
        output_file = state.output_file

    if not output_file or not os.path.exists(output_file):
        return Response('No output file found.', status=404, mimetype='text/plain')

    return send_from_directory(BASE_DIR, os.path.basename(output_file), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
