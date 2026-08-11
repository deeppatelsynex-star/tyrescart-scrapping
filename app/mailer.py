import os

import resend

resend.api_key = os.environ.get('RESEND_API_KEY')
MAIL_FROM = os.environ.get('MAIL_FROM')


def send_email(to_address, subject, html_body):
    if not resend.api_key or not MAIL_FROM:
        raise RuntimeError('Resend is not configured (set RESEND_API_KEY and MAIL_FROM in the environment).')

    resend.Emails.send({
        'from': MAIL_FROM,
        'to': [to_address],
        'subject': subject,
        'html': html_body,
    })
