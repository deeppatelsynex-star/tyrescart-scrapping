import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Automatically load .env from project root or current working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
load_dotenv()

# Verified Gmail Credentials
GMAIL_USER = 'task.klever@gmail.com'
GMAIL_APP_PASSWORD = 'mschrzdtlqdxykoo'


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP (Port 465 SSL primary, Port 587 STARTTLS fallback)."""
    username = GMAIL_USER
    password = GMAIL_APP_PASSWORD
    sender = username
    host = 'smtp.gmail.com'

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