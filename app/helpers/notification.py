import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import os
import json
import tempfile
# Obtener la ruta del archivo de credenciales
# Inicializar la app de Firebase
#json_object = json.dumps(dictado, indent = 4)
cred = credentials.Certificate(json.loads(os.environ.get('FIREBASE_KEY')))
firebase_admin.initialize_app(cred)
def send_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title, body=body, image=None),
        token=token        
    )
    response = messaging.send(message)
    print('Successfully sent notification message:', response)
    return response

