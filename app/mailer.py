import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Automatically load .env from project root or current working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv()

# Gmail SMTP Configuration from environment (.env)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
SMTP_USER = os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER') or os.environ.get('MAIL_USERNAME')
SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD') or os.environ.get('MAIL_PASSWORD')
MAIL_FROM = os.environ.get('MAIL_FROM') or SMTP_USER


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP (supports both SSL 465 and STARTTLS 587 with auto-fallback)."""
    username = SMTP_USER or os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER')
    password = SMTP_PASSWORD or os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD')
    host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    port = int(os.environ.get('SMTP_PORT', 465))

    if not username or not password:
        raise RuntimeError(
            'Gmail SMTP credentials are not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file.'
        )

    # Clean app password if pasted with spaces or quotes
    password = password.strip().replace(' ', '').replace('"', '').replace("'", "")
    sender = (MAIL_FROM or username).strip().replace('"', '').replace("'", "")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_address

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    errors = []

    # Priority 1: If port 465 or default, connect via SMTP_SSL
    if port == 465:
        try:
            with smtplib.SMTP_SSL(host, 465, timeout=20) as server:
                server.login(username, password)
                server.send_message(msg)
                return True
        except Exception as e:
            errors.append(f'SSL 465 failed: {e}')

    # Priority 2: Connect via SMTP with STARTTLS (Port 587)
    try:
        with smtplib.SMTP(host, 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.send_message(msg)
            return True
    except Exception as e:
        errors.append(f'STARTTLS 587 failed: {e}')

    # Fallback Priority 3: If port 587 was tried first and failed, try SSL 465
    if port != 465:
        try:
            with smtplib.SMTP_SSL(host, 465, timeout=20) as server:
                server.login(username, password)
                server.send_message(msg)
                return True
        except Exception as e:
            errors.append(f'SSL 465 fallback failed: {e}')

    raise RuntimeError(f"Failed to send email via Gmail SMTP: {'; '.join(errors)}")