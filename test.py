from firebase_admin import credentials, firestore, initialize_app
import os
import dotenv
import json

dotenv.load_dotenv()

credentials = credentials.Certificate(json.loads(os.environ.get('FIREBASE_KEY')))

