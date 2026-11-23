from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

async def send_verification_email(recipient: str, token: str) -> None:
    message = EmailMessage()

    message['From'] = settings.smtp_from
    message['To'] = recipient
    message['Subject'] = 'Confire your email'

    message.set_content(
        f'Your verification token:\n\n{token}\n\n'
        f'This token expires in 20 minutes.'
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password.get_secret_value(),
        start_tls=True
    )

async def send_email_change_email(recipient: str, token: str) -> None:
    message = EmailMessage()

    message['From'] = settings.smtp_from
    message['To'] = recipient
    message['Subject'] = 'Confirm your new email'

    message.set_content(
        f'Hello!\n\n'
        f'You requested to change your email address.\n\n'
        f'{token}\n\n'
        f'This token expires in 20 minutes.\n'
        f'If you did not request this change, ignore this email.'
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password.get_secret_value(),
        start_tls=True
    )