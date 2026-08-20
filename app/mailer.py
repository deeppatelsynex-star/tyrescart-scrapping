import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Gmail SMTP Configuration from environment (.env)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER') or os.environ.get('MAIL_USERNAME')
SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD') or os.environ.get('MAIL_PASSWORD')
MAIL_FROM = os.environ.get('MAIL_FROM') or SMTP_USER


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP using STARTTLS."""
    username = SMTP_USER or os.environ.get('GMAIL_USER') or os.environ.get('SMTP_USER')
    password = SMTP_PASSWORD or os.environ.get('GMAIL_APP_PASSWORD') or os.environ.get('SMTP_PASSWORD')

    if not username or not password:
        raise RuntimeError(
            'Gmail SMTP credentials are not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file.'
        )

    # Clean app password if user pasted with spaces
    password = password.strip().replace(' ', '')
    sender = MAIL_FROM or username

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_address

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=25) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(username, password)
            server.send_message(msg)
            return True
    except Exception as e:
        raise RuntimeError(f'Failed to send email via Gmail SMTP: {e}') from e
