import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

def send_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title, body=body, image='resources/Match.png'),
        token=token,
        webpush=messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon='resources/Match.png'
            )
        )
    )
    response = messaging.send(message)
    print('Successfully sent notification message:', response)
    return response

