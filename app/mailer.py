import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Automatically load .env from project root or current working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv()

# Verified default credentials
DEFAULT_GMAIL_USER = 'task.klever@gmail.com'
DEFAULT_GMAIL_APP_PASSWORD = 'mschrzdtlqdxykoo'


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
    """Sends an HTML email via Gmail SMTP (Port 465 SSL primary, Port 587 STARTTLS fallback)."""
    env_user = _clean_str(os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER') or os.environ.get('MAIL_USERNAME'))
    env_pass = _clean_pass(os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD') or os.environ.get('MAIL_PASSWORD'))

    # If env variable has old placeholder or invalid value, use verified defaults
    username = env_user if (env_user and '@' in env_user and not env_user.startswith('onboarding@')) else DEFAULT_GMAIL_USER
    password = env_pass if (env_pass and len(env_pass) >= 16) else DEFAULT_GMAIL_APP_PASSWORD

    raw_sender = _clean_str(os.environ.get('MAIL_FROM'))
    sender = raw_sender if (raw_sender and '@' in raw_sender and not raw_sender.startswith('onboarding@')) else username
    host = _clean_str(os.environ.get('SMTP_HOST')) or 'smtp.gmail.com'

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

    raise RuntimeError(f"Failed to send email via Gmail SMTP [user: {username}] ({'; '.join(errors)})")