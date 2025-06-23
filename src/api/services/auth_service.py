from werkzeug.security import generate_password_hash, check_password_hash
from src.database.models import User
from src.database.config import SessionLocal
from src.utils.jwt_helper import create_access_token
from src.api.services.user_service import UserService

class AuthService:
    def __init__(self):
        self.user_service = UserService()

    def login(self, username, password):
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

    def register_user(self, nama_lengkap, role, divisi):
        session = SessionLocal()
        
        try:
            # Validasi nama_lengkap jika sudah ada
            existing_user = session.query(User).filter(
                User.nama_lengkap == nama_lengkap
            ).first()
            
            if existing_user:
                session.close()
                return None, f"Nama {nama_lengkap} sudah ada. Silakan gunakan nama lain."

            # Validasi untuk role kasub - hanya boleh 1 per divisi
            if role == 'kasub' and divisi:
                existing_kasub = session.query(User).filter(
                    User.role == 'kasub',
                    User.divisi == divisi
                ).first()
                
                if existing_kasub:
                    session.close()
                    return None, f"Kepala Sub Bagian untuk divisi {self._get_divisi_name(divisi)} sudah ada. Hanya boleh ada 1 Kepala Sub Bagian per divisi."
            
            # Validasi untuk role sekertaris - hanya boleh 1 secara global
            if role == 'sekertaris':
                existing_sekertaris = session.query(User).filter(
                    User.role == 'sekertaris'
                ).first()
                
                if existing_sekertaris:
                    session.close()
                    return None, "Sekertaris sudah ada. Hanya boleh ada 1 Sekertaris dalam sistem."
            
            # Validasi divisi untuk role kasub dan staf
            if role in ['kasub', 'staf'] and not divisi:
                session.close()
                return None, f"Divisi harus dipilih untuk role {self._get_role_name(role)}"
            
            # Validasi divisi untuk role sekertaris
            if role == 'sekertaris' and divisi:
                session.close()
                return None, "Sekertaris tidak perlu memilih divisi"
            
            session.close()
            
            # Jika semua validasi berhasil, buat user
            user, error = self.user_service.create_user(nama_lengkap, role, divisi)
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
            
        except Exception as e:
            session.close()
            return None, f"Terjadi kesalahan saat mendaftarkan user: {str(e)}"

    def _get_divisi_name(self, divisi):
        """Helper method untuk mendapatkan nama divisi yang readable"""
        divisi_names = {
            'teknis_dan_hukum': 'Teknis dan Hukum',
            'data_dan_informasi': 'Data dan Informasi',
            'logistik_dan_keuangan': 'Logistik dan Keuangan',
            'sdm_dan_parmas': 'SDM dan Parmas'
        }
        return divisi_names.get(divisi, divisi)

    def _get_role_name(self, role):
        """Helper method untuk mendapatkan nama role yang readable"""
        role_names = {
            'sekertaris': 'Sekertaris',
            'kasub': 'Kepala Sub Bagian',
            'staf': 'Staf'
        }
        return role_names.get(role, role)

# Create a singleton instance
auth_service = AuthService()