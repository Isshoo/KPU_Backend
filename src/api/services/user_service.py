from src.database.config import SessionLocal
from src.database.models import User
from werkzeug.security import generate_password_hash
import random
import string

def generate_username(nama_lengkap, user_id):
    # Ambil nama pertama dan terakhir
    nama_parts = nama_lengkap.split()
    if len(nama_parts) >= 2:
        first_name = nama_parts[0].lower()
        last_name = nama_parts[-1].lower()
        return f"{first_name}{last_name}{user_id}"
    else:
        return f"{nama_lengkap.lower()}{user_id}"

def generate_password(length=8):
    # Generate random password dengan kombinasi huruf dan angka
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_users():
    session = SessionLocal()
    users = session.query(User).order_by(User.username.asc()).all()
    session.close()
    return users

def get_user(user_id):
    session = SessionLocal()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user

def create_user(nama_lengkap, role, divisi):
    session = SessionLocal()
    try:
        # Generate temporary username untuk mendapatkan ID
        temp_username = f"temp_{nama_lengkap.lower().replace(' ', '_')}"
        new_user = User(
            username=temp_username,
            password_hash=generate_password_hash(temp_username),
            nama_lengkap=nama_lengkap,
            role=role,
            divisi=divisi
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        # Update username dengan ID yang sudah ada
        new_username = generate_username(nama_lengkap, new_user.id)
        new_user.username = new_username
        new_user.password_hash = generate_password_hash(new_username)
        session.commit()
        session.refresh(new_user)
        
        return new_user, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def update_user(user_id, data):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found"

        if 'nama_lengkap' in data:
            user.nama_lengkap = data['nama_lengkap']

        if 'role' in data:
            user.role = data['role']

        if 'divisi' in data:
            user.divisi = data['divisi']

        session.commit()
        session.refresh(user)
        return user, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()

def update_password(user_id, new_password):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"

        user.password_hash = generate_password_hash(new_password)
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()

def delete_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"

        session.delete(user)
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()