from flask_jwt_extended import create_access_token, create_refresh_token
import jwt
from config import Config
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer

def create_tokens(user_id):
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return access_token, refresh_token

def new_access_token(user_id):
    access_token = create_access_token(identity=user_id)
    return access_token

def decode_token(token):
    try:
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def verify_expiry(token):
    data = decode_token(token)
    if not data:
        return False
    expiry_time = datetime.fromtimestamp(data['exp'], tz=timezone.utc)
    print(expiry_time)
    current_time = datetime.now(timezone.utc)
    if expiry_time > current_time:
        return False
    return True

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SALT)

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=Config.SALT,
            max_age=expiration
        )
        return email
    except:
        return False
    
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SALT)

def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=Config.SALT,
            max_age=300
        )
        return email
    except:
        return False
    
    
