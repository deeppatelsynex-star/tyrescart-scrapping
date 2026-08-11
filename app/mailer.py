import os
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER')
# Google displays app passwords as 4 space-separated groups for readability, but
# the real credential has no spaces -- strip them so a direct copy/paste from
# Google's UI doesn't silently break auth.
SMTP_PASSWORD = (os.environ.get('SMTP_PASSWORD') or '').replace(' ', '') or None
SMTP_FROM = os.environ.get('SMTP_FROM', SMTP_USER)
SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').strip().lower() != 'false'


def send_email(to_address, subject, html_body):
    if not SMTP_HOST or not SMTP_FROM:
        raise RuntimeError('SMTP is not configured (set SMTP_HOST and SMTP_FROM/SMTP_USER in the environment).')

    message = MIMEText(html_body, 'html')
    message['Subject'] = subject
    message['From'] = SMTP_FROM
    message['To'] = to_address

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [to_address], message.as_string())
