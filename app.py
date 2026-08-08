import glob
import os
import subprocess
import sys
import threading

from flask import Flask, Response, jsonify, render_template, send_from_directory

from scraper_status_utils import build_status_summary, parse_status_line

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(BASE_DIR, 'pitstoparabiabycsv.py')

scraper_process = None
scraper_thread = None
scraper_url_statuses = []
scraper_done = False
scraper_stopped = False
scraper_lock = threading.Lock()


# @app.route('/')
# def index():
#     return render_template("Dashboard.html", page="Dashboard")


@app.route('/') 
def Scrap():
    return render_template("Scrap.html", page="scraping")


def _read_scraper_output(process):
    global scraper_done, scraper_stopped
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            cleaned_line = line.rstrip('\n')
            with scraper_lock:
                parsed_status = parse_status_line(cleaned_line)
                if parsed_status:
                    existing = next((item for item in scraper_url_statuses if item['url'] == parsed_status['url']), None)
                    if existing:
                        existing['status'] = parsed_status['status']
                        if parsed_status.get('parent'):
                            existing['parent'] = parsed_status['parent']
                        if parsed_status.get('type'):
                            existing['type'] = parsed_status['type']
                    else:
                        scraper_url_statuses.append({
                            'url': parsed_status['url'],
                            'status': parsed_status['status'],
                            'parent': parsed_status.get('parent') or '',
                            'type': parsed_status.get('type') or 'root',
                        })
        process.stdout.close()
        process.wait()
    finally:
        with scraper_lock:
            scraper_done = not scraper_stopped


@app.route('/StartScraper', methods=['POST'])
def start_scraper():
    global scraper_process, scraper_thread, scraper_done, scraper_stopped

    with scraper_lock:
        if scraper_process and scraper_process.poll() is None:
            return Response('Scraper is already running.', status=409, mimetype='text/plain')

        scraper_url_statuses.clear()
        scraper_done = False
        scraper_stopped = False

        process = subprocess.Popen(
            [sys.executable, '-u', SCRIPT_PATH],
            cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
        )

        scraper_process = process
        scraper_thread = threading.Thread(target=_read_scraper_output, args=(process,), daemon=True)
        scraper_thread.start()

    return Response(
        f'Background scraper started with PID {process.pid}.',
        status=200,
        mimetype='text/plain'
    )


@app.route('/stop-scraper', methods=['POST'])
def stop_scraper():
    global scraper_process, scraper_stopped
    with scraper_lock:
        if not scraper_process or scraper_process.poll() is not None:
            return jsonify({'stopped': False, 'message': 'No scraper process is running.'})

        scraper_stopped = True
        try:
            scraper_process.terminate()
            scraper_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            scraper_process.kill()
            scraper_process.wait()
        finally:
            scraper_process = None

    return jsonify({'stopped': True, 'message': 'Scraper has been stopped.'})

@app.route('/scraper-url-statuses')
def scraper_url_statuses_endpoint():
    with scraper_lock:
        statuses = list(scraper_url_statuses)

    return jsonify({
        'statuses': statuses,
        'summary': build_status_summary(statuses),
    })


@app.route('/scraper-status')
def scraper_status():
    with scraper_lock:
        running = scraper_process is not None and scraper_process.poll() is None
        done = scraper_done and not running

    files = glob.glob(os.path.join(BASE_DIR, 'pitstoparabia_data_*.xlsx'))
    latest_file = max(files, key=os.path.getmtime) if files else None

    return jsonify({
        'running': running,
        'done': done,
        'outputAvailable': bool(latest_file),
        'outputFile': os.path.basename(latest_file) if latest_file else '',
    })


@app.route('/download-output')
def download_output():
    files = glob.glob(os.path.join(BASE_DIR, 'pitstoparabia_data_*.xlsx'))
    if not files:
        return Response('No output file found.', status=404, mimetype='text/plain')

    latest_file = max(files, key=os.path.getmtime)
    return send_from_directory(BASE_DIR, os.path.basename(latest_file), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
