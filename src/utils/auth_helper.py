from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta

def verify_password(stored_password_hash, provided_password):
    """
    Verifikasi password yang diberikan dengan hash yang tersimpan.
    """
    return check_password_hash(stored_password_hash, provided_password)

def generate_token(identity, expires_delta=timedelta(days=1)):
    """
    Generate JWT token baru untuk user.
    """
    return create_access_token(identity=identity, expires_delta=expires_delta)
