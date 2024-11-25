from flask_mail import Message
from app import mail
import os

def send_email(to, subject, template):
    sender = os.environ.get('EMAIL_USER')
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender= sender
    )
    mail.send(msg)

