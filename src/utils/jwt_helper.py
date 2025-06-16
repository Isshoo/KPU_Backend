import jwt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps
from src.database.config import JWT_SECRET_KEY, JWT_ALGORITHM
from src.database.models import User, RoleEnum
from src.database.config import SessionLocal

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        db = None
        try:
            if 'Authorization' in request.headers:
                bearer = request.headers['Authorization']
                token = bearer.split()[1] if bearer.startswith('Bearer ') else bearer

            if not token:
                return jsonify({"message": "Missing token"}), 401

            data = decode_access_token(token)
            if not data:
                return jsonify({"message": "Invalid or expired token"}), 401

            db = SessionLocal()
            user = db.query(User).filter(User.id == data["user_id"]).first()

            if not user:
                return jsonify({"message": "User not found"}), 404

            request.current_user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500
            
        finally:
            if db:
                db.close()
                
    return decorated

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if user.role != RoleEnum.sekertaris:
            return jsonify({"message": "Admin privilege required"}), 403
        return f(*args, **kwargs)
    return decorated