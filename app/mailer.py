import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Gmail SMTP configuration -- hardcoded directly here (not read from .env)
# per explicit request, since this app's systemd unit only re-reads its
# EnvironmentFile on a full `systemctl restart` (not the SIGHUP-based
# graceful reload this account can trigger without sudo) -- a stale/typo'd
# env var can persist across reloads indefinitely otherwise. Keeping the
# real credential values only here means updating them just needs a code
# deploy + reload, not a full service restart.
GMAIL_USER = 'task.klever@gmail.com'
GMAIL_APP_PASSWORD = 'mschrzdtlqdxykoo'
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT_SSL = 465
SMTP_PORT_TLS = 587
MAIL_FROM = GMAIL_USER


def send_email(to_address, subject, html_body, text_body=None):
    """Sends an HTML email via Gmail SMTP with dual SSL 465 and TLS 587 support."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to_address

    if text_body:
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    errors = []

    # 1. Primary: Direct SSL on port 465
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT_SSL, timeout=20) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            return True
    except Exception as e:
        errors.append(f'SSL 465 failed: {e}')

    # 2. Fallback: STARTTLS on port 587
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT_TLS, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
            return True
    except Exception as e:
        errors.append(f'TLS 587 failed: {e}')

    raise RuntimeError(f"Failed to send email via Gmail SMTP: {'; '.join(errors)}")

#update 12:58 