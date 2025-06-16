from werkzeug.security import generate_password_hash, check_password_hash
from src.database.models import User
from src.database.config import SessionLocal
from src.utils.jwt_helper import create_access_token
from src.api.services.user_service import generate_password

def login(username, password):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    if not user:
        session.close()
        return None, "User not found"

    if not check_password_hash(user.password_hash, password):
        session.close()
        return None, "Incorrect password"

    token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "divisi": user.divisi
    })
    session.close()
    return token, None

def register_user(nama_lengkap, role, divisi):
    from src.api.services.user_service import create_user
    

    user, error = create_user(nama_lengkap, role, divisi)
    if error:
        return None, error
    
    return {
        "id": user.id,
        "username": user.username,
        "password": user.username,  # Password sementara yang akan ditampilkan ke admin
        "nama_lengkap": user.nama_lengkap,
        "role": user.role,
        "divisi": user.divisi
    }, None