# seed_admin.py

from src.database.config import SessionLocal
from src.database.models import User
from werkzeug.security import generate_password_hash


def seed_admin():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(
            User.username == 'admin').first()
        if existing_admin:
            print("Admin user already exists.")
        else:
            admin_user = User(
                username='juanderry',
                password_hash=generate_password_hash(
                    'junkerz', method='pbkdf2:sha256'),
                nama_lengkap='Juan Derry',
                role='sekertaris',
                divisi=None
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
