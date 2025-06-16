from src.database.config import SessionLocal
from src.database.models import User
from werkzeug.security import generate_password_hash
import random
import string
from sqlalchemy import or_

class UserService:
    @staticmethod
    def generate_username(nama_lengkap, user_id):
        # Ambil nama pertama dan terakhir
        nama_parts = nama_lengkap.split()
        if len(nama_parts) >= 2:
            first_name = nama_parts[0].lower()
            last_name = nama_parts[-1].lower()
            return f"{first_name}{last_name}{user_id}"
        else:
            return f"{nama_lengkap.lower()}{user_id}"

    @staticmethod
    def generate_password(length=8):
        # Generate random password dengan kombinasi huruf dan angka
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def get_users(self, page=1, per_page=10, search=None, role=None, divisi=None):
        session = SessionLocal()
        try:
            # Base query
            query = session.query(User)

            # Apply filters if provided
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.nama_lengkap.ilike(search_term)
                    )
                )
            
            if role:
                query = query.filter(User.role == role)
            
            if divisi:
                query = query.filter(User.divisi == divisi)

            # Get total count before pagination
            total = query.count()

            # Apply pagination
            users = query.order_by(User.username.asc())\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()

            # Calculate pagination info
            total_pages = (total + per_page - 1) // per_page

            return {
                "users": users,
                "pagination": {
                    "total": total,
                    "per_page": per_page,
                    "current_page": page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
        finally:
            session.close()

    def get_user(self, user_id):
        session = SessionLocal()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user

    def create_user(self, nama_lengkap, role, divisi):
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
            new_username = self.generate_username(nama_lengkap, new_user.id)
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

    def update_user(self, user_id, data):
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

    def update_password(self, user_id, new_password):
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

    def delete_user(self, user_id):
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

# Create a singleton instance
user_service = UserService()