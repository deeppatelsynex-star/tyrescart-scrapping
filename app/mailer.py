import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Automatically load .env from project root or current working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv()


def _clean_str(val):
    if not val:
        return ''
    return str(val).strip().strip("'\"").strip()


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP with automatic credentials sanitization and dual-mode SSL/TLS."""
    raw_user = os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER') or os.environ.get('MAIL_USERNAME') or ''
    raw_pass = os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD') or os.environ.get('MAIL_PASSWORD') or ''
    raw_sender = os.environ.get('MAIL_FROM') or raw_user
    raw_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    raw_port = os.environ.get('SMTP_PORT', '465')

    username = _clean_str(raw_user)
    password = _clean_str(raw_pass).replace(' ', '')
    sender = _clean_str(raw_sender) or username
    host = _clean_str(raw_host) or 'smtp.gmail.com'

    try:
        port = int(_clean_str(raw_port) or 465)
    except (ValueError, TypeError):
        port = 465

    if not username or not password:
        raise RuntimeError(
            'Gmail SMTP credentials are not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file.'
        )

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_address

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    errors = []

    # Priority 1: SMTP_SSL on port 465 (Most reliable on cloud VPS)
    try:
        with smtplib.SMTP_SSL(host, 465, timeout=20) as server:
            server.login(username, password)
            server.send_message(msg)
            return True
    except Exception as e:
        errors.append(f'SSL 465: {e}')

    # Priority 2: SMTP with STARTTLS on port 587
    try:
        with smtplib.SMTP(host, 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.send_message(msg)
            return True
    except Exception as e:
        errors.append(f'STARTTLS 587: {e}')

    raise RuntimeError(f"Failed to send email via Gmail SMTP ({'; '.join(errors)})")