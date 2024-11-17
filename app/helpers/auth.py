from flask_jwt_extended import create_access_token, create_refresh_token
import jwt
from config import Config
from datetime import datetime, timezone

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
    
