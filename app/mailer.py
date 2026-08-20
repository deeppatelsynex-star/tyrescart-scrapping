import os
import re
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
    first_line = str(val).split('\n')[0].split('\r')[0]
    return first_line.strip().strip("'\"").strip()


def _clean_pass(val):
    if not val:
        return ''
    first_line = str(val).split('\n')[0].split('\r')[0]
    return first_line.strip().strip("'\"").replace(' ', '').strip()


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP with bulletproof credentials sanitization and dual-mode SSL/TLS."""
    raw_user = (
        os.environ.get('GMAIL_USER')
        or os.environ.get('SMTP_USER')
        or os.environ.get('MAIL_USERNAME')
        or os.environ.get('MAIL_FROM')
        or 'task.klever@gmail.com'
    )
    raw_pass = (
        os.environ.get('GMAIL_APP_PASSWORD')
        or os.environ.get('SMTP_PASSWORD')
        or os.environ.get('MAIL_PASSWORD')
        or 'mschrzdtlqdxykoo'
    )
    raw_sender = os.environ.get('MAIL_FROM') or raw_user
    raw_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    raw_port = os.environ.get('SMTP_PORT', '465')

    username = _clean_str(raw_user) or 'task.klever@gmail.com'
    password = _clean_pass(raw_pass) or 'mschrzdtlqdxykoo'
    sender = _clean_str(raw_sender) or username
    host = _clean_str(raw_host) or 'smtp.gmail.com'

    try:
        port = int(_clean_str(raw_port) or 465)
    except (ValueError, TypeError):
        port = 465

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_address

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    errors = []

    # Priority 1: SMTP_SSL on port 465 (Direct SSL connection)
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